/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ustc: {
          50:  '#e6eef7',
          100: '#c4d8ed',
          200: '#9bbde1',
          300: '#6a9fd3',
          400: '#3d84c3',
          500: '#005BAE',
          600: '#00509a',
          700: '#004383',
          800: '#00366b',
          900: '#002246',
        },
      },
    },
  },
  plugins: [],
}
