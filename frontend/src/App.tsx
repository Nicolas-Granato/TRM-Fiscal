import React, { useRef, useState } from "react";
import { generateFiscalReports } from "./services/fiscalApi";
import "./App.css";

const MAX_FILES = 3;

export function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const addFiles = (incomingFiles: FileList | null) => {
    if (!incomingFiles) return;
    setErrorMsg(null);
    setSuccessMsg(null);

    const selected = Array.from(incomingFiles);
    const validZips = selected.filter((f) =>
      f.name.toLowerCase().endsWith(".zip")
    );

    if (validZips.length !== selected.length) {
      setErrorMsg("Apenas arquivos no formato .zip são permitidos.");
    }

    setFiles((prev) => {
      // Evita duplicados pelo nome + tamanho e respeita o teto de 3 arquivos
      const combined = [...prev];
      for (const zip of validZips) {
        const alreadyExists = combined.some(
          (item) => item.name === zip.name && item.size === zip.size
        );
        if (!alreadyExists && combined.length < MAX_FILES) {
          combined.push(zip);
        }
      }

      if (prev.length + validZips.length > MAX_FILES) {
        setErrorMsg(`Limite máximo de ${MAX_FILES} arquivos .zip atingido.`);
      }

      return combined;
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (files.length < MAX_FILES) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (files.length < MAX_FILES) {
      addFiles(e.dataTransfer.files);
    }
  };

  const handleGenerateReports = async () => {
    if (files.length === 0 || isLoading) return;

    setIsLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

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

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <main className="page-wrapper">
      <section className="card">
        <header className="card-header">
          <h1>TRM Fiscal</h1>
          <p>Envie até 3 lotes (.zip) com XMLs fiscais para gerar os relatórios em PDF.</p>
        </header>

        {/* Container de Upload */}
        <div
          className={`dropzone ${isDragging ? "dragging" : ""} ${
            files.length >= MAX_FILES ? "disabled" : ""
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => {
            if (files.length < MAX_FILES && !isLoading) {
              fileInputRef.current?.click();
            }
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip,application/zip"
            multiple
            hidden
            onChange={(e) => addFiles(e.target.files)}
            disabled={files.length >= MAX_FILES || isLoading}
          />

          <div className="dropzone-content">
            <span className="dropzone-icon">📦</span>
            {files.length < MAX_FILES ? (
              <>
                <strong>Clique para selecionar ou arraste seus arquivos .zip aqui</strong>
                <span className="dropzone-hint">
                  Slots disponíveis: {MAX_FILES - files.length} de {MAX_FILES}
                </span>
              </>
            ) : (
              <strong>Limite máximo de 3 arquivos .zip atingido</strong>
            )}
          </div>
        </div>

        {/* Lista de arquivos anexados */}
        {files.length > 0 && (
          <ul className="file-list">
            {files.map((file, index) => (
              <li key={`${file.name}-${file.size}`} className="file-item">
                <div className="file-info">
                  <span className="file-badge">Lote {index + 1}</span>
                  <span className="file-name" title={file.name}>
                    {file.name}
                  </span>
                  <span className="file-size">({formatFileSize(file.size)})</span>
                </div>
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeFile(index)}
                  disabled={isLoading}
                  aria-label={`Remover ${file.name}`}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        )}

        {/* Feedbacks de erro ou sucesso */}
        {errorMsg && <div className="alert error">{errorMsg}</div>}
        {successMsg && <div className="alert success">{successMsg}</div>}

        {/* Botão de Ação */}
        <button
          type="button"
          className="submit-btn"
          onClick={handleGenerateReports}
          disabled={files.length === 0 || isLoading}
        >
          {isLoading ? "Processando XMLs e Gerando PDFs..." : "Gerar Relatórios"}
        </button>
      </section>
    </main>
  );
}

export default App;