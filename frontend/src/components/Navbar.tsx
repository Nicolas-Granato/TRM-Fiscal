import logoTRM from "../assets/LogoTRM.png";

export function Navbar() {
  return (
    <header className="top-navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <img
            src={logoTRM}
            alt="Logo TRM Sistemas"
            className="navbar-logo"
          />
          <div className="navbar-titles">
            <span className="navbar-system-name">TRM Fiscal</span>
            <span className="navbar-subtitle">
              GERADOR DE RELATÓRIOS FISCAIS
            </span>
          </div>
        </div>

        <a
          href="https://trmsistemas.com.br/"
          target="_blank"
          rel="noopener noreferrer"
          className="navbar-link"
        >
          Sobre a TRM Sistemas <span className="link-arrow">↗</span>
        </a>
      </div>
    </header>
  );
}
