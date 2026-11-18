from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from backend.src.database.session_manager.session_manager import DuckDBSession
from backend.src.schemas.api_schema import ErrorResponseSchema, HealthResponseSchema
from backend.src.schemas.export_schema import ReportFiltersSchema
from backend.src.services.export.exporter import ReportExporter
from backend.src.services.pipelines.fiscal_pipeline import FiscalPipeline

router = APIRouter(prefix="/fiscal", tags=["Fiscal"])


def _validate_zip_file(upload: Optional[UploadFile]) -> None:
    if upload and upload.filename and not upload.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O arquivo '{upload.filename}' é inválido. Envie apenas arquivos .zip.",
        )


@router.get(
    "/health",
    response_model=HealthResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verifica disponibilidade da API",
)
async def health_check() -> HealthResponseSchema:
    return HealthResponseSchema(status="ok", database="duckdb-in-memory")


@router.post(
    "/export-reports",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Processa XMLs (.zip) e gera relatórios fiscais em PDF (.zip)",
    responses={
        200: {
            "content": {"application/zip": {}},
            "description": "Arquivo .zip contendo os PDFs gerados.",
        },
        400: {
            "model": ErrorResponseSchema,
            "description": "Arquivo inválido, vazio ou CNPJ/CPF da empresa não identificado.",
        },
        422: {
            "model": ErrorResponseSchema,
            "description": "Erro de validação dos dados fiscais extraídos.",
        },
        500: {
            "model": ErrorResponseSchema,
            "description": "Erro interno ao processar banco DuckDB ou gerar PDFs.",
        },
    },
)
async def export_fiscal_reports(
    zip_file: UploadFile = File(..., description="Arquivo .zip principal contendo XMLs."),
    zip_file_2: Optional[UploadFile] = File(default=None, description="Segundo arquivo .zip (opcional)."),
    zip_file_3: Optional[UploadFile] = File(default=None, description="Terceiro arquivo .zip (opcional)."),
) -> Response:
    _validate_zip_file(zip_file)
    _validate_zip_file(zip_file_2)
    _validate_zip_file(zip_file_3)

    bytes_1 = await zip_file.read()
    if not bytes_1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo .zip principal está vazio.",
        )

    bytes_2 = await zip_file_2.read() if zip_file_2 else None
    bytes_3 = await zip_file_3.read() if zip_file_3 else None

    pipeline = FiscalPipeline(
        zip_file=bytes_1,
        zip_file_2=bytes_2,
        zip_file_3=bytes_3,
    )

    try:
        with DuckDBSession() as session:
            pipeline.run_pipeline(session.executemany_sql)

            if not pipeline.company_cnpj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível identificar o CNPJ/CPF da empresa nos XMLs enviados.",
                )

            filters = ReportFiltersSchema(
                company_cnpj=pipeline.company_cnpj,
                cliente_nome=pipeline.company_name or "Não informado",
            )

            exporter = ReportExporter(session)
            zip_bytes, zip_filename = exporter.export_zip_bytes(
                company_cnpj=filters.company_cnpj,
                cliente_nome=filters.cliente_nome,
            )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{zip_filename}"',
        },
    )