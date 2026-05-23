import CategoriesSection from '../components/Categories'
import FeaturedProducts from '../components/FeaturedProducts'
import { useState } from 'react'
import ProductCard from '../components/ProductCard'
import products from '../data/products'
import './Products.css'
import { FiSearch } from 'react-icons/fi'

function Products() {

  const [search, setSearch] = useState('')

  const filteredProducts = products.filter(product =>

    product.name
      .toLowerCase()
      .includes(search.toLowerCase())

  )

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
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <button>
            <FiSearch />
          </button>

        </div>

      </div>

      {
        search.length > 0 && (

          <div className="search-results">

            <h2 className="results-title">

              Resultados para: "{search}"

            </h2>

            <p className="results-subtitle">

              {filteredProducts.length} productos encontrados

            </p>

            {
              filteredProducts.length > 0 ? (

                <div className="search-products-grid">

                  {
                    filteredProducts.map(product => (

                      <ProductCard
                        key={product.id}
                        product={product}
                      />

                    ))
                  }

                </div>

              ) : (

                <div className="no-results">

                  No se encontraron productos.

                </div>

              )
            }

          </div>

        )
      }

      <CategoriesSection />

      <FeaturedProducts />

    </section>
  )
}

export default Products