import './Categories.css'

import { Link } from 'react-router-dom'

function CategoriesSection() {

    const categories = [

        {
            name: 'Lacteos',
            icon: '🥛'
        },

        {
            name: 'Verduras',
            icon: '🍅'
        },

        {
            name: 'Carnes',
            icon: '🍖'
        },

        {
            name: 'Panaderia',
            icon: '🍞'
        },

        {
            name: 'Bebidas',
            icon: '🥤'
        },

        {
            name: 'Aseo',
            icon: '🧴'
        }

    ]

    return (

        <section className="categories-section">

            <h2>Categorías</h2>
            <p>
                Compara precios entre supermercados y encuentra la mejor opción.
            </p>

            <div className="categories-grid">

                {
                    categories.map((category, index) => (

                        <Link
                            to={`/products/${category.name.toLowerCase()}`}
                            className="category-card"
                            key={index}
                        >

                            <span className="category-icon">
                                {category.icon}
                            </span>

                            <h3>
                                {category.name}
                            </h3>

                        </Link>

                    ))
                }

            </div>

        </section>
    )
}

export default CategoriesSection

