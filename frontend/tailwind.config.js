/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Urbanist', 'sans-serif'],
                display: ['Outfit', 'sans-serif'],
            },
            colors: {
                nebula: {
                    900: '#0B0E14', // Deep space background
                    800: '#151925', // Panel background
                    700: '#1E2536', // Lighter panel
                    500: '#6366f1', // Primary accent (Indigo)
                    400: '#818cf8', // Highlight
                    300: '#a5b4fc', // Soft accent
                },
                neon: {
                    blue: '#00f0ff',
                    purple: '#b829ea',
                    green: '#0aff68',
                }
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out forwards',
                'shine': 'shine 2s infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'float': 'float 6s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                shine: {
                    '0%': { backgroundPosition: '200% center' },
                    '100%': { backgroundPosition: '-200% center' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                }
            },
            backgroundImage: {
                'nebula-gradient': 'radial-gradient(circle at 50% 0%, #1e2536 0%, #0b0e14 100%)',
                'glass-gradient': 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
                'glow-blue': 'conic-gradient(from 180deg at 50% 50%, #00f0ff33 0deg, transparent 60deg, transparent 300deg, #00f0ff33 360deg)',
            }
        },
    },
    plugins: [],
}
