import './ProductDetail.css'
import products from '../data/products'
import { Link, useParams } from 'react-router-dom'
import { useState } from 'react'

function ProductDetail({ cart, setCart }) {

    const { id } = useParams()

    const product = products.find(
        item => item.slug === id
    )

    const [selectedMarket, setSelectedMarket] = useState(null)

    const addToCart = () => {

        if (!selectedMarket) return

        const productToAdd = {

            slug: product.slug,

            name: product.name,

            image: product.image,

            market: selectedMarket.market,

            price: selectedMarket.price

        }

        const existingProduct = cart.find(
            item => item.slug === product.slug
        )

        if (existingProduct) {

            const updatedCart = cart.map(item =>

                item.slug === product.slug
                    ? productToAdd
                    : item

            )

            setCart(updatedCart)

        } else {

            setCart([...cart, productToAdd])

        }
    }

    return (

        <section className="product-detail-page">

            <div className="product-detail-container">

                <div className="product-left-column">

                    <div className="back-links">
                        <Link to={`/products/${product.category}`}>
                            ← Volver a {product.category}
                        </Link>
                    </div>

                    <div className="product-header">


                        <h1>{product.name}</h1>

                        <p className="product-description">
                            {product.description}
                        </p>

                    </div>

                    <div className="product-image-card">

                        <img
                            src={product.image}
                            alt={product.name}
                        />

                    </div>

                </div>

                <div className="product-right-column">

                    <div className="availability-box">
                        🛒 Disponible en {product.prices.length} supermercados
                    </div>

                    <div className="markets-section">

                        <div className="markets-header">

                            <h3>Selecciona el supermercado que prefieras</h3>

                            <span>
                                
                            </span>

                        </div>

                        {
                            product.prices.map((item, index) => (

                                <div
                                    className={
                                        selectedMarket?.market === item.market
                                            ? 'market-card selected'
                                            : 'market-card'
                                    }
                                    key={index}
                                    onClick={() => setSelectedMarket(item)}
                                >

                                    <div className="market-left">

                                        <span>{item.market}</span>

                                        {
                                            index === 0 && (
                                                <small>
                                                    Mejor precio
                                                </small>
                                            )
                                        }

                                    </div>

                                    <strong>{item.price}</strong>

                                </div>

                            ))
                        }

                    </div>


                    <button
                        className="add-cart-btn"
                        onClick={addToCart}
                    >
                        Agrega producto a tu lista
                    </button>

                </div>

            </div>

        </section>
    )
}

export default ProductDetail