import './Navbar.css'
import { Link } from 'react-router-dom'
import { FaShoppingCart } from 'react-icons/fa'

function Navbar() {
  return (
    <nav className="navbar">

      <div className="logo">
        SmartMarket
      </div>

      <div className="nav-links">

        <Link to="/">Inicio</Link>

        <Link to="/products">Productos</Link>

        <Link to="/offers">Ofertas</Link>

        <Link to="/about">Nosotros</Link>

        <Link to="/login">Login</Link>

        <div className="cart-icon">
          <FaShoppingCart />
        </div>

      </div>

    </nav>
  )
}

export default Navbar