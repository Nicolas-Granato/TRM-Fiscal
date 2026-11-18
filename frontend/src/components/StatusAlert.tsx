interface StatusAlertProps {
  type: "error" | "success";
  message: string | null;
}

export function StatusAlert({ type, message }: StatusAlertProps) {
  if (!message) return null;

  return (
    <div className={`alert ${type}`} role="alert">
      {message}
    </div>
  );
}
