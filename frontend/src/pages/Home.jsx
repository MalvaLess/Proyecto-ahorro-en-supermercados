import Navbar from '../components/Navbar'
import Hero from '../components/Hero'
import Features from '../components/Features'
import Products from '../components/FeaturedProducts'
import Categories from '../components/Categories'
import Footer from '../components/Footer'
import HowItWorks from '../components/HowItWorks'

function Home() {
  return (
    <div>

        <Hero />
        <Features />
        <Products />
        <Categories />
        <HowItWorks />
        <Footer/>
        
    

    </div>
  )
}

export default Home