import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AUGUST — Decision Intelligence",
  applicationName: "AUGUST",
  description: "From raw signals to decisions.",
  icons: {
    icon: [{ url: "/august-icon.svg", type: "image/svg+xml" }],
    shortcut: "/august-icon.svg",
    apple: "/august-icon.svg"
  }
};

export const viewport: Viewport = {
  themeColor: "#FF5600",
  colorScheme: "dark"
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
