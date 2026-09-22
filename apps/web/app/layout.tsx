import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AUGUST — Decision Intelligence",
  description: "From raw signals to decisions."
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
