import lecheImg from '../assets/Sabor_Original_Opt_329b4b6db5.png'
import yogurtGriego from '../assets/627C4B7F7239395D.png!c750x0.jpeg'
import quesoParmesano from '../assets/queso-parmesano-latti-100-g-01.png'
import tomates from '../assets/Fresh-Tomato-PNG-Picture.png'
import lechuga from '../assets/360_F_563197320_gNMb7ZZookMZmYGt0kANZZDmIChNm014.jpg'
import mandarinas from '../assets/images (1).jpeg'

const products = [

    {
        id: 1,

        slug: 'leche-alpina',

        category: 'lacteos',

        name: 'Leche Alpina',

        image: lecheImg,


        prices: [

            {
                market: 'D1',
                price: '$4.800'
            },

            {
                market: 'Éxito',
                price: '$5.200'
            },

            {
                market: 'Ara',
                price: '$4.950'
            }

        ]
    },

    {
        id: 2,

        slug: 'yogurt-griego',

        category: 'lacteos',

        name: 'Yogurt Griego',

        image: yogurtGriego,

        prices: [

            {
                market: 'D1',
                price: '$6.200'
            },

            {
                market: 'Éxito',
                price: '$6.500'
            },

            {
                market: 'Ara',
                price: '$6.100'
            }

        ]
    },

    {
        id: 3,

        slug: 'queso-parmesano',

        category: 'lacteos',

        name: 'Queso Parmesano',

        image: quesoParmesano,


        prices: [

            {
                market: 'D1',
                price: '$8.500'
            },

            {
                market: 'Éxito',
                price: '$8.900'
            },

            {
                market: 'Ara',
                price: '$8.300'
            }

        ]


    },

    {
        id: 4,

        slug: 'tomates',

        category: 'verduras',

        name: 'Tomates',

        image: tomates,

        prices: [

            {
                market: 'D1',
                price: '$2.800'
            },

            {
                market: 'Éxito',
                price: '$3.100'
            },

            {
                market: 'Ara',
                price: '$2.950'
            }

        ]

    },

    {
        id: 5,

        slug: 'lechuga',

        category: 'verduras',

        name: 'Lechuga',

        image: lechuga,

        prices: [

            {
                market: 'D1',
                price: '$1.900'
            },

            {
                market: 'Éxito',
                price: '$2.200'
            },

            {
                market: 'Ara',
                price: '$2.000'
            }

        ]
    },

    {
        id: 6,

        slug: 'mandarinas',

        category: 'verduras',

        name: 'Mandarinas',

        image: mandarinas,


        prices: [

            {
                market: 'D1',
                price: '$1.900'
            },

            {
                market: 'Éxito',
                price: '$2.200'
            },

            {
                market: 'Ara',
                price: '$2.000'
            }

        ]


    }

]

export default products