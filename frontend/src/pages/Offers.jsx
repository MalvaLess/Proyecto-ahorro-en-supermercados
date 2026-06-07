import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { apiRequest } from '../services/apiClient'
import './Products.css'

function Offers() {
  const [searchParams, setSearchParams] = useSearchParams()
  const currentPage = parseInt(searchParams.get('page') || '1')

  const [products, setProducts] = useState([])
  const [pagination, setPagination] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function formatPrice(value, currency) {
    if (value === null || value === undefined) return 'Sin precio'
    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency: currency || 'UYU',
      maximumFractionDigits: 0
    }).format(value)
  }

  function buildProduct(raw) {
    const priceItems = raw.items || []
    const prices = priceItems.map((item, index) => ({
      market: item.storeChainName,
      price: formatPrice(item.finalPrice, item.currency),
      normalPrice: formatPrice(item.price, item.currency),
      hasOffer: item.hasOffer,
      isBestPrice: index === 0,
      storeProductId: item.storeProductId,
      ocaPrice: item.ocaPrice != null ? formatPrice(item.ocaPrice, item.currency) : null
    }))

    const validPrices = priceItems
      .filter(item => item.finalPrice !== null && item.finalPrice !== undefined)
      .map(item => item.finalPrice)
    const maxPrice = validPrices.length > 0 ? Math.max(...validPrices) : null
    const minPrice = validPrices.length > 0 ? Math.min(...validPrices) : null
    const saving = maxPrice && minPrice ? maxPrice - minPrice : 0

    return {
      ...raw,
      prices,
      availableStores: prices.length,
      saving: formatPrice(saving, priceItems[0]?.currency || 'UYU')
    }
  }

  async function loadOffers(page) {
    try {
      setLoading(true)
      setError('')
      const response = await apiRequest(`/price-comparison/offers?page=${page}&perPage=40`)
      setProducts((response.data || []).map(buildProduct))
      setPagination(response.pagination)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOffers(currentPage)
  }, [currentPage])

  function handlePreviousPage() {
    if (currentPage <= 1) return
    setSearchParams({ page: String(currentPage - 1) })
  }

  function handleNextPage() {
    if (!pagination || currentPage >= pagination.totalPages) return
    setSearchParams({ page: String(currentPage + 1) })
  }

  return (
    <section className="products-page">

      <div className="products-header">
        <h1>Ofertas</h1>
      </div>

      <div className="search-results">

        {loading && (
          <p className="results-subtitle">Cargando ofertas...</p>
        )}

        {error && (
          <div className="no-results">{error}</div>
        )}

        {!loading && !error && (
          <>
            <p className="results-subtitle">
              {pagination?.totalItems || 0} productos en oferta
            </p>

            {products.length > 0 ? (
              <>
                <div className="search-products-grid">
                  {products.map(product => (
                    <ProductCard key={product.productId} product={product} />
                  ))}
                </div>

                {pagination && pagination.totalPages > 1 && (
                  <div className="products-pagination">
                    <button
                      type="button"
                      onClick={handlePreviousPage}
                      disabled={currentPage <= 1}
                    >
                      Anterior
                    </button>

                    <span className="pagination-info">
                      Página {pagination.page} de {pagination.totalPages}
                    </span>

                    <button
                      type="button"
                      onClick={handleNextPage}
                      disabled={currentPage >= pagination.totalPages}
                    >
                      Siguiente
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="no-results">No hay ofertas disponibles.</div>
            )}
          </>
        )}

      </div>

    </section>
  )
}

export default Offers
