import type { Metadata } from "next";
import { Cormorant_SC, Poppins } from "next/font/google";
import "./globals.css";

const cormorantSC = Cormorant_SC({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

export const metadata: Metadata = {
  title: "TanLaw Advisory",
  description: "Internal document assistant for TanLaw Advisory",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${cormorantSC.variable} ${poppins.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
