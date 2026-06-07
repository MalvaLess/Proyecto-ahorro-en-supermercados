import './Navbar.css'
import { Link } from 'react-router-dom'
import { FaShoppingCart } from 'react-icons/fa'
import { useEffect, useState } from 'react'
import { isAuthenticated } from '../services/authService';
import logo from '../assets/logo-SM.png'

function Navbar({ cart = [] }) {

  const [loggedIn, setLoggedIn] = useState(isAuthenticated());

  const cartTotalQuantity = cart.reduce((acc, item) => {
    return acc + (item.quantity || 1)
  }, 0)

  function refreshAuthState() {
    setLoggedIn(isAuthenticated());
  }

  useEffect(() => {
    refreshAuthState();

    window.addEventListener('auth-change', refreshAuthState);

    return () => {
      window.removeEventListener("auth-change", refreshAuthState)
    }
  }, []);

  return (

    <nav className="navbar">

      <Link to="/" className="logo">
        <img src={logo} alt="SmartMarket" className="logo-image" />
      </Link>

      <div className="nav-links">

        <Link to="/">Inicio</Link>

        <Link to="/products">Productos</Link>

        <Link to="/offers">Ofertas</Link>

        <Link to="/about">Nosotros</Link>

        {
          loggedIn ? (
            <Link to="/account">Mi Cuenta</Link>
          ) : (
            <Link to="/login">Login</Link>
          )
        }

        <Link to="/cart" className="cart-icon">

          <FaShoppingCart />

          {
            cartTotalQuantity > 0 && (

              <span className="cart-count">
                {cartTotalQuantity}
              </span>

            )
          }

        </Link>

      </div>

    </nav>
  )
}

export default Navbar