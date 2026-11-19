interface HeaderProps {
  title: string;
  subtitle: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  return (
    <div className="card-header">
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </div>
  );
}
