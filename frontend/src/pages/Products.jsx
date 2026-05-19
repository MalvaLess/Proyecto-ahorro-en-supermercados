import CategoriesSection from '../components/Categories'
import FeaturedProducts from '../components/FeaturedProducts'
import './Products.css'
import { FiSearch } from 'react-icons/fi'

function Products() {

  return (

    <section className="products-page">

      <div className="products-header">

        <h1>Encuentra los mejores precios</h1>

        <div className="search-box">

          <div className="search-icon-left">
            <FiSearch />
          </div>

          <input
            type="text"
            placeholder="Buscar productos (ej. leche, arroz, frutas...)"
          />

          <button>
            <FiSearch />
          </button>

        </div>

        <p className="products-description">
          Compara productos entre supermercados y ahorra en tus compras.
        </p>

      </div>

      <CategoriesSection />

      <FeaturedProducts />

    </section>
  )
}

export default Products