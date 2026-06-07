import "./Footer.css";
import logo from "../assets/logo-SM.png";

function Footer() {
  return (
    <footer className="footer">

      <img
        src={logo}
        alt="SmartMarket"
        className="footer-logo"
      />

      <p className="footer-copy">
        © 2026 SmartMarket
      </p>

    </footer>
  );
}

export default Footer;