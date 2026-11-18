import React, { useRef, useState } from "react";
import { MAX_ZIP_FILES } from "../utils/fileUtils";

interface ZipDropzoneProps {
  isFull: boolean;
  disabled: boolean;
  remainingSlots: number;
  onFilesAdded: (files: FileList | null) => void;
}

export function ZipDropzone({
  isFull,
  disabled,
  remainingSlots,
  onFilesAdded,
}: ZipDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const isBlocked = isFull || disabled;

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

  return (
    <div
      className={`dropzone ${isDragging ? "dragging" : ""} ${
        isBlocked ? "disabled" : ""
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !isBlocked && fileInputRef.current?.click()}
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

      <div className="dropzone-content">
        <span className="dropzone-icon">📦</span>
        {!isFull ? (
          <>
            <strong>Clique para selecionar ou arraste seus arquivos .zip aqui</strong>
            <span className="dropzone-hint">
              Slots disponíveis: {remainingSlots} de {MAX_ZIP_FILES}
            </span>
          </>
        ) : (
          <strong>Limite máximo de {MAX_ZIP_FILES} arquivos .zip atingido</strong>
        )}
      </div>
    </div>
  );
}
