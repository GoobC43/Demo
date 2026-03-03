import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
    optimizeDeps: {
        // Explicitly pre-bundle ALL deps so the optimizer doesn't hang
        // mid-bundling and leave stale deps_temp_* directories
        include: [
            'react',
            'react-dom',
            'react-router-dom',
            'react-is',
            'axios',
            'lucide-react',
            'recharts',
            'qrcode.react',
            'react-plotly.js',
        ],
        // Force re-bundle on every server start to avoid stale cache
        force: true,
    },
})
