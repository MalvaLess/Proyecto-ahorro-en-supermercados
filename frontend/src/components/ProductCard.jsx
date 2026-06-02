import './ProductCard.css'
import { Link, useLocation } from 'react-router-dom'

function ProductCard({ product }) {
  const location = useLocation()

  const productId = product.productId || product.id
  const productImage = product.imageURL || product.image || 'https://via.placeholder.com/300x220?text=Producto'

  return (
    <Link
      to={`/product/${productId}`}
      state={{
        from: `${location.pathname}${location.search}`
      }}
      className="product-card"
    >
      <img
        src={productImage}
        alt={product.name}
      />

      <h3>{product.name}</h3>

      <div className="available-stores">
        🛒 Disponible en {product.availableStores || 0} supermercados
      </div>

      {
        product.prices && product.prices.length > 0 ? (
          <div className="prices-list">
            {
              product.prices.map((item, index) => (
                <div className="price-row" key={index}>
                  <div className="market-info">
                    <span>{item.market}</span>

                    {
                      item.isBestPrice && (
                        <small>Mejor precio</small>
                      )
                    }
                  </div>

                  <strong>{item.price}</strong>
                </div>
              ))
            }
          </div>
        ) : (
          <div className="no-card-prices">
            Sin precios disponibles
          </div>
        )
      }

      {
        product.prices && product.prices.length > 1 && (
          <div className="saving-box">
            ↑ Ahorra hasta {product.saving}
          </div>
        )
      }
    </Link>
  )
}

export default ProductCard