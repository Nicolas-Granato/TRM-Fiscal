export function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-container">
        <span>© 2026 TRM Sistemas — Automação Comercial</span>

        <div className="footer-right">
          <span>
            Desenvolvido por <strong>Nícolas Granato</strong>
          </span>
          <a
            href="https://github.com/Nicolas-Granato"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            GitHub
          </a>
          <span className="footer-dot">•</span>
          <a
            href="https://www.linkedin.com/in/nicolasgranato-jf/"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            LinkedIn
          </a>
        </div>
      </div>
    </footer>
  );
}