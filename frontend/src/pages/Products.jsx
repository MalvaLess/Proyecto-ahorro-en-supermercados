import CategoriesSection from '../components/Categories'
import FeaturedProducts from '../components/FeaturedProducts'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import './Products.css'
import { FiSearch } from 'react-icons/fi'
import { apiRequest } from '../services/apiClient'

function Products() {
  const [searchParams, setSearchParams] = useSearchParams()

  const categoryId = searchParams.get('categoryId')
  const currentSearch = searchParams.get('q') || ''
  const currentPage = parseInt(searchParams.get('page') || '1')

  const [search, setSearch] = useState(currentSearch)
  const [products, setProducts] = useState([])
  const [pagination, setPagination] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const perPage = 20

  // Sincronizar input con URL cuando el usuario presiona atrás
  useEffect(() => {
    setSearch(currentSearch)
  }, [currentSearch])

  function formatPrice(value, currency) {
    if (value === null || value === undefined) {
      return 'Sin precio'
    }

    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency: currency || 'UYU',
      maximumFractionDigits: 0
    }).format(value)
  }

  function buildProductsEndpoint(page, searchValue) {
    let endpoint = `/products?page=${page}&perPage=${perPage}`

    if (categoryId) endpoint += `&categoryId=${categoryId}`

    if (searchValue.trim() !== '') {
      endpoint += `&q=${encodeURIComponent(searchValue.trim())}`
    }

    return endpoint
  }

  function buildProductFromBulk(product, items) {
    const prices = items.map((item, index) => ({
      market: item.storeChainName,
      price: formatPrice(item.finalPrice, item.currency),
      normalPrice: formatPrice(item.price, item.currency),
      hasOffer: item.hasOffer,
      isBestPrice: index === 0,
      storeProductId: item.storeProductId,
      ocaPrice: item.ocaPrice != null ? formatPrice(item.ocaPrice, item.currency) : null
    }))

    const validPrices = items
      .filter(item => item.finalPrice !== null && item.finalPrice !== undefined)
      .map(item => item.finalPrice)

    const maxPrice = validPrices.length > 0 ? Math.max(...validPrices) : null
    const minPrice = validPrices.length > 0 ? Math.min(...validPrices) : null
    const saving = maxPrice && minPrice ? maxPrice - minPrice : 0

    return {
      ...product,
      id: product.productId,
      slug: product.productId,
      image: product.imageURL || 'https://via.placeholder.com/300x220?text=Producto',
      prices,
      availableStores: prices.length,
      saving: formatPrice(saving, items[0]?.currency || 'UYU')
    }
  }

  async function loadProducts(page, searchValue) {
    try {
      setLoading(true)
      setError('')

      const response = await apiRequest(buildProductsEndpoint(page, searchValue))
      const rawProducts = response.data

      if (rawProducts.length === 0) {
        setProducts([])
        setPagination(response.pagination)
        return
      }

      const productIds = rawProducts.map(p => p.productId).join(',')
      const bulkResponse = await apiRequest(`/price-comparison/bulk?productIds=${productIds}`)
      const pricesByProduct = bulkResponse.data

      const productsWithPrices = rawProducts.map(product => {
        const items = pricesByProduct[String(product.productId)] || []
        return buildProductFromBulk(product, items)
      })

      setProducts(productsWithPrices)
      setPagination(response.pagination)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!categoryId && currentSearch === '') {
      setProducts([])
      setPagination(null)
      return
    }
    loadProducts(currentPage, currentSearch)
  }, [currentPage, currentSearch, categoryId])

  function handleSearchSubmit(event) {
    event.preventDefault()
    const cleanSearch = search.trim()

    if (!categoryId && cleanSearch === '') {
      setSearchParams({})
      return
    }

    const params = {}
    if (cleanSearch) params.q = cleanSearch
    if (categoryId) params.categoryId = categoryId
    params.page = '1'
    setSearchParams(params)
  }

  function handlePreviousPage() {
    if (currentPage <= 1) return
    const params = {}
    if (currentSearch) params.q = currentSearch
    if (categoryId) params.categoryId = categoryId
    params.page = String(currentPage - 1)
    setSearchParams(params)
  }

  function handleNextPage() {
    if (!pagination || currentPage >= pagination.totalPages) return
    const params = {}
    if (currentSearch) params.q = currentSearch
    if (categoryId) params.categoryId = categoryId
    params.page = String(currentPage + 1)
    setSearchParams(params)
  }

  const shouldShowResults = categoryId || currentSearch.length > 0

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
                  : `Resultados para: "${currentSearch}"`
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
        !categoryId && currentSearch.length === 0 && (

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