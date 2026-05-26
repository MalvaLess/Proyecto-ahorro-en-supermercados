import './Cart.css'

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

            <div className="cart-header">

                <h1>Mi lista</h1>

                <p>
                    Productos seleccionados para comparar presupuesto.
                </p>

            </div>

            {
                cart.length === 0 ? (

                    <div className="empty-cart">

                        <h2>No hay productos en la lista</h2>

                    </div>

                ) : (

                    <>

                        <div className="cart-products">

                            {
                                cart.map((item, index) => (

                                    <div className="cart-card" key={index}>

                                        <img
                                            src={item.image}
                                            alt={item.name}
                                        />

                                        <div className="cart-info">

                                            <h3>{item.name}</h3>

                                            <p>{item.market}</p>

                                        </div>

                                        <strong>{item.price}</strong>

                                        <button
                                            onClick={() => removeProduct(index)}
                                        >
                                            Eliminar
                                        </button>

                                    </div>

                                ))
                            }

                        </div>

                        <div className="cart-total">

                            <h2>
                                Total estimado:
                            </h2>

                            <strong>
                                ${total.toLocaleString()}
                            </strong>

                        </div>

                    </>

                )
            }

        </section>
    )
}

export default Cart