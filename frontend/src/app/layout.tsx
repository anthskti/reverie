import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/components/providers/auth-provider";
import { ToastProvider } from "@/components/providers/toast-provider";
import { AuthSessionSync } from "@/components/auth/auth-session-sync";
import { AuthErrorHandler } from "@/components/auth/auth-error-handler";
import { AuthModalProvider } from "@/components/providers/auth-modal-provider";
import { AppShell } from "@/components/layout/app-shell";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Reverie — Gamified Upcycling",
  description:
    "Turn old clothes into your next favorite piece. AI-powered upcycling, verification, and marketplace.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <AuthProvider>
          <AuthErrorHandler />
          <AuthSessionSync />
          <AuthModalProvider>
            <AppShell>{children}</AppShell>
            <ToastProvider />
          </AuthModalProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
