import { MAX_ZIP_FILES, triggerBlobDownload } from "../utils/fileUtils";

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8001`;
const ENDPOINT_URL = `${API_BASE_URL}/api/v1/fiscal/export-reports`;

const FILE_FIELD_KEYS = ["zip_file", "zip_file_2", "zip_file_3"] as const;

export async function generateFiscalReports(files: File[]): Promise<string> {
  if (files.length === 0) {
    throw new Error("Selecione pelo menos 1 arquivo .zip para continuar.");
  }

  if (files.length > MAX_ZIP_FILES) {
    throw new Error(`Você pode enviar no máximo ${MAX_ZIP_FILES} arquivos .zip.`);
  }

  const formData = new FormData();
  files.forEach((file, index) => {
    const fieldName = FILE_FIELD_KEYS[index];
    if (fieldName) {
      formData.append(fieldName, file);
    }
  });

  const response = await fetch(ENDPOINT_URL, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `Erro ${response.status}: ${response.statusText}`
    );
  }

  const disposition = response.headers.get("Content-Disposition");
  let filename = "relatorios_fiscais.zip";
  if (disposition) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match?.[1]) {
      filename = match[1];
    }
  }

  const blob = await response.blob();
  triggerBlobDownload(blob, filename);

  return filename;
}
