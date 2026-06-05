import './Login.css'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { GoogleLogin } from '@react-oauth/google'
import { loginUser, googleLogin } from '../services/authService'

function Login() {

  const navigate = useNavigate();

  const [ formData, setFormData ] = useState({
    email: "",
    password: ""
  });

  const [ error, setError ] = useState("");

  const [ loading, setLoading ] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setError("");
      setLoading(true);

      await loginUser(formData);

      navigate("/")
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse) {
    try {
      setError("");
      setLoading(true);

      await googleLogin(credentialResponse.credential);

      navigate("/")
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Login</h1>

        <p>Inicia sección para encontrar las mejores ofertas.</p>

        {error && <p className="form-error">{error}</p>}

        <div className="input-group">
          <label>Correo electrónico</label>
          <input 
          type="email" 
          name="email"
          placeholder="Ingresa tu correo"
          value={formData.email}
          onChange={handleChange}
          />
        </div>

        <div className="input-group">
          <label>Contraseña</label>
          <input 
          type="password" 
          name="password"
          placeholder="Ingresa tu contraseña" 
          value={formData.password}
          onChange={handleChange}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Ingresando..." : "Iniciar sesión"}
        </button>

        <p className="register-link">
          ¿No tienes cuenta?{" "}
          <Link to="/register" className="register-link-span">
            Crear cuenta
          </Link>
        </p>

        <p className="register-link">
          ¿Olvidaste tu contraseña?{" "}
          <Link to="/forgot-password" className="register-link-span">
            Recuperar contraseña
          </Link>
        </p>

        <div className="login-divider">
          <span>o</span>
        </div>

        <div className="google-login-wrapper">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError("Error al iniciar sesión con Google")}
            width="100%"
            theme="outline"
            size="large"
            text="signin_with"
            locale="es"
          />
        </div>
      </form>
    </section>
  )
}

export default Login