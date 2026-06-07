import './Login.css'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { resetPassword } from '../services/authService'

function ResetPassword() {

  const { token } = useParams()
  const navigate = useNavigate()

  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    if (password !== confirm) {
      setError("Las contraseñas no coinciden")
      return
    }

    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres")
      return
    }

    try {
      setError("")
      setLoading(true)

      await resetPassword(token, password)

      navigate("/login")
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Nueva contraseña</h1>

        <p>Ingresá tu nueva contraseña.</p>

        {error && <p className="form-error">{error}</p>}

        <div className="input-group">
          <label>Nueva contraseña</label>
          <input
            type="password"
            placeholder="Ingresa tu nueva contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="input-group">
          <label>Confirmar contraseña</label>
          <input
            type="password"
            placeholder="Confirmá tu nueva contraseña"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Guardando..." : "Guardar contraseña"}
        </button>

        <p className="register-link">
          <Link to="/login" className="register-link-span">
            Volver al inicio de sesión
          </Link>
        </p>
      </form>
    </section>
  )
}

export default ResetPassword
