import type { Metadata, Viewport } from "next";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "CALPHAD School 2026 · guided self-study",
  description: "Nineteen open steps, 00–18, from Gibbs-energy basics to real Cu–Ni and Ni–Nb calculations and on to how a program proves its equilibrium is the lowest, with an optional LP primer and interactive labs.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f4efe4" },
    { media: "(prefers-color-scheme: dark)", color: "#0f1319" },
  ],
};

// Applies a stored theme choice before first paint; storage failures fall back to the system preference.
const themeScript = `try{var t=localStorage.getItem('calphad-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}catch(e){}document.documentElement.classList.add('js')`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <link rel="preload" href="/fonts/school-serif-400.woff" as="font" type="font/woff" crossOrigin="anonymous" />
        <link rel="preload" href="/fonts/inter-400.woff" as="font" type="font/woff" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
