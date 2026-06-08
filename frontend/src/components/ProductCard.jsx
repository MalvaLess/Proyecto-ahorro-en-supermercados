import './ProductCard.css'
import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { FaHeart, FaRegHeart } from 'react-icons/fa'


function ProductCard({ product }) {
  const location = useLocation()
  const [isFavorite, setIsFavorite] = useState(false)
  const [isHovered, setIsHovered] = useState(false)



  const handleFavorite = async (e) => {
    e.preventDefault()
    e.stopPropagation()

    try {
      await apiRequest('/favorites/', {
        method: 'POST',
        body: JSON.stringify({
          productId: productId
        })
      })

      setIsFavorite(!isFavorite)

    } catch (error) {
      alert('Debes iniciar sesión')
    }
  }
  const [fav, setFav] = useState(false);
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
      <button
        className="favorite-btn"
        onClick={handleFavorite}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {
          (isFavorite || isHovered)
            ? <FaHeart />     
            : <FaRegHeart />  
        }
      </button>
      <img
        src={productImage}
        alt={product.name}
      />

      <h3 className='product-info'>{product.name}</h3>

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

                  <div className="price-value">
                    {item.hasOffer && item.normalPrice && (
                      <span className="normal-price-crossed">{item.normalPrice}</span>
                    )}
                    <strong>{item.price}</strong>
                    {item.ocaPrice && (
                      <span className="oca-price">OCA: {item.ocaPrice}</span>
                    )}
                  </div>
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