import './Navbar.css'
import { Link } from 'react-router-dom'
import { FaShoppingCart } from 'react-icons/fa'
import { useEffect, useState } from 'react'
import { isAuthenticated } from '../services/authService';
import logo from '../assets/logo-SM.png'

function Navbar({ cart = [] }) {

  const [loggedIn, setLoggedIn] = useState(isAuthenticated());
  const [menuOpen, setMenuOpen] = useState(false);

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

  function closeMenu() {
    setMenuOpen(false);
  }

  return (

    <nav className="navbar">

      <Link to="/" className="logo" onClick={closeMenu}>
        <img src={logo} alt="SmartMarket" className="logo-image" />
      </Link>

      <button
        className="hamburger"
        onClick={() => setMenuOpen(prev => !prev)}
        aria-label="Menú"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <div className={`nav-links${menuOpen ? ' open' : ''}`}>

        <Link to="/" onClick={closeMenu}>Inicio</Link>

        <Link to="/products" onClick={closeMenu}>Productos</Link>

        <Link to="/offers" onClick={closeMenu}>Ofertas</Link>

        <Link to="/about" onClick={closeMenu}>Nosotros</Link>

        {
          loggedIn ? (
            <Link to="/account" onClick={closeMenu}>Mi Cuenta</Link>
          ) : (
            <Link to="/login" onClick={closeMenu}>Login</Link>
          )
        }

        <Link to="/cart" className="cart-icon" onClick={closeMenu}>

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