import './Categories.css'

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest } from '../services/apiClient'

function CategoriesSection() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const categoryIcons = {
    'Almacén': '🛒',
    'Bebidas': '🥤',
    'Congelados': '🧊',
    'Frescos': '🥬',
    'Limpieza': '🧴'
  }

  useEffect(() => {
    async function loadCategories() {
      try {
        setLoading(true)
        setError('')

        const response = await apiRequest('/categories/')

        setCategories(response.data)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    loadCategories()
  }, [])

  return (
    <section className="categories-section">
      <h2>Categorías</h2>

      <p>
        Compara precios entre supermercados y encuentra la mejor opción.
      </p>

      {loading && <p>Cargando categorías...</p>}

      {error && <p className="categories-error">{error}</p>}

      {!loading && !error && (
        <div className="categories-grid">
          {
            categories.map((category) => (
              <Link
                to={`/products?categoryId=${category.categoryId}`}
                className="category-card"
                key={category.categoryId}
              >
                <span className="category-icon">
                  {categoryIcons[category.name] || '🛍️'}
                </span>

                <h3>
                  {category.name}
                </h3>
              </Link>
            ))
          }
        </div>
      )}
    </section>
  )
}

export default CategoriesSection