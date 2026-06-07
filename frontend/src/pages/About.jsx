import './About.css'
import {
    FaReact,
    FaDocker
} from 'react-icons/fa'

import {
    SiFlask,
    SiPostgresql
} from 'react-icons/si'

function About() {

    return (

        <section className="about-page">
            <div className="about-hero">
                <span className="about-badge">
                    Proyecto académico
                </span>

                <h1>

                    Compara precios.
                    <br />
                    Ahorra más.

                </h1>

                <p>
                    Proyecto Ahorro en Supermercados permite comparar
                    productos entre diferentes cadenas para ayudar a los
                    usuarios a tomar mejores decisiones de compra.
                </p>

            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <h2>4+</h2>
                    <span>Supermercados</span>
                </div>

                <div className="stat-card">
                    <h2>500+</h2>
                    <span>Productos</span>
                </div>

                <div className="stat-card">
                    <h2>1000+</h2>
                    <span>Comparaciones</span>
                </div>

            </div>

            <div className="mission-section">
                <div className="mission-left">
                    <h2>Nuestra misión</h2>
                    <p>
                        Facilitar la comparación de precios entre
                        supermercados para que los usuarios puedan ahorrar
                        dinero y encontrar la mejor opción disponible en
                        pocos segundos.
                    </p>

                </div>
                <div className="mission-right">
                    <div className="mission-card">
                        <h3>¿Qué hacemos?</h3>
                        <p>
                            Centralizamos información de productos,
                            precios y supermercados para ofrecer una
                            experiencia simple y eficiente.
                        </p>

                    </div>
                </div>
            </div>

            <div className="technologies-section">
                <h2>Tecnologías utilizadas</h2>
                <div className="tech-grid">
                    <div className="tech-card">
                        <FaReact className="tech-icon react" />
                        <span>React</span>
                    </div>

                    <div className="tech-card">
                        <SiFlask className="tech-icon flask" />
                        <span>Flask</span>
                    </div>

                    <div className="tech-card">
                        <SiPostgresql className="tech-icon postgres" />
                        <span>PostgreSQL</span>
                    </div>

                    <div className="tech-card">
                        <FaDocker className="tech-icon docker" />
                        <span>Docker</span>
                    </div>

                </div>

            </div>
            <div className="team-section">
                <h2>Equipo de desarrollo</h2>
                <div className="team-grid">
                    <div className="team-card">
                        <div className="team-avatar">
                            👨‍💻
                        </div>

                        <h3>Tu Nombre</h3>

                        <span>
                            Frontend Developer
                        </span>

                    </div>

                    <div className="team-card">
                        <div className="team-avatar">
                            ⚙️
                        </div>
                        <h3>Maximiliano Malvarez</h3>

                        <span>
                            Backend Developer
                        </span>

                    </div>

                    <div className="team-card">
                        <div className="team-avatar">
                            🗄️
                        </div>
                        <h3>Enzo Soto</h3>
                        <span>
                            Database Developer
                        </span>

                    </div>
                </div>

            </div>

            <div className="about-footer">
                <h2>
                    Construido para ayudar a los consumidores
                    a encontrar mejores precios.
                </h2>
            </div>

        </section>

    )
}

export default About