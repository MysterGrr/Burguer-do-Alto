/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.{html,js}"],
  theme: {
    //Alteração da fonte padrão para a Poppins
    fontFamily:{
      'sans': ['Poppins', 'sans-serif']
    },
    extend:{
      backgroundImage:{
        "home": "url('/assets/bg.png')"
      }
    },
  },
  plugins: [],
}

