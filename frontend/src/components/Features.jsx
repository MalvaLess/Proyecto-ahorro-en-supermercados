import './Features.css'

function Features() {
  return (
    <section className="features">

      <div className="feature-card">

        <div className="feature-icon">
          💰
        </div>

        <h3>Compara precios</h3>

        <p>
          Encuentra los productos más económicos entre supermercados.
        </p>
      </div>

      <div className="feature-card">

        <div className="feature-icon">
          🛒
        </div>

        <h3>Encuentra ofertas</h3>

        <p>
          Descubre promociones y descuentos disponibles.
        </p>
      </div>

      <div className="feature-card">

        <div className="feature-icon">
          📈
        </div>

        <h3>Controla gastos</h3>

        <p>
          Administra mejor tu presupuesto mensual.
        </p>
      </div>

    </section>
  )
}

export default Features