import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "CS2 News | O Portal Global de Counter-Strike 2",
  description: "As últimas notícias, transferências e resultados do mundo do CS2 totalmente automatizado.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.variable} ${outfit.variable} antialiased`}>
        <header className="fixed top-0 w-full z-50 glass-card px-6 py-4 flex justify-between items-center border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center font-black text-background text-xl italic">
              CS2
            </div>
            <span className="text-2xl font-black uppercase tracking-tighter">
              HLTV<span className="text-primary italic">REBORN</span>
            </span>
          </div>
          <nav className="hidden md:flex gap-8 text-sm font-bold uppercase tracking-widest text-muted">
            <a href="/" className="hover:text-primary transition-colors">Notícias</a>
            <a href="#" className="hover:text-primary transition-colors">Torneios</a>
            <a href="#" className="hover:text-primary transition-colors">Rankings</a>
            <a href="#" className="hover:text-primary transition-colors">Mercado</a>
          </nav>
          <div className="w-32 flex justify-end">
            <span className="px-3 py-1 bg-accent/20 text-accent rounded-full text-xs font-bold ring-1 ring-accent/30">
              AO VIVO
            </span>
          </div>
        </header>

        <main className="pt-24 min-h-screen container mx-auto px-4 md:px-6">
          {children}
        </main>

        <footer className="mt-20 py-10 border-t border-white/5 text-center text-muted text-sm">
          <p>© 2026 CS2 HLTV REBORN. Powered by Automation and AI.</p>
        </footer>
      </body>
    </html>
  );
}
