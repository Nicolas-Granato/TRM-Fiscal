interface HeaderProps {
  title: string;
  subtitle: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="card-header">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </header>
  );
}
