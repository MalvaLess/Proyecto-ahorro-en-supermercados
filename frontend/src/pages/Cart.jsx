import './Cart.css'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { apiRequest } from '../services/apiClient'
import { isAuthenticated } from '../services/authService'

function Cart({ cart, setCart }) {
  const [listName, setListName] = useState('Mi lista de productos')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [listSaved, setListSaved] = useState(false)

  function removeProduct(indexToRemove) {
    const updatedCart = cart.filter(
      (_, index) => index !== indexToRemove
    )

    setCart(updatedCart)
  }

  function getItemPrice(item) {
    if (typeof item.unitPrice === 'number') {
      return item.unitPrice
    }

    if (typeof item.finalPrice === 'number') {
      return item.finalPrice
    }

    if (typeof item.price === 'number') {
      return item.price
    }

    if (typeof item.price === 'string') {
      return Number(
        item.price
          .replace('$', '')
          .replace(/\./g, '')
          .replace(',', '.')
          .trim()
      )
    }

    return 0
  }

  function formatPrice(value, currency = 'UYU') {
    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency,
      maximumFractionDigits: 0
    }).format(value)
  }

  function increaseCartItemQuantity(indexToUpdate) {
    const updatedCart = cart.map((item, index) => {
      if (index === indexToUpdate) {
        const newQuantity = item.quantity + 1

        return {
          ...item,
          quantity: newQuantity,
          totalPrice: item.unitPrice * newQuantity
        }
      }

      return item
    })

    setCart(updatedCart)
  }

  function decreaseCartItemQuantity(indexToUpdate) {
    const updatedCart = cart
      .map((item, index) => {
        if (index === indexToUpdate) {
          const newQuantity = item.quantity - 1

          if (newQuantity <= 0) {
            return null
          }

          return {
            ...item,
            quantity: newQuantity,
            totalPrice: item.unitPrice * newQuantity
          }
        }

        return item
      })
      .filter(Boolean)

    setCart(updatedCart)
  }

  const total = cart.reduce((acc, item) => {
    const quantity = item.quantity || 1
    const price = getItemPrice(item)

    return acc + price * quantity
  }, 0)

  async function saveShoppingList() {
    if (!isAuthenticated()) {
      setMessage('')
      setError('Debes iniciar sesión o crear una cuenta para guardar tu lista.')
      return
    }

    if (cart.length === 0) {
      setMessage('')
      setError('Tu lista está vacía.')
      return
    }

    try {
      setSaving(true)
      setError('')
      setMessage('')

      const shoppingListResponse = await apiRequest('/shopping-lists/', {
        method: 'POST',
        body: JSON.stringify({
          name: listName
        })
      })

      const shoppingListId = shoppingListResponse.data.shoppingListId

      for (const item of cart) {
        await apiRequest(`/shopping-lists/${shoppingListId}/items`, {
          method: 'POST',
          body: JSON.stringify({
            productId: item.productId,
            selectedStoreProductId: item.selectedStoreProductId,
            quantity: item.quantity || 1,
            unitPrice: getItemPrice(item)
          })
        })
      }

        setMessage('Lista guardada correctamente.')

        setCart([])

        localStorage.removeItem('cart')

        setListName('Mi lista de productos')
        setListSaved(false)
    } catch (error) {
      setError(error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="cart-page">
        <h1 className="cart-title">
        Mi lista de productos
        </h1>

        {message && (
        <p className="cart-success">
            {message}
        </p>
        )}

        {error && (
        <p className="cart-error">
            {error}
        </p>
        )}

      {
        cart.length === 0 ? (
          <div className="empty-cart">
            <h2>
              Tu lista está vacía
            </h2>

            <p>
              Agrega{' '}
              <strong>
                <Link
                  to="/products"
                  className="link-to-product"
                >
                  productos
                </Link>
              </strong>{' '}
              para comenzar a comparar precios.
            </p>
          </div>
        ) : (
          <div className="cart-layout">
            <div className="cart-products">
              {
                cart.map((item, index) => {
                  const image = item.imageURL || item.image || 'https://via.placeholder.com/120x120?text=Producto'
                  const market = item.storeChainName || item.market || 'Sin supermercado'
                  const quantity = item.quantity || 1
                  const unitPrice = getItemPrice(item)
                  const itemTotal = unitPrice * quantity
                  const currency = item.currency || 'UYU'

                  return (
                    <div className="cart-item" key={item.cartItemId || index}>
                      <div className="cart-item-image">
                        <img
                          src={image}
                          alt={item.name}
                        />
                      </div>

                      <div className="cart-item-info">
                        <h3>{item.name}</h3>
                        <p>{market}</p>

                        <span className="cart-item-quantity-label">
                          Cantidad: {quantity}
                        </span>
                      </div>

                      <div className="cart-item-quantity-box">
                        <button
                          type="button"
                          onClick={() => decreaseCartItemQuantity(index)}
                        >
                          -
                        </button>

                        <span>{quantity}</span>

                        <button
                          type="button"
                          onClick={() => increaseCartItemQuantity(index)}
                        >
                          +
                        </button>
                      </div>

                      <div className="cart-item-actions">
                        <strong>{formatPrice(itemTotal, currency)}</strong>

                        <button
                          type="button"
                          onClick={() => removeProduct(index)}
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  )
                })
              }
            </div>

            <div className="budget-summary">
              <h2>
                Resumen de presupuesto
              </h2>

              <div className="summary-row">
                <span>Productos</span>
                <strong>{cart.length}</strong>
              </div>

              <div className="summary-row">
                <span>Total estimado</span>
                <strong>{formatPrice(total, 'UYU')}</strong>
              </div>

              <div className="summary-list-name">
                <label>Nombre de la lista</label>

                <input
                  type="text"
                  value={listName}
                  onChange={(event) => setListName(event.target.value)}
                />
              </div>

              {
                error && (
                  <p className="cart-error">
                    {error}
                  </p>
                )
              }

              {
                message && (
                  <p className="cart-success">
                    {message}
                  </p>
                )
              }

              {
                !isAuthenticated() && (
                  <div className="cart-login-warning">
                    <p>
                      Para guardar tu lista debes iniciar sesión o crear una cuenta.
                    </p>

                    <div className="cart-auth-links">
                      <Link to="/login">Iniciar sesión</Link>
                      <Link to="/register">Crear cuenta</Link>
                    </div>
                  </div>
                )
              }

              <button
                type="button"
                className="save-budget-btn"
                onClick={saveShoppingList}
                disabled={saving || listSaved}
              >
                {saving ? "Guardando..." : listSaved ? "Lista guardada" : "Guardar lista"}
              </button>
            </div>
          </div>
        )
      }
    </section>
  )
}

export default Cart