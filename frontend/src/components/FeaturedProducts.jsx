import './FeaturedProducts.css'

function Products() {
  return (
    <section className="products">

      <div className="products-header">
        <h2>Productos destacados</h2>
        <p>Compara precios entre supermercados</p>
      </div>

      <div className="products-grid">

        <div className="product-card">
          <img
            src="https://images.unsplash.com/photo-1586201375761-83865001e31c"
            alt="Manzanas"
          />

          <h3>Manzanas</h3>

          <p>$3.99</p>

          <button>Ver oferta</button>
        </div>

        <div className="product-card">
          <img
            src="https://images.unsplash.com/photo-1615485290382-441e4d049cb5"
            alt="Leche"
          />

          <h3>Leche</h3>

          <p>$2.50</p>

          <button>Ver oferta</button>
        </div>

        <div className="product-card">
          <img
            src="https://images.unsplash.com/photo-1502741338009-cac2772e18bc"
            alt="Vegetales"
          />

          <h3>Vegetales</h3>

          <p>$5.20</p>

          <button>Ver oferta</button>
        </div>

      </div>

    </section>
  )
}

export default Products