import { ZipFileItem } from "./ZipFileItem";

interface ZipFileListProps {
  files: File[];
  disabled: boolean;
  onRemoveFile: (index: number) => void;
}

export function ZipFileList({ files, disabled, onRemoveFile }: ZipFileListProps) {
  if (files.length === 0) return null;

  return (
    <ul className="file-list">
      {files.map((file, index) => (
        <ZipFileItem
          key={`${file.name}-${file.size}`}
          file={file}
          index={index}
          disabled={disabled}
          onRemove={onRemoveFile}
        />
      ))}
    </ul>
  );
}
