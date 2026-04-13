/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      colors: {
        bg: '#0a0a0f',
        surface: '#13131a',
        border: '#1e1e2e',
        accent: '#7c6dfa',
        'accent-dim': '#4a3fad',
        success: '#22d3a0',
        danger: '#f06a6a',
        warn: '#f5a524',
        muted: '#6b6b8a',
        text: '#e2e2f0',
      },
    },
  },
  plugins: [],
}
