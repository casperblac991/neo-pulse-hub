import { trpc } from "@/lib/trpc";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Search, BookOpen, ArrowLeft, Loader2, RefreshCw,
  Clock, Globe, Sparkles, TrendingUp, ExternalLink,
} from "lucide-react";
import { useMemo, useState } from "react";

export default function Blogs() {
  const [searchTerm, setSearchTerm] = useState("");
  const [lang, setLang] = useState<"all" | "ar" | "en">("all");

  const blogsQuery = trpc.blogs.list.useQuery(undefined, { retry: 2, staleTime: 5 * 60_000 });
  const blogs = blogsQuery.data ?? [];

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return blogs.filter(b => {
      const matchLang = lang === "all" || b.language === lang;
      const matchQ = !q || b.title.toLowerCase().includes(q) || (b.excerpt ?? "").toLowerCase().includes(q);
      return matchLang && matchQ;
    });
  }, [blogs, searchTerm, lang]);

  const arCount = blogs.filter(b => b.language === "ar").length;
  const enCount = blogs.filter(b => b.language === "en").length;

  return (
    <div dir="rtl" className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/70 backdrop-blur sticky top-0 z-40">
        <div className="container flex items-center justify-between gap-4 py-4">
          <div className="flex items-center gap-3">
            <a href="/" className="text-muted-foreground hover:text-primary transition-colors">
              <ArrowLeft className="h-5 w-5" />
            </a>
            <div>
              <h1 className="text-xl font-bold">الأدلة والمقارنات</h1>
              <p className="text-xs text-muted-foreground">{blogs.length} مقال · عربي وإنجليزي</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="text-primary font-semibold">{arCount}</span> عربي
            <span>·</span>
            <span className="text-blue-400 font-semibold">{enCount}</span> إنجليزي
          </div>
        </div>
      </header>

      <main className="container space-y-6 py-6">
        {/* SEO note */}
        <div className="flex items-start gap-3 rounded-xl border border-green-500/20 bg-green-500/5 p-4 text-sm">
          <TrendingUp className="h-5 w-5 text-green-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-green-400">محتوى مُحسَّن للبحث (SEO)</p>
            <p className="text-muted-foreground text-xs mt-1">
              كل مقال يستهدف كلمات مفتاحية بحثية — الزوار من Google يتحولون لعملاء عبر روابط الأفيليت.
            </p>
          </div>
        </div>

        {/* Search + lang filter */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute right-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              dir="rtl"
              placeholder="ابحث في المقالات..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pr-10 input-neon"
            />
          </div>
          <div className="flex gap-2">
            {([
              { key: "all", label: `الكل (${blogs.length})` },
              { key: "ar",  label: `🇸🇦 عربي (${arCount})` },
              { key: "en",  label: `🇬🇧 English (${enCount})` },
            ] as const).map(({ key, label }) => (
              <Button key={key} size="sm" variant={lang === key ? "default" : "outline"} onClick={() => setLang(key)}>
                {label}
              </Button>
            ))}
          </div>
        </div>

        {/* Loading */}
        {blogsQuery.isLoading && (
          <div className="flex items-center justify-center gap-3 py-16 text-muted-foreground">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <p>جارٍ تحميل المقالات...</p>
          </div>
        )}

        {/* Error */}
        {blogsQuery.isError && (
          <Card className="mx-auto max-w-md p-8 text-center">
            <RefreshCw className="mx-auto h-8 w-8 text-destructive mb-3" />
            <p className="font-semibold">تعذر تحميل المقالات</p>
            <Button className="mt-4" onClick={() => blogsQuery.refetch()}>إعادة المحاولة</Button>
          </Card>
        )}

        {/* Empty */}
        {!blogsQuery.isLoading && !blogsQuery.isError && filtered.length === 0 && (
          <Card className="mx-auto max-w-md p-10 text-center">
            <BookOpen className="mx-auto h-10 w-10 text-muted-foreground mb-3" />
            <p className="font-semibold">لا توجد مقالات مطابقة</p>
            <p className="text-sm text-muted-foreground mt-1">جرّب كلمة بحث أخرى أو غيّر اللغة</p>
          </Card>
        )}

        {/* Blogs grid */}
        {!blogsQuery.isLoading && !blogsQuery.isError && filtered.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((blog, i) => (
              <Card key={(blog as any).id ?? i} className="group border-primary/15 bg-card/80 overflow-hidden transition hover:-translate-y-1 hover:border-primary/50">
                {(blog as any).image && (
                  <div className="overflow-hidden">
                    <img
                      src={(blog as any).image}
                      alt={blog.title}
                      className="h-40 w-full object-cover transition-transform duration-300 group-hover:scale-105"
                      loading="lazy"
                      onError={e => { e.currentTarget.style.display = "none"; }}
                    />
                  </div>
                )}
                <CardContent className="p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {blog.language === "ar" ? "🇸🇦 عربي" : "🇬🇧 English"}
                    </Badge>
                    {(blog as any).category && (
                      <Badge className="text-xs bg-primary/15 text-primary border-primary/20">
                        {(blog as any).category}
                      </Badge>
                    )}
                  </div>
                  <h2 className="font-bold leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                    {blog.title}
                  </h2>
                  {(blog as any).excerpt && (
                    <p className="text-xs leading-5 text-muted-foreground line-clamp-3">
                      {(blog as any).excerpt}
                    </p>
                  )}
                  {(blog as any).url ? (
                    <Button asChild variant="outline" size="sm" className="w-full gap-2">
                      <a href={(blog as any).url} target="_blank" rel="noreferrer noopener">
                        قراءة المقال <ExternalLink className="h-3 w-3" />
                      </a>
                    </Button>
                  ) : (blog as any).slug ? (
                    <Button asChild variant="outline" size="sm" className="w-full">
                      <a href={`/blogs/${(blog as any).slug}`}>قراءة المقال</a>
                    </Button>
                  ) : null}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
