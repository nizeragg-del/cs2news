import { supabase } from "@/lib/supabase";
import Link from "next/link";

export const revalidate = 60; // Revalidate every minute

export default async function Home() {
  const { data: posts, error } = await supabase
    .from("posts")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching posts:", error);
  }

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative h-[400px] rounded-3xl overflow-hidden glass-card group">
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent z-10" />
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center group-hover:scale-105 transition-transform duration-700 opacity-60" />

        <div className="absolute bottom-0 left-0 p-8 md:p-12 z-20 max-w-2xl">
          <span className="px-3 py-1 bg-primary text-background font-black text-xs uppercase tracking-widest rounded mb-4 inline-block">
            DESTAQUE
          </span>
          <h1 className="text-4xl md:text-6xl font-black uppercase tracking-tighter mb-4 leading-none">
            O Futuro do <span className="gradient-text italic">CS2</span> é Agora.
          </h1>
          <p className="text-muted text-lg font-medium leading-relaxed mb-6">
            Acompanhe as principais mudanças, transferências e o cenário competitivo global em tempo real.
          </p>
        </div>
      </section>

      {/* Posts Grid */}
      <section>
        <div className="flex justify-between items-end mb-8">
          <div>
            <h2 className="text-3xl font-black uppercase tracking-tighter">Últimas <span className="text-primary italic">Notícias</span></h2>
            <p className="text-muted font-medium">Atualizado há poucos minutos</p>
          </div>
          <div className="flex gap-2">
            {["Todos", "Torneios", "Transferências"].map((cat) => (
              <button key={cat} className="px-4 py-2 rounded-full border border-white/5 bg-white/5 hover:bg-primary hover:text-background transition-all text-xs font-bold uppercase tracking-wider">
                {cat}
              </button>
            ))}
          </div>
        </div>

        {posts && posts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post) => (
              <Link href={`/post/${post.id}`} key={post.id} className="glass-card rounded-2xl overflow-hidden flex flex-col group">
                <div className="relative aspect-video overflow-hidden">
                  <img
                    src={post.image_url || "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=2070&auto=format&fit=crop"}
                    alt={post.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute top-4 left-4">
                    <span className="px-2 py-1 bg-background/80 backdrop-blur-md text-[10px] font-bold uppercase tracking-widest rounded border border-white/10">
                      {post.category || "Notícia"}
                    </span>
                  </div>
                </div>
                <div className="p-6 flex-1 flex flex-col">
                  <h3 className="text-xl font-bold leading-tight mb-3 group-hover:text-primary transition-colors line-clamp-2">
                    {post.title}
                  </h3>
                  <p className="text-muted text-sm line-clamp-2 mb-6 flex-1">
                    {post.excerpt}
                  </p>
                  <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-muted mt-auto">
                    <span>{new Date(post.created_at).toLocaleDateString("pt-BR")}</span>
                    <span className="flex items-center gap-1 group-hover:text-primary transition-colors">
                      Ler Mais →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="py-20 text-center glass-card rounded-3xl border-dashed border-2 border-white/5">
            <div className="text-4xl mb-4 text-muted/20 italic font-black">SEM NOTÍCIAS AINDA</div>
            <p className="text-muted max-w-sm mx-auto">
              O motor de automação está sendo aquecido. Em breve, as últimas da HLTV aparecerão aqui.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
