import { createContext, useContext, useState, useEffect } from 'react'
import { apiRequest } from '../services/apiClient'
import { isAuthenticated } from '../services/authService'

const FavoritesContext = createContext({ favoriteIds: new Set(), toggleFavorite: () => {} })

export function FavoritesProvider({ children }) {
  const [favoriteIds, setFavoriteIds] = useState(new Set())

  async function fetchFavorites() {
    if (!isAuthenticated()) {
      setFavoriteIds(new Set())
      return
    }
    try {
      const response = await apiRequest('/favorites/')
      setFavoriteIds(new Set(response.data.map(f => f.productId)))
    } catch {
      setFavoriteIds(new Set())
    }
  }

  useEffect(() => {
    fetchFavorites()
    window.addEventListener('auth-change', fetchFavorites)
    return () => window.removeEventListener('auth-change', fetchFavorites)
  }, [])

  async function toggleFavorite(productId) {
    if (!isAuthenticated()) {
      alert('Debes iniciar sesión para agregar a favoritos')
      return
    }

    const isFav = favoriteIds.has(productId)

    setFavoriteIds(prev => {
      const next = new Set(prev)
      isFav ? next.delete(productId) : next.add(productId)
      return next
    })

    try {
      if (isFav) {
        await apiRequest(`/favorites/products/${productId}`, { method: 'DELETE' })
      } else {
        await apiRequest('/favorites/', {
          method: 'POST',
          body: JSON.stringify({ productId })
        })
      }
    } catch {
      setFavoriteIds(prev => {
        const next = new Set(prev)
        isFav ? next.add(productId) : next.delete(productId)
        return next
      })
      alert('Error al actualizar favoritos')
    }
  }

  return (
    <FavoritesContext.Provider value={{ favoriteIds, toggleFavorite }}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavorites() {
  return useContext(FavoritesContext)
}
