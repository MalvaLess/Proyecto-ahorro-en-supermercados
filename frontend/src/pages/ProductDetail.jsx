import './ProductDetail.css'
import { Link, useParams } from 'react-router-dom'
import { useState } from 'react'
import lecheImg from '../assets/Sabor_Original_Opt_329b4b6db5.png'
import yogurtGriego from '../assets/627C4B7F7239395D.png!c750x0.jpeg'
import quesoParmesano from '../assets/queso-parmesano-latti-100-g-01.png'
import tomates from '../assets/Fresh-Tomato-PNG-Picture.png'
import lechuga from '../assets/360_F_563197320_gNMb7ZZookMZmYGt0kANZZDmIChNm014.jpg'
import mandarinas from '../assets/images (1).jpeg'

function ProductDetail({ cart, setCart }) {

    const { id } = useParams()

    const products = [

        {
            slug: 'leche-alpina',

            category: 'lacteos',

            name: 'Leche Alpina',

            image: lecheImg,

            description:
                'Leche entera ideal para el desayuno y consumo diario.',

            prices: [

                {
                    market: 'D1',
                    price: '$4.800'
                },

                {
                    market: 'Éxito',
                    price: '$5.200'
                },

                {
                    market: 'Ara',
                    price: '$4.950'
                }

            ]
        },

        {
            slug: 'yogurt-griego',

            category: 'lacteos',

            name: 'Yogurt Griego',

            image: yogurtGriego,

            description:
                'Yogurt griego natural alto en proteína.',

            prices: [

                {
                    market: 'D1',
                    price: '$6.200'
                },

                {
                    market: 'Éxito',
                    price: '$6.500'
                },

                {
                    market: 'Ara',
                    price: '$6.100'
                }

            ]
        },

        {
            slug: 'queso-parmesano',

            category: 'lacteos',

            name: 'Queso Parmesano',

            image: quesoParmesano,

            description:
                'Queso parmesano ideal para pastas y comidas italianas.',

            prices: [

                {
                    market: 'D1',
                    price: '$8.500'
                },

                {
                    market: 'Éxito',
                    price: '$8.900'
                },

                {
                    market: 'Ara',
                    price: '$8.300'
                }

            ]
        },

        {
            slug: 'tomates',

            category: 'verduras',

            name: 'Tomates',

            image: tomates,

            description:
                'Tomates frescos seleccionados diariamente.',

            prices: [

                {
                    market: 'D1',
                    price: '$2.800'
                },

                {
                    market: 'Éxito',
                    price: '$3.100'
                },

                {
                    market: 'Ara',
                    price: '$2.950'
                }

            ]
        },

        {
            slug: 'lechuga',

            category: 'verduras',

            name: 'Lechuga',

            image: lechuga,

            description:
                'Lechuga fresca ideal para ensaladas saludables.',

            prices: [

                {
                    market: 'D1',
                    price: '$1.900'
                },

                {
                    market: 'Éxito',
                    price: '$2.200'
                },

                {
                    market: 'Ara',
                    price: '$2.000'
                }

            ]
        },

        {
            slug: 'mandarinas',

            category: 'verduras',

            name: 'Mandarinas',

            image: mandarinas,

            description:
                'Mandarinas dulces y frescas de temporada.',

            prices: [

                {
                    market: 'D1',
                    price: '$1.900'
                },

                {
                    market: 'Éxito',
                    price: '$2.200'
                },

                {
                    market: 'Ara',
                    price: '$2.000'
                }

            ]
        }

    ]

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

            <div className="back-links">

                <Link to={`/products/${product.category}`}>

                    ← Volver a {product.category}

                </Link>

            </div>

            <div className="product-detail-container">

                <div className="product-left">

                    <h1>{product.name}</h1>

                    <p className="product-description">
                        {product.description}
                    </p>

                    <div className="product-image">

                        <img
                            src={product.image}
                            alt={product.name}
                        />

                    </div>

                </div>

                <div className="product-info">

                    <div className="markets-list">

                        <p className="market-helper-text">

                            Compara precios y elige la mejor opción para ti.

                        </p>

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

                                    <span>{item.market}</span>

                                    <strong>{item.price}</strong>

                                </div>

                            ))
                        }

                    </div>

                    <button
                        className="add-cart-btn"
                        onClick={addToCart}
                    >

                        Agregar a mi lista

                    </button>

                </div>

            </div>

        </section>
    )
}

export default ProductDetail
