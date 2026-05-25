import './Navbar.css'
import { Link } from 'react-router-dom'
import { FaShoppingCart } from 'react-icons/fa'
import { useEffect, useState } from 'react'
import { isAuthenticated } from '../services/authService';

function Navbar({ cart = [] }) {

  const [ loggedIn, setLoggedIn ] = useState(isAuthenticated());

  function refreshAuthState() {
    setLoggedIn(isAuthenticated());
  }

  useEffect(() => {
    refreshAuthState();

    window.addEventListener('auth-change', refreshAuthState);

    return() => {
      window.removeEventListener("auth-change", refreshAuthState)
    }
  }, []);

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