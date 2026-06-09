import { useState } from 'react'
import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Products from './pages/Products'
import Offers from './pages/Offers'
import About from './pages/About'
import Login from './pages/Login'
import ProductsCategory from './pages/ProductsCategory'
import Register from './pages/Register'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import ProtectedRoute from './components/ProtectedRoute'
import Account from './pages/Account'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Footer from './components/Footer'
import { FavoritesProvider } from './context/FavoritesContext'




function App() {

  const [cart, setCart] = useState(() => {

    const savedCart = localStorage.getItem('cart')

    return savedCart ? JSON.parse(savedCart) : []

  })

  useEffect(() => {

    localStorage.setItem(
      'cart',
      JSON.stringify(cart)
    )

  }, [cart])

  
  return (

    <BrowserRouter>
    <FavoritesProvider>

      <Navbar cart={cart} />

      <Routes>

        <Route path="/" element={<Home />} />

        <Route path="/products" element={<Products />} />

        <Route path="/offers" element={<Offers />} />

        <Route path="/about" element={<About />} />

        <Route path="/login" element={<Login />} />

        {/* <Route path="/products/:category" element={<ProductsCategory />} /> */}
        <Route path="/products" element={<Products />} />

        <Route path="/register" element={<Register />} />

        <Route path="/forgot-password" element={<ForgotPassword />} />

        <Route path="/reset-password/:token" element={<ResetPassword />} />

        <Route path="/product/:id" element={<ProductDetail cart={cart} setCart={setCart} />} />

        <Route path="/cart" element={<Cart cart={cart} setCart={setCart} />} />

        <Route
          path='/account'
          element={<ProtectedRoute>
            <Account />
          </ProtectedRoute>}
        />

      </Routes>

      <Footer />

    </FavoritesProvider>
    </BrowserRouter>
  )
}

export default App