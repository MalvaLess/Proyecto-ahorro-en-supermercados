import './ProductCard.css'
import { Link } from 'react-router-dom'

function ProductCard({ product }) {

  const bestPrice = product.prices[0]

  const highestPrice = product.prices.reduce((max, item) => {

    const currentPrice = Number(
      item.price.replace('$', '').replace('.', '')
    )

    return currentPrice > max ? currentPrice : max

  }, 0)

  const lowestPrice = Number(
    bestPrice.price.replace('$', '').replace('.', '')
  )

  const savings = highestPrice - lowestPrice
  const productId = product.productId || product.id
  const productImage = product.imageURL || product.image || 'https://via.placeholder.com/300x220?text=Producto'

  return (
    <Link
      to={`/product/${productId}`}
      className="product-card"
    >

      <div className="product-image-container">

        <img
          src={productImage}
          alt={product.name}
        />

      </div>

      <div className="product-info">

        <h3>{product.name}</h3>

        <p className="availability-text">

          {
            product.prices.length === 1
              ? `Disponible solo en ${product.prices[0].market}`
              : `Disponible en ${product.prices.length} supermercados`
          }

        </p>


      <div className="best-price-box">

        <div className="best-price-row">

          <div className="best-market-info">

            <strong>{bestPrice.market}</strong>

            <span className="best-price-tag">

              Mejor precio

            </span>

          </div>

          <span>{bestPrice.price}</span>

        </div>

      </div>

      <div className="markets-preview">

        {
          product.prices.slice(1).map((item, index) => (

            <div
              className="market-preview-row"
              key={index}
            >

              <span>{item.market}</span>

              <span>{item.price}</span>

            </div>

          ))
        }

      </div>

      {
        savings > 0 && (

          <div className="savings-text">

            ↗ Ahorra hasta ${savings.toLocaleString()}

          </div>

        )
      }

    </div>

    </Link >

  )
}

export default ProductCard