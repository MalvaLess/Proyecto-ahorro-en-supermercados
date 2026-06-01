import './ProductCard.css'
import { Link } from 'react-router-dom'

function ProductCard({ product }) {
  const productId = product.productId || product.id
  const productImage = product.imageURL || product.image || 'https://via.placeholder.com/300x220?text=Producto'

  return (
    <Link
      to={`/product/${productId}`}
      className="product-card"
    >
      <img
        src={productImage}
        alt={product.name}
      />

      <h3>{product.name}</h3>

      {
        product.brand && (
          <p className="product-brand">
            {product.brand.name}
          </p>
        )
      }

      {
        product.prices && product.prices.length > 0 && (
          <div className="prices-list">
            {
              product.prices.map((item, index) => (
                <div className="price-row" key={index}>
                  <span>{item.market}</span>
                  <strong>{item.price}</strong>
                </div>
              ))
            }
          </div>
        )
      }

      {
        product.categories && product.categories.length > 0 && (
          <div className="product-categories">
            {
              product.categories.map((category) => (
                <span key={category.categoryId}>
                  {category.name}
                </span>
              ))
            }
          </div>
        )
      }
    </Link>
  )
}

export default ProductCard