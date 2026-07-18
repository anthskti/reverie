import type { Metadata } from "next";
import { Nunito, DM_Sans } from "next/font/google";
import { AuthProvider } from "@/components/providers/auth-provider";
import { ToastProvider } from "@/components/providers/toast-provider";
import { AuthSessionSync } from "@/components/auth/auth-session-sync";
import { AuthModalProvider } from "@/components/providers/auth-modal-provider";
import { AppShell } from "@/components/layout/app-shell";
import "./globals.css";

const nunito = Nunito({
  variable: "--font-nunito",
  weight: ["400", "600", "700", "800", "900"],
  subsets: ["latin"],
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  weight: ["400", "500", "600", "700"],
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
      className={`${nunito.variable} ${dmSans.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <AuthProvider>
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
