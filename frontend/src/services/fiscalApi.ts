const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function generateFiscalReports(files: File[]): Promise<string> {
  if (files.length === 0) {
    throw new Error("Selecione pelo menos 1 arquivo .zip para continuar.");
  }

  if (files.length > 3) {
    throw new Error("Você pode enviar no máximo 3 arquivos .zip.");
  }

  const formData = new FormData();
  formData.append("zip_file", files[0]);

  if (files[1]) {
    formData.append("zip_file_2", files[1]);
  }

  if (files[2]) {
    formData.append("zip_file_3", files[2]);
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/fiscal/export-reports`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `Erro ao gerar relatórios (Status ${response.status}).`
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
  const downloadUrl = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();

  link.remove();
  window.URL.revokeObjectURL(downloadUrl);

  return filename;
}