import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPrefixes = [
  "/profile",
  "/upcycle",
  "/projects",
  "/inventory",
  "/marketplace/sell",
];

const publicPaths = ["/", "/login", "/marketplace"];

function isProtected(pathname: string): boolean {
  if (publicPaths.some((p) => pathname === p)) return false;
  if (pathname.startsWith("/marketplace/") && !pathname.startsWith("/marketplace/sell")) {
    return false;
  }
  return protectedPrefixes.some((prefix) => pathname.startsWith(prefix));
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (!isProtected(pathname)) {
    return NextResponse.next();
  }

  const authSession = request.cookies.get("reverie_auth")?.value;
  if (authSession === "1") {
    return NextResponse.next();
  }

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("returnTo", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: [
    "/profile/:path*",
    "/upcycle/:path*",
    "/projects/:path*",
    "/inventory/:path*",
    "/marketplace/sell/:path*",
  ],
};
