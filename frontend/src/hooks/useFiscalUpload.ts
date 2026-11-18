import { useState } from "react";
import { generateFiscalReports } from "../services/fiscalApi";
import { isZipFile, MAX_ZIP_FILES } from "../utils/fileUtils";

export function useFiscalUpload() {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const clearFeedback = () => {
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const addFiles = (incomingFiles: FileList | null) => {
    if (!incomingFiles) return;
    clearFeedback();

    const selected = Array.from(incomingFiles);
    const validZips = selected.filter(isZipFile);

    if (validZips.length !== selected.length) {
      setErrorMsg("Apenas arquivos no formato .zip são permitidos.");
    }

    setFiles((prev) => {
      const combined = [...prev];

      for (const zip of validZips) {
        const alreadyExists = combined.some(
          (item) => item.name === zip.name && item.size === zip.size
        );
        if (!alreadyExists && combined.length < MAX_ZIP_FILES) {
          combined.push(zip);
        }
      }

      if (prev.length + validZips.length > MAX_ZIP_FILES) {
        setErrorMsg(`Limite máximo de ${MAX_ZIP_FILES} arquivos .zip atingido.`);
      }

      return combined;
    });
  };

  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
    clearFeedback();
  };

  const submitReports = async () => {
    if (files.length === 0 || isLoading) return;

    setIsLoading(true);
    clearFeedback();

    try {
      const downloadedFilename = await generateFiscalReports(files);
      setSuccessMsg(`Relatórios gerados com sucesso: ${downloadedFilename}`);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Falha inesperada ao processar.";
      setErrorMsg(message);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    files,
    isLoading,
    errorMsg,
    successMsg,
    remainingSlots: MAX_ZIP_FILES - files.length,
    isFull: files.length >= MAX_ZIP_FILES,
    addFiles,
    removeFile,
    submitReports,
  };
}
