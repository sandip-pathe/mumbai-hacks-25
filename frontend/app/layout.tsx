import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

// Body font - Inter
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600", "700"],
});

// Heading font - Outfit via Google Fonts (avoids shipping local woff2 files)
const outfit = Outfit({
  subsets: ["latin"],
  weight: ["700", "800"],
  variable: "--font-gt-america",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Anaya Watchtower - Compliance Intelligence",
  description: "AI-powered compliance monitoring for Indian fintech",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${outfit.variable} font-sans antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
