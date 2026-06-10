import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "ContractIQ — AI-Powered Contract Intelligence",
  description:
    "Transform contracts from static legal documents into actionable business intelligence. Upload, analyze, and identify risks automatically.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider appearance={{ baseTheme: dark }}>
      <html lang="en" className="dark">
        <body className={`${inter.variable} font-sans antialiased bg-slate-950 text-slate-100`}>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
