import React, { useRef, useState } from "react";
import { formatFileSize, MAX_ZIP_FILES } from "../utils/fileUtils";

interface ZipDropzoneProps {
  files: File[];
  isFull: boolean;
  disabled: boolean;
  remainingSlots: number;
  onFilesAdded: (files: FileList | null) => void;
  onRemoveFile: (index: number) => void;
}

export function ZipDropzone({
  files,
  isFull,
  disabled,
  remainingSlots,
  onFilesAdded,
  onRemoveFile,
}: ZipDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const isBlocked = isFull || disabled;
  const hasFiles = files.length > 0;

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!isBlocked) setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (!isBlocked) {
      onFilesAdded(e.dataTransfer.files);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilesAdded(e.target.files);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const openFilePicker = () => {
    if (!isBlocked) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="upload-box-card">
      <div className="upload-box-header">
        <span className="upload-box-icon">📦</span>
        <h3>Pacotes de XMLs (.ZIP) [Máx. {MAX_ZIP_FILES}]</h3>
      </div>

      <div
        className={`dropzone ${hasFiles ? "has-files" : ""} ${
          isDragging ? "dragging" : ""
        } ${isBlocked ? "disabled" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!hasFiles ? openFilePicker : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip,application/zip"
          multiple
          hidden
          onChange={handleInputChange}
          disabled={isBlocked}
        />

        {!hasFiles ? (
          <div className="dropzone-content">
            <span className="dropzone-plus">+</span>
            <span className="dropzone-text">
              Arraste ou clique para selecionar os pacotes .ZIP
            </span>
            <span className="dropzone-hint">
              Slots disponíveis: {remainingSlots} de {MAX_ZIP_FILES}
            </span>
          </div>
        ) : (
          <div className="inner-files-wrapper">
            <ul className="inner-file-list">
              {files.map((file, index) => (
                <li key={`${file.name}-${file.size}-${index}`} className="inner-file-item">
                  <div className="inner-file-left">
                    <span className="inner-file-icon">📦</span>
                    <div className="inner-file-details">
                      <span className="inner-file-name" title={file.name}>
                        {file.name}
                      </span>
                      <span className="inner-file-size">
                        {formatFileSize(file.size)}
                      </span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="inner-remove-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveFile(index);
                    }}
                    disabled={disabled}
                    aria-label={`Remover ${file.name}`}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>

            {!isFull && (
              <button
                type="button"
                className="add-more-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  openFilePicker();
                }}
                disabled={disabled}
              >
                + Adicionar outro pacote .ZIP ({remainingSlots} restante
                {remainingSlots > 1 ? "s" : ""})
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
