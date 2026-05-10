import './Categories.css'

function Categories() {
  return (
    <section className="categories">

      <div className="categories-header">
        <h2>Categorías</h2>
        <p>Explora productos por categoría</p>
      </div>

      <div className="categories-grid">

        <div className="category-card">
          <div className="category-icon">🥦</div>
          <h3>Verduras</h3>
        </div>

        <div className="category-card">
          <div className="category-icon">🍎</div>
          <h3>Frutas</h3>
        </div>

        <div className="category-card">
          <div className="category-icon">🥩</div>
          <h3>Carnes</h3>
        </div>

        <div className="category-card">
          <div className="category-icon">🥤</div>
          <h3>Bebidas</h3>
        </div>

        <div className="category-card">
          <div className="category-icon">🍪</div>
          <h3>Snacks</h3>
        </div>

      </div>

    </section>
  )
}

export default Categories