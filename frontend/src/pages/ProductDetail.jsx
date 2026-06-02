import './ProductDetail.css'
import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { apiRequest } from '../services/apiClient'

function ProductDetail({ cart, setCart }) {
  const { id } = useParams()
  const location = useLocation()

  const backUrl = location.state?.from || '/products'

  const [product, setProduct] = useState(null)
  const [priceItems, setPriceItems] = useState([])
  const [selectedPrice, setSelectedPrice] = useState(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const chainIds = '1,2,3,4'

  function formatPrice(value, currency) {
    if (value === null || value === undefined) {
      return 'Sin precio'
    }

    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency: currency || 'UYU',
      maximumFractionDigits: 0
    }).format(value)
  }

  async function loadProductDetail() {
    try {
      setLoading(true)
      setError('')

      const productResponse = await apiRequest(`/products/${id}`)

      const comparisonResponse = await apiRequest(
        `/price-comparison/products/${id}?chainIds=${chainIds}`
      )

      const productData = productResponse.data
      const pricesData = comparisonResponse.data.items || []

      setProduct(productData)
      setPriceItems(pricesData)

      if (pricesData.length > 0) {
        setSelectedPrice(pricesData[0])
      }
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProductDetail()
  }, [id])

  function handleAddToCart() {
    if (!product) return

    const cartItem = {
      cartItemId: `${product.productId}-${selectedPrice?.storeProductId || 'no-store'}-${Date.now()}`,
      productId: product.productId,
      name: product.name,
      imageURL: product.imageURL,
      brand: product.brand,
      quantity: 1,
      selectedStoreProductId: selectedPrice?.storeProductId || null,
      storeChainName: selectedPrice?.storeChainName || null,
      storeAddress: selectedPrice?.storeAddress || null,
      unitPrice: selectedPrice?.finalPrice || 0,
      currency: selectedPrice?.currency || 'UYU',
      totalPrice: selectedPrice?.finalPrice || 0
    }

    setCart([...cart, cartItem])
    setMessage('Producto agregado al carrito correctamente.')
  }

  if (loading) {
    return (
      <section className="product-detail-page">
        <p>Cargando producto...</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="product-detail-page">
        <Link to={backUrl} className="back-link">
          ← Volver
        </Link>

        <div className="product-detail-error">
          {error}
        </div>
      </section>
    )
  }

  if (!product) {
    return (
      <section className="product-detail-page">
        <Link to={backUrl} className="back-link">
          ← Volver
        </Link>

        <div className="product-detail-error">
          Producto no encontrado.
        </div>
      </section>
    )
  }

  const productImage = product.imageURL || 'https://via.placeholder.com/500x400?text=Producto'

  return (
    <section className="product-detail-page">

      <Link to={backUrl} className="back-link">
        ← Volver a la lista
      </Link>

      <div className="product-detail-layout">

        <div className="product-detail-left">

          <h1>{product.name}</h1>

          <p className="product-description">
            {product.description || 'Producto disponible para comparar precios entre supermercados.'}
          </p>

          <div className="product-image-card">
            <img
              src={productImage}
              alt={product.name}
            />
          </div>

        </div>

        <div className="product-detail-right">

          <div className="available-summary">
            🛒 Disponible en {priceItems.length} supermercados
          </div>

          <div className="stores-card">

            <h2>Selecciona el supermercado que prefieras</h2>

            {
              priceItems.length > 0 ? (

                <div className="store-price-list">

                  {
                    priceItems.map((item, index) => (
                      <button
                        type="button"
                        key={item.storeProductId}
                        className={
                          selectedPrice?.storeProductId === item.storeProductId
                            ? 'store-price-row selected'
                            : 'store-price-row'
                        }
                        onClick={() => setSelectedPrice(item)}
                      >

                        <div className="store-info">
                          <strong>{item.storeChainName}</strong>

                          {
                            index === 0 && (
                              <span>Mejor precio</span>
                            )
                          }

                          {
                            item.hasOffer && (
                              <small>Oferta disponible</small>
                            )
                          }
                        </div>

                        <div className="store-price">
                          {formatPrice(item.finalPrice, item.currency)}
                        </div>

                      </button>
                    ))
                  }

                </div>

              ) : (

                <div className="no-prices-detail">
                  No hay precios disponibles para este producto.
                </div>

              )
            }

          </div>

          {message && <p className="product-detail-success">{message}</p>}

          <button
            type="button"
            className="add-to-cart-button"
            onClick={handleAddToCart}
            disabled={priceItems.length === 0}
          >
            Agrega producto a tu lista
          </button>

        </div>

      </div>

    </section>
  )
}

export default ProductDetail