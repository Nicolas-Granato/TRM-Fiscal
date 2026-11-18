interface GenerateButtonProps {
  isLoading: boolean;
  disabled: boolean;
  onClick: () => void;
}

export function GenerateButton({ isLoading, disabled, onClick }: GenerateButtonProps) {
  return (
    <button
      type="button"
      className="submit-btn"
      onClick={onClick}
      disabled={disabled || isLoading}
    >
      {isLoading ? "Processando XMLs e Gerando PDFs..." : "Gerar Relatórios"}
    </button>
  );
}
