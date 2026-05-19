import './HowItWorks.css'

function HowItWorks() {
  return (
    <section className="how">

      <div className="how-header">
        <h2>¿Cómo funciona?</h2>

        <p>
          Empieza a ahorrar en pocos pasos.
        </p>
      </div>

      <div className="how-steps">

        <div className="step-card">

          <div className="step-number">
            1
          </div>

          <h3>Busca productos</h3>

          <p>
            Encuentra artículos disponibles en distintos supermercados.
          </p>

        </div>

        <div className="step-card">

          <div className="step-number">
            2
          </div>

          <h3>Compara precios</h3>

          <p>
            Revisa rápidamente cuál opción es más económica.
          </p>

        </div>

        <div className="step-card">

          <div className="step-number">
            3
          </div>

          <h3>Ahorra dinero</h3>

          <p>
            Toma mejores decisiones y optimiza tu presupuesto.
          </p>

        </div>

      </div>

    </section>
  )
}

export default HowItWorks