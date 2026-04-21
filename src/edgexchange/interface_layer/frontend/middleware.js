import { NextResponse } from "next/server";

const protectedRoutes = ["/dashboard", "/portfolio", "/execute"];
const authRoutes = ["/login", "/register"];

export function middleware(request) {
  const { pathname } = request.nextUrl;
  const sessionId = request.cookies.get("session_id")?.value;

  // redirect logged-in users away from login/register
  if (authRoutes.includes(pathname) && sessionId) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // redirect unauthenticated users away from protected pages
  if (protectedRoutes.includes(pathname) && !sessionId) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard", "/portfolio", "/execute", "/login", "/register"],
};