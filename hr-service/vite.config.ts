import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import proxyOptions from "./proxyOptions";

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react(), tailwindcss()],
	server: {
		port: 8080,
		proxy: proxyOptions,
		hmr: {
			overlay: false,
		},
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
		},
	},
	build: {
		outDir: "../common/public/hr-service",
		emptyOutDir: true,
		target: "es2015",
	},
});
