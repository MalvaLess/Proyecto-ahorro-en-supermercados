import CategoriesSection from '../components/Categories'
import FeaturedProducts from '../components/FeaturedProducts'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import './Products.css'
import { FiSearch } from 'react-icons/fi'
import { apiRequest } from '../services/apiClient'

function Products() {
  const [searchParams] = useSearchParams()

  const categoryId = searchParams.get('categoryId')

  const [search, setSearch] = useState('')
  const [submittedSearch, setSubmittedSearch] = useState('')
  const [products, setProducts] = useState([])
  const [pagination, setPagination] = useState(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const perPage = 20

  function buildProductsEndpoint(page = 1, searchValue = submittedSearch) {
    let endpoint = `/products?page=${page}&perPage=${perPage}`

    if (categoryId) {
      endpoint += `&categoryId=${categoryId}`
    }

    if (searchValue.trim() !== '') {
      endpoint += `&q=${encodeURIComponent(searchValue.trim())}`
    }

    return endpoint
  }

  function getEndpointFromPaginationUrl(url) {
    if (!url) return null

    const parsedUrl = new URL(url)

    return parsedUrl.pathname.replace('/api', '') + parsedUrl.search
  }

  async function loadProducts(endpoint = null) {
    try {
      setLoading(true)
      setError('')

      const requestEndpoint = endpoint || buildProductsEndpoint(1)

      const response = await apiRequest(requestEndpoint)

      setProducts(response.data)
      setPagination(response.pagination)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (categoryId) {
      setSearch('')
      setSubmittedSearch('')
      loadProducts(buildProductsEndpoint(1, ''))
    }
  }, [categoryId])

  function handleSearchSubmit(event) {
    event.preventDefault()

    const cleanSearch = search.trim()

    setSubmittedSearch(cleanSearch)

    if (!categoryId && cleanSearch === '') {
      setProducts([])
      setPagination(null)
      return
    }

    loadProducts(buildProductsEndpoint(1, cleanSearch))
  }

  function handlePreviousPage() {
    if (!pagination?.previousPage) return

    const endpoint = getEndpointFromPaginationUrl(pagination.previousPage)

    loadProducts(endpoint)
  }

  function handleNextPage() {
    if (!pagination?.nextPage) return

    const endpoint = getEndpointFromPaginationUrl(pagination.nextPage)

    loadProducts(endpoint)
  }

  const shouldShowResults = categoryId || submittedSearch.length > 0

  return (
    <section className="products-page">

      <div className="products-header">

        <h1>Encuentra los mejores precios</h1>

        <form className="search-box" onSubmit={handleSearchSubmit}>

          <div className="search-icon-left">
            <FiSearch />
          </div>

          <input
            type="text"
            placeholder="Buscar productos (ej. leche, arroz, frutas...)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <button type="submit">
            <FiSearch />
          </button>

        </form>

      </div>

      {
        shouldShowResults && (

          <div className="search-results">

            <h2 className="results-title">
              {
                categoryId
                  ? 'Productos de la categoría seleccionada'
                  : `Resultados para: "${submittedSearch}"`
              }
            </h2>

            {
              loading && (
                <p className="results-subtitle">
                  Cargando productos...
                </p>
              )
            }

            {
              error && (
                <div className="no-results">
                  {error}
                </div>
              )
            }

            {
              !loading && !error && (

                <>

                  <p className="results-subtitle">
                    {pagination?.totalItems || 0} productos encontrados
                  </p>

                  {
                    products.length > 0 ? (

                      <>

                        <div className="search-products-grid">

                          {
                            products.map(product => (

                              <ProductCard
                                key={product.productId}
                                product={product}
                              />

                            ))
                          }

                        </div>

                        {
                          pagination && pagination.totalPages > 1 && (

                            <div className="products-pagination">

                              <button
                                type="button"
                                onClick={handlePreviousPage}
                                disabled={!pagination.previousPage}
                              >
                                Anterior
                              </button>

                              <span className="pagination-info">
                                Página {pagination.page} de {pagination.totalPages}
                              </span>

                              <button
                                type="button"
                                onClick={handleNextPage}
                                disabled={!pagination.nextPage}
                              >
                                Siguiente
                              </button>

                            </div>

                          )
                        }

                      </>

                    ) : (

                      <div className="no-results">
                        No se encontraron productos.
                      </div>

                    )
                  }

                </>

              )
            }

          </div>

        )
      }

      {
        !categoryId && submittedSearch.length === 0 && (

          <>

            <CategoriesSection />

            <FeaturedProducts />

          </>

        )
      }

    </section>
  )
}

export default Products