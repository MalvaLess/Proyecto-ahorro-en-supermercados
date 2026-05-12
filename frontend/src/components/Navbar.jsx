import './Navbar.css'

function Navbar() {
  return (
    <nav className="navbar">
      <h2 className="navbar-logo">Ahorro Supermercados</h2>

      <ul className="navbar-links">
        <li>Inicio</li>
        <li>Comparar</li>
        <li>Ofertas</li>
        <li>Login</li>
      </ul>
    </nav>
  )
}

export default Navbar