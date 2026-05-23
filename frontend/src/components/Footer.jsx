import './Footer.css'

function Footer() {
    return (
        <footer className="footer">

            <div className="footer-container">

                <div className="footer-brand">
                    <h2>Ahorro Supermercados</h2>

                    <p>
                        Compara precios y encuentra las mejores ofertas cerca de ti.
                    </p>
                </div>

                <div className="footer-links">

                    <div>
                        <h3>Explorar</h3>

                        <ul>
                            <li>Inicio</li>
                            <li>Ofertas</li>
                            <li>Categorías</li>
                        </ul>
                    </div>

                    <div>
                        <h3>Compañía</h3>

                        <ul>
                            <li>Nosotros</li>
                            <li>Contacto</li>
                            <li>Soporte</li>
                        </ul>
                    </div>

                </div>

            </div>

        </footer>
    )
}

export default Footer