"use client";

import { useAuth0 } from "@auth0/auth0-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Leaf, LogOut, User } from "lucide-react";
import { useAuthModal } from "@/components/providers/auth-modal-provider";

const navLinks = [
  { href: "/upcycle", label: "Upcycle" },
  { href: "/profile", label: "Profile" },
  { href: "/marketplace", label: "Marketplace" },
];

export function Header() {
  const pathname = usePathname();
  const { isAuthenticated, isLoading, user, logout } = useAuth0();
  const { openAuthModal } = useAuthModal();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary shadow-sm">
            <Leaf className="h-4 w-4 text-primary-foreground" />
          </span>
          <span className="text-xl font-black text-primary">Reverie</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-semibold transition-colors hover:bg-accent/15 hover:text-primary",
                pathname.startsWith(link.href)
                  ? "bg-accent/20 text-primary"
                  : "text-muted-foreground",
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {isLoading ? null : isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full p-0">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={user?.picture} alt={user?.name ?? "User"} />
                    <AvatarFallback>
                      {user?.name?.charAt(0) ?? "U"}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link href="/profile" className="cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="cursor-pointer"
                  onClick={() =>
                    logout({ logoutParams: { returnTo: window.location.origin } })
                  }
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button size="sm" onClick={() => openAuthModal()}>
              Log in
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border bg-primary text-primary-foreground">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2 text-sm text-primary-foreground/80">
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent">
            <Leaf className="h-3.5 w-3.5 text-accent-foreground" />
          </span>
          Reverie — gamified upcycling for a circular wardrobe
        </div>
        <div className="flex gap-6 text-sm font-semibold text-primary-foreground/80">
          <Link href="/marketplace" className="hover:text-primary-foreground">
            Marketplace
          </Link>
          <Link href="/upcycle" className="hover:text-primary-foreground">
            Start Upcycling
          </Link>
        </div>
      </div>
    </footer>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </>
  );
}
