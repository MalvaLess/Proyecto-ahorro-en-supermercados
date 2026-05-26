import './Cart.css'
import { Link } from 'react-router-dom'

function Cart({ cart, setCart }) {

    const removeProduct = (indexToRemove) => {

        const updatedCart = cart.filter(
            (_, index) => index !== indexToRemove
        )

        setCart(updatedCart)
    }

    const total = cart.reduce((acc, item) => {

        const cleanPrice = Number(
            item.price.replace('$', '').replace('.', '')
        )

        return acc + cleanPrice

    }, 0)

    return (

        <section className="cart-page">

            <h1 className="cart-title">
                Mi lista de productos
            </h1>

            {
                cart.length === 0 ? (

                    <div className="empty-cart">

                        <h2>
                            Tu lista está vacía
                        </h2>

                        <p>
                            Agrega <strong>
                                <Link
                                    to= '/products'
                                    className='link-to-product'
                                >
                                    productos
                                </Link>

                            </strong> para comenzar a comparar precios.
                        </p>

                    </div>

                ) : (

                    <div className="cart-layout">

                        <div className="cart-products">

                            {
                                cart.map((item, index) => (

                                    <div className="cart-item" key={index}>

                                        <div className="cart-item-left">

                                            <img
                                                src={item.image}
                                                alt={item.name}
                                            />

                                            <div>

                                                <h3>{item.name}</h3>

                                                <p>{item.market}</p>

                                            </div>

                                        </div>

                                        <div className="cart-item-right">

                                            <strong>{item.price}</strong>

                                            <button
                                                onClick={() => removeProduct(index)}
                                            >
                                                Eliminar
                                            </button>

                                        </div>

                                    </div>

                                ))
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

                                <strong>${total.toLocaleString()}</strong>

                            </div>

                            <button className="save-budget-btn">

                                Guardar lista

                            </button>

                        </div>

                    </div>

                )
            }

        </section>

    )
}

export default Cart
