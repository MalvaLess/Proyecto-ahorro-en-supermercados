import './ProductCard.css'

function ProductCard({ image, name, price }) {
  return (
    <div className="product-card">

      <img src={image} alt={name} />

      <h3>{name}</h3>

      <p>${price}</p>

      <button>
        Agregar al carrito
      </button>

    </div>
  )
}

export default ProductCard