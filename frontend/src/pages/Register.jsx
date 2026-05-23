import './Register.css'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { registerUser } from '../services/authService'

function Register() {

  const navigate = useNavigate();

  const [ formData, setFormData ] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: ""
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    try {
      setError("");
      setLoading(true);

      await registerUser({
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        password: formData.password
      });

      navigate("/login");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (

    <section className="register-page">

      <div className="register-container">

        <h1>Crear cuenta</h1>

        <p>
          Regístrate para comenzar a comparar precios y ahorrar.
        </p>

        <form className="register-form" onSubmit={handleSubmit}>

          {error && <p className="form-error">{error}</p>}

          <div className="input-group">

            <label>Nombre</label>

            <input
              type="text"
              name="firstName"
              placeholder="Ingresa tu nombre"
              value={formData.firstName}
              onChange={handleChange}
            />

          </div>

          <div className="input-group">

            <label>Apellido</label>

            <input
              type="text"
              name="lastName"
              placeholder="Ingresa tu apellido"
              value={formData.lastName}
              onChange={handleChange}
            />

          </div>

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
              placeholder="Crea una contraseña"
              value={formData.password}
              onChange={handleChange}
            />

          </div>

          <div className="input-group">

            <label>Confirmar contraseña</label>

            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirma tu contraseña"
              value={formData.confirmPassword}
              onChange={handleChange}
            />

          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Registrando..." : "Registrarse"}
          </button>

        </form>

      </div>

    </section>
  )
}

export default Register