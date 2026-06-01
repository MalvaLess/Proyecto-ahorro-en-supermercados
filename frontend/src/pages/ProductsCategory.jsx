import './ProductsCategory.css'
import products from '../data/products'
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



    const categoryProducts = products.filter(
        product => product.category === category
    )
    const filteredProducts = categoryProducts.filter(product =>
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