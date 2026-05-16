import type { Metadata } from "next";
import { Inter, Crimson_Pro } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: '--font-inter',
});

const crimsonPro = Crimson_Pro({
  subsets: ["latin"],
  variable: '--font-crimson',
});

export const metadata: Metadata = {
  title: "Prefrontal — Evolutionary Psychology Explainer",
  description: "Trace modern human fears, behaviors, and quirks back to their ancestral survival origins.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${crimsonPro.variable}`}>
        {children}
      </body>
    </html>
  );
}
