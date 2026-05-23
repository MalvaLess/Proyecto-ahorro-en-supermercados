import './ProductsCategory.css'
import { FiSearch } from 'react-icons/fi'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import lecheImg from '../assets/Sabor_Original_Opt_329b4b6db5.png'
import yogurtGriego from '../assets/627C4B7F7239395D.png!c750x0.jpeg'
import quesoParmesano from '../assets/queso-parmesano-latti-100-g-01.png'
import tomates from '../assets/Fresh-Tomato-PNG-Picture.png'
import lechuga from '../assets/360_F_563197320_gNMb7ZZookMZmYGt0kANZZDmIChNm014.jpg'
import mandarinas from '../assets/images (1).jpeg'



function ProductsCategory() {

    const { category } = useParams()
    const [search, setSearch] = useState('')

    const productsData = {

        lacteos: [

            {
                id: 1,

                slug: 'leche-alpina',

                name: 'Leche Alpina',

                image: lecheImg,

                prices: [
                    { market: 'D1', price: '$4.800' },
                    { market: 'Éxito', price: '$5.200' },
                    { market: 'Ara', price: '$4.950' }
                ]
            },

            {
                id: 2,

                slug: 'yogurt-griego',

                name: 'Yogurt Griego',

                image: yogurtGriego,

                prices: [
                    { market: 'D1', price: '$6.200' },
                    { market: 'Éxito', price: '$6.500' },
                    { market: 'Ara', price: '$6.100' }
                ]
            },

            {
                id: 3,

                slug: 'queso-parmesano',

                name: 'Queso Parmesano',

                image: quesoParmesano,

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

                slug: 'tomates',

                name: 'Tomates',

                image: tomates,

                prices: [
                    { market: 'D1', price: '$2.800' },
                    { market: 'Éxito', price: '$3.100' },
                    { market: 'Ara', price: '$2.950' }
                ]
            },

            {
                id: 2,

                slug: 'lechuga',

                name: 'Lechuga',

                image: lechuga,

                prices: [
                    { market: 'D1', price: '$1.900' },
                    { market: 'Éxito', price: '$2.200' },
                    { market: 'Ara', price: '$2.000' }
                ]
            },

            {
                id: 3,

                slug: 'mandarinas',

                name: 'Mandarinas',

                image: mandarinas,

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
    const filteredProducts = products.filter(product =>
        product.name
            .toLowerCase()
            .includes(search.toLowerCase())
    )

    return (

        <section className="products-category-page">

            <div className="back-links">

                <Link to="/products">

                    ← Productos

                </Link>

            </div>

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
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                <button>
                    <FiSearch />
                </button>

            </div>

            <div className="products-category-grid">

                {
                    filteredProducts.map(product => (

                        <ProductCard
                            key={product.id}
                            product={product}
                        />

                    ))
                }

            </div>

        </section>
    )
}

export default ProductsCategory