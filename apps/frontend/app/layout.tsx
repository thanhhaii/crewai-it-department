import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IT Department Command Center",
  description: "Production target application managed by the CrewAI IT department."
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
