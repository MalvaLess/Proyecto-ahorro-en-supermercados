import './ProductsCategory.css'
import { FiSearch } from 'react-icons/fi'
import { useParams } from 'react-router-dom'
import lecheImg from '../assets/Sabor_Original_Opt_329b4b6db5.png'
import yogurtGriego from '../assets/627C4B7F7239395D.png!c750x0.jpeg'

function ProductsCategory() {

    const { category } = useParams()

    const productsData = {

        lacteos: [

            {
                id: 1,
                name: 'Leche Alquería',
                image: lecheImg,
                prices: [
                    { market: 'D1', price: '$4.800' },
                    { market: 'Éxito', price: '$5.200' },
                    { market: 'Ara', price: '$4.950' }
                ]
            },

            {
                id: 2,
                name: 'Yogurt Griego',
                image: yogurtGriego,
                prices: [
                    { market: 'D1', price: '$6.200' },
                    { market: 'Éxito', price: '$6.500' },
                    { market: 'Ara', price: '$6.100' }
                ]
            }

        ],

        verduras: [

            {
                id: 1,
                name: 'Tomate',
                image: 'https://via.placeholder.com/200',
                prices: [
                    { market: 'D1', price: '$2.800' },
                    { market: 'Éxito', price: '$3.100' },
                    { market: 'Ara', price: '$2.950' }
                ]
            },

            {
                id: 2,
                name: 'Lechuga',
                image: 'https://via.placeholder.com/200',
                prices: [
                    { market: 'D1', price: '$1.900' },
                    { market: 'Éxito', price: '$2.200' },
                    { market: 'Ara', price: '$2.000' }
                ]
            }

        ],

        bebidas: [

            {
                id: 1,
                name: 'Coca Cola',
                image: 'https://via.placeholder.com/200',
                prices: [
                    { market: 'D1', price: '$5.000' },
                    { market: 'Éxito', price: '$5.500' },
                    { market: 'Ara', price: '$5.200' }
                ]
            }

        ]

    }

    const products = productsData[category] || []

    return (

        <section className="products-category-page">

            <div className="category-header">

                <h1>{category}</h1>

                <p>
                    Compara precios entre supermercados y encuentra la mejor opción.
                </p>

            </div>

            <div className="search-box">

                <div className="search-icon-left">
                    <FiSearch />
                </div>

                <input
                    type="text"
                    placeholder={`Buscar en ${category}...`}
                />

                <button>
                    <FiSearch />
                </button>

            </div>

            <div className="products-grid">

                {
                    products.map(product => (

                        <div className="product-card" key={product.id}>

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

                        </div>

                    ))
                }

            </div>

        </section>
    )
}

export default ProductsCategory