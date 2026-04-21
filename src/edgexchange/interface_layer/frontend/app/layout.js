import "./globals.css";
import { SessionProvider } from "@/context/SessionContext";
import { PortfolioProvider } from "@/context/PortfolioContext";
import { Toaster } from "@/components/ui/toaster";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <SessionProvider>
          <PortfolioProvider>
            <Toaster />
            {children}
          </PortfolioProvider>
        </SessionProvider>
      </body>
    </html>
  );
}