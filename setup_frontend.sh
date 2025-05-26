#!/bin/bash

mkdir frontend
npm create vite@latest ./frontend -- --template react
cd frontend

npm install -D tailwindcss@3 postcss autoprefixer

npx tailwindcss init -p

cat > tailwind.config.js <<EOL
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOL

cat > src/index.css <<EOL
@tailwind base;
@tailwind components;
@tailwind utilities;
EOL

cat > src/App.jsx <<EOL
export default function App() {
  return (
    <h1 className="text-3xl font-bold underline">
      Hello world!
    </h1>
  )
}
EOL

rm -rf src/assets
rm src/App.css


echo "Frontend setup completed with TailwindCSS and React!"



cd ..