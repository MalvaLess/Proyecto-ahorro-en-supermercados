import './Login.css'
import { Link } from 'react-router-dom'

function Login() {
  return (
    <section className="login-page">
      <form className="login-form">
        <h1>Login</h1>

        <p>Inicia sección para encontrar las mejores ofertas.</p>

        <div className="input-group">
          <label>Correo electrónico</label>
          <input type="email" placeholder="Ingresa tu correo" />
        </div>

        <div className="input-group">
          <label>Contraseña</label>
          <input type="password" placeholder="Ingresa tu contraseña" />
        </div>

        <button type="submit">Iniciar sesión</button>

        <p className="register-link">
          ¿No tienes cuenta?{" "}
          <Link to="/register" className="register-link-span">
            Crear cuenta
          </Link>
        </p>
      </form>
    </section>
  )
}

export default Login