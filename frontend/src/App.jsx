import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Products from './pages/Products'
import Offers from './pages/Offers'
import About from './pages/About'
import Login from './pages/Login'
import ProductsCategory from './pages/ProductsCategory'

function App() {

  return (

    <BrowserRouter>

      <Navbar />

      <Routes>

        <Route path="/" element={<Home />} />

        <Route path="/products" element={<Products />} />

        <Route path="/offers" element={<Offers />} />

        <Route path="/about" element={<About />} />

        <Route path="/login" element={<Login />} />

        <Route path="/products/:category"element={<ProductsCategory />}/>



      </Routes>

    </BrowserRouter>
  )
}

export default App