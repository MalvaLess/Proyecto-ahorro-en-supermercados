import './FeaturedProducts.css'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest } from '../services/apiClient'

let _cache = null
let _cacheTs = 0
const CACHE_TTL = 5 * 60 * 1000

function FeaturedProducts() {

  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [startIndex, setStartIndex] = useState(0)
  const [animClass, setAnimClass] = useState('')

  useEffect(() => {
    const now = Date.now()

    if (_cache && (now - _cacheTs) < CACHE_TTL) {
      setProducts(_cache)
      setLoading(false)
      return
    }

    async function fetchTopDiscounts() {
      try {
        const response = await apiRequest("/price-comparison/top-discounts?limit=10")
        _cache = response.data
        _cacheTs = Date.now()
        setProducts(response.data)
      } catch (error) {
        console.error("Error al cargar productos destacados:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchTopDiscounts()
  }, [])

  function getVisibleProducts() {
    if (products.length === 0) return []
    return [0, 1, 2].map(i => products[(startIndex + i) % products.length])
  }

  function navigate(direction) {
    const anim = direction === 'next' ? 'slide-left' : 'slide-right'
    setStartIndex(prev =>
      direction === 'next'
        ? (prev + 1) % products.length
        : (prev - 1 + products.length) % products.length
    )
    setAnimClass(anim)
    setTimeout(() => setAnimClass(''), 450)
  }

  const visible = getVisibleProducts()

  return (
    <section className="products">

      <div className="products-header">
        <h2>Productos destacados</h2>
        <p>Los 10 productos con mayor descuento hoy</p>
      </div>

      {loading ? (
        <p className="products-loading">Cargando productos...</p>
      ) : products.length === 0 ? (
        <p className="products-loading">No hay productos en oferta en este momento.</p>
      ) : (
        <div className="carousel-wrapper">

          <button className="carousel-btn carousel-btn-left" onClick={() => navigate('prev')}>&#8249;</button>

          <div className={`products-featured-grid ${animClass}`}>
            {visible.map((product) => (
              <div className="product-card" key={`${product.productId}-${startIndex}`}>

                {product.discountPct > 0 && (
                  <div className="discount-badge">-{product.discountPct}%</div>
                )}

                {product.imageURL ? (
                  <img src={product.imageURL} alt={product.name} />
                ) : (
                  <div className="product-card-no-image">Sin imagen</div>
                )}

                <div className="product-card-body">
                  <h3>{product.name}</h3>
                  {product.brand && <p className="product-card-brand">{product.brand}</p>}

                  <div className="product-card-prices">
                    {product.normalPrice && (
                      <span className="price-original">${product.normalPrice.toLocaleString("es-UY")}</span>
                    )}
                    <span className="price-offer">${product.offerPrice.toLocaleString("es-UY")}</span>
                  </div>

                  <Link to={`/product/${product.productId}`}>
                    <button>Ver oferta</button>
                  </Link>
                </div>

              </div>
            ))}
          </div>

          <button className="carousel-btn carousel-btn-right" onClick={() => navigate('next')}>&#8250;</button>

        </div>
      )}

    </section>
  )
}

export default FeaturedProducts
