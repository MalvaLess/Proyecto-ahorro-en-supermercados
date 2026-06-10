import { Link } from 'react-router-dom'
import './Hero.css'
import heroImage from '../assets/ChatGPT Image 9 may 2026, 22_42_52.png'

function Hero() {
    return (
        <section className="hero">

            <div className="hero-container">
                <div className="hero-image">
                    <img
                        src={heroImage}
                        alt="Pareja comparando precios"
                    />
                </div>

                <div className="hero-text">
                    <h1>Compara precios y <br />
                        AHORRA</h1>

                    <p>
                        Encuentra las mejores ofertas y administra <br />mejor tus compras.
                    </p>

                    <Link to="/products"><button>Comenzar</button></Link>
                </div>



            </div>

        </section>
    )
}

export default Hero