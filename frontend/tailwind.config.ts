import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ps: {
          canvas: "#FBF8F1",
          "canvas-raised": "#F2F7FC",
          surface: "#FFFFFF",
          "surface-strong": "#EAF4FB",
          control: "#F7FAFD",
          border: "#C9DCE8",
          "border-strong": "#8FB7CE",
          "text-primary": "#10233A",
          "text-secondary": "#405A73",
          "text-muted": "#61758A",
          accent: "#5FA8D3",
          "accent-strong": "#3D7BA1",
          "accent-hover": "#346F91",
          "accent-soft": "#EAF4FB",
          success: "#18794E",
          info: "#236F9D",
          warning: "#8A5A00",
          neutral: "#596A7A",
        },
      },
    },
  },
  plugins: [],
};

export default config;
