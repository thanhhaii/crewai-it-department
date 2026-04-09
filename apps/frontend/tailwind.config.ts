import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#f8fafc",
        ink: "#0f172a",
        accent: "#f59e0b",
        mist: "#dbeafe"
      },
      boxShadow: {
        soft: "0 24px 80px rgba(15, 23, 42, 0.14)"
      }
    }
  },
  plugins: []
};

export default config;
