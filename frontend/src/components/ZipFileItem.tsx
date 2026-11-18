import { formatFileSize } from "../utils/fileUtils";

interface ZipFileItemProps {
  file: File;
  index: number;
  disabled: boolean;
  onRemove: (index: number) => void;
}

export function ZipFileItem({ file, index, disabled, onRemove }: ZipFileItemProps) {
  return (
    <li className="file-item">
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
        onClick={() => onRemove(index)}
        disabled={disabled}
        aria-label={`Remover ${file.name}`}
      >
        ✕
      </button>
    </li>
  );
}
