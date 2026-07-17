/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        md: '1.25rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '2.5rem',
      },
      screens: {
        sm: '640px',
        md: '900px',
        lg: '1200px',
        xl: '1536px',
        '2xl': '1920px',
      },
    },
    extend: {
      colors: {
        primary: '#005BFF',
        secondary: '#FFD400',
        background: '#F5F8FD',
        card: '#FFFFFF',
        text: '#111827',
        'secondary-text': '#6B7280',
        border: '#E5E7EB',
        success: '#16A34A',
        danger: '#EF4444',
        warning: '#F59E0B',
      },
      fontFamily: {
        sans: ['"Be Vietnam Pro"', 'sans-serif'],
      },
      boxShadow: {
        hero: '0 20px 60px rgba(0,0,0,.08)',
        card: '0 8px 24px rgba(15,23,42,.08)',
        hover: '0 20px 40px rgba(0,91,255,.15)',
        button: '0 10px 20px rgba(0,91,255,.25)',
      },
      borderRadius: {
        hero: '32px',
        card: '24px',
        button: '18px',
        input: '18px',
        badge: '999px',
        product: '20px',
        category: '18px',
      }
    },
  },
  plugins: [],
}
