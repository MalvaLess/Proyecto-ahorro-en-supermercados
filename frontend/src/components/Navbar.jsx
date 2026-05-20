import './Navbar.css'
import { Link } from 'react-router-dom'
import { FaShoppingCart } from 'react-icons/fa'

function Navbar({ cart = [] }) {

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

        <Link to="/cart" className="cart-icon">

          <FaShoppingCart />

          {
            cart?.length > 0 && (

              <span className="cart-count">
                {cart.length}
              </span>

            )
          }

        </Link>

      </div>

    </nav>
  )
}

export default Navbar