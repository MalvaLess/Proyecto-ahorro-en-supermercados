import './Register.css'

function Register() {

  return (

    <section className="register-page">

      <div className="register-container">

        <h1>Crear cuenta</h1>

        <p>
          Regístrate para comenzar a comparar precios y ahorrar.
        </p>

        <form className="register-form">

          <div className="input-group">

            <label>Nombre</label>

            <input
              type="text"
              placeholder="Ingresa tu nombre"
            />

          </div>

          <div className="input-group">

            <label>Correo electrónico</label>

            <input
              type="email"
              placeholder="Ingresa tu correo"
            />

          </div>

          <div className="input-group">

            <label>Contraseña</label>

            <input
              type="password"
              placeholder="Crea una contraseña"
            />

          </div>

          <div className="input-group">

            <label>Confirmar contraseña</label>

            <input
              type="password"
              placeholder="Confirma tu contraseña"
            />

          </div>

          <button type="submit">
            Registrarse
          </button>

        </form>

      </div>

    </section>
  )
}

export default Register