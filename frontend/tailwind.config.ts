import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(220 20% 98%)",
        foreground: "hsl(222 40% 11%)",
        border: "hsl(224 22% 88%)",
        card: "rgba(255,255,255,0.84)",
        primary: "hsl(233 91% 65%)",
        secondary: "hsl(227 44% 96%)",
        muted: "hsl(223 26% 92%)",
      },
      boxShadow: {
        glow: "0 24px 80px rgba(65, 88, 255, 0.16)",
      },
      backgroundImage: {
        "hero-grid":
          "radial-gradient(circle at top left, rgba(91, 122, 255, 0.22), transparent 25%), radial-gradient(circle at 80% 0%, rgba(144, 84, 255, 0.20), transparent 28%), linear-gradient(180deg, rgba(255,255,255,0.96), rgba(240,244,255,0.94))",
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
