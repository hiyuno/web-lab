import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Listen on localhost (IPv4 and IPv6) so the browser preview can reach it either way.
export default defineConfig({ plugins: [react()], server: { host: 'localhost' } })
