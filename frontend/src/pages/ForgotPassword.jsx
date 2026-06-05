import './Login.css'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { forgotPassword } from '../services/authService'

function ForgotPassword() {

  const [email, setEmail] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      setError("")
      setSuccess("")
      setLoading(true)

      await forgotPassword(email)

      setSuccess("Si el email está registrado, recibirás un enlace de recuperación.")
      setEmail("")
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Recuperar contraseña</h1>

        <p>Ingresá tu email y te enviaremos un enlace para restablecer tu contraseña.</p>

        {error && <p className="form-error">{error}</p>}
        {success && <p className="form-success">{success}</p>}

        <div className="input-group">
          <label>Correo electrónico</label>
          <input
            type="email"
            placeholder="Ingresa tu correo"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Enviando..." : "Enviar enlace"}
        </button>

        <p className="register-link">
          ¿Recordaste tu contraseña?{" "}
          <Link to="/login" className="register-link-span">
            Iniciar sesión
          </Link>
        </p>
      </form>
    </section>
  )
}

export default ForgotPassword
