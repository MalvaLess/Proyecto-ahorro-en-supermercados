import './ProductCard.css'
import { Link } from 'react-router-dom'

function ProductCard({ product }) {

  return (

    <Link
      to={`/product/${product.slug}`}
      className="product-card"
    >
      <img
        src={product.image}
        alt={product.name}
      />

      <h3>{product.name}</h3>

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

    </Link>

  )
}

export default ProductCard