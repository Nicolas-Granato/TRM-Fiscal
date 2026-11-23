# TRM Fiscal

Sistema web desenvolvido para automatizar a geração de relatórios fiscais em PDF a partir de lotes de XMLs (NF-e e NFC-e) disponibilizados pelo GFISCAL, eliminando gargalos operacionais da equipe de suporte da **TRM Sistemas**.

---

## Funcionalidades Principais

* **Ingestão Recursiva em Lote:** Upload de 1 a 3 arquivos `.zip` por requisição, com suporte a pacotes `.zip` aninhados.
* **Parsing Resiliente de XML:** Extração automática de metadados (CNPJ/CPF do emitente via estrutura de pastas ou tag `<emit>`, chave de acesso `chNF`, CFOP, datas e valores tributários), aplicando valores padrão (`0`) em tags opcionais ausentes para suportar notas isentas e NFC-e sem descartá-las.
* **Processamento Analítico Isolado:** Persistência temporária *in-memory* via `TEMP TABLES` no DuckDB por sessão, garantindo isolamento para uso multiusuário simultâneo.
* **Deduplicação e Tolerância a Falhas:** Remoção automática de chaves de acesso duplicadas (`chNF`) e descarte seguro de XMLs corrompidos sem interromper o processamento do restante do lote.
* **Detecção de Cancelamentos:** Identificação automática de notas canceladas por eventos (`110111`, `110112`, `canc`) ou status no XML (`<cStat>` `101`, `135`, `151`).
* **Consolidação em PDF:** Geração e empacotamento em um único `.zip` para download contendo os relatórios de **Resumo**, **Compras**, **CFOP/Modelo** e **Notas Canceladas**.

---

## Arquitetura e Stack Tecnológica

O projeto segue uma arquitetura desacoplada entre interface web e API monolítica de processamento em memória:

* **Back-end (`backend/`):**
  * **Python + FastAPI:** Exposição da API REST (`POST /api/fiscal/export-reports`).
  * **DuckDB:** Motor analítico *in-memory* com isolamento de sessão via tabelas temporárias.
  * **Pydantic:** Validação estrita de schemas de entrada, documentos XML e contratos de erro (`HTTP 400/422`).
  * **Jinja2 + WeasyPrint:** Renderização de templates HTML para documentos PDF.
* **Front-end (`frontend/`):**
  * **React + TypeScript + Vite:** Interface para upload drag-and-drop de pacotes `.zip`, feedback de status e download dos relatórios.
* **Infraestrutura e CI/CD:**
  * **Docker & Docker Compose:** Conteinerização dos serviços de front-end e back-end.
  * **GitHub Actions:** Pipeline automatizado de testes no repositório.

---

## Estrutura do Repositório

```text
TRM-Fiscal/
├── .github/workflows/       # Pipelines de CI/CD
├── backend/
│   └── src/
│       ├── controllers/     # Rotas da API (fiscal_controller.py)
│       ├── extractors/      # Leitura recursiva de ZIPs e parsing XML (xml_parser.py, fiscal_pipeline.py)
│       ├── schemas/         # Contratos Pydantic (xml_schema.py, export_schema.py, api_schema.py)
│       └── services/export/ # Orquestração e geradores de PDF (report_exporter.py e templates)
├── frontend/
│   └── src/                 # Componentes React (ZipDropzone, StatusAlert, etc.) e hooks (useFiscalUpload)
└── docker-compose.yml       # Orquestração dos contêineres
