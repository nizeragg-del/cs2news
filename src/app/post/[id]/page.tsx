import { supabase } from "@/lib/supabase";
import { notFound } from "next/navigation";
import Link from "next/link";

export default async function PostPage(props: { params: Promise<{ id: string }> }) {
    const params = await props.params;
    const { data: post, error } = await supabase
        .from("posts")
        .select("*")
        .eq("id", params.id)
        .single();

    if (error || !post) {
        return notFound();
    }

    return (
        <div className="max-w-4xl mx-auto py-12">
            <Link href="/" className="inline-flex items-center text-sm font-bold uppercase tracking-widest text-muted hover:text-primary transition-colors mb-8">
                ← Voltar para Notícias
            </Link>

            <article className="glass-card rounded-3xl overflow-hidden">
                <div className="relative aspect-video w-full overflow-hidden">
                    <img
                        src={post.image_url || "https://images.unsplash.com/photo-1542751371-adc38448a05e"}
                        alt={post.title}
                        className="w-full h-full object-cover"
                        referrerPolicy="no-referrer"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent" />
                </div>

                <div className="p-8 md:p-12 -mt-20 relative z-10">
                    <div className="flex items-center gap-4 mb-6">
                        <span className="px-3 py-1 bg-primary text-background font-black text-xs uppercase tracking-widest rounded inline-block">
                            {post.category || "NOTÍCIA"}
                        </span>
                        <span className="text-xs font-bold uppercase tracking-widest text-muted">
                            {new Date(post.created_at).toLocaleDateString("pt-BR")}
                        </span>
                    </div>

                    <h1 className="text-4xl md:text-6xl font-black uppercase tracking-tighter mb-8 leading-tight italic">
                        {post.title}
                    </h1>

                    <div className="prose prose-invert max-w-none text-muted leading-relaxed text-lg whitespace-pre-wrap">
                        {post.content}
                    </div>
                </div>
            </article>
        </div>
    );
}
