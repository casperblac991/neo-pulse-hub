import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Search, ExternalLink, Loader2, RefreshCw, PackageSearch,
  Sparkles, Star, ArrowLeft, SlidersHorizontal, TrendingUp, Zap,
} from "lucide-react";
import { useMemo, useState, useRef, useEffect } from "react";

const FALLBACK_IMAGE = "https://placehold.co/800x600/0a0d1a/60a5fa?text=NEO+PULSE+HUB";

const CATEGORY_LABELS: Record<string, string> = {
  smartwatch: "⌚ ساعات ذكية", earbuds: "🎧 سماعات", headphones: "🎧 سماعات كبيرة",
  "smart-home": "🏠 منزل ذكي", health: "❤️ صحة ولياقة", productivity: "💼 إنتاجية",
  gaming: "🎮 ألعاب", cameras: "📷 كاميرات", "smart-glasses": "🥽 نظارات ذكية",
  accessories: "🔌 إكسسوار", kitchen: "🍳 مطبخ ذكي", sports: "🏋️ رياضة",
  car: "🚗 سيارة", kids: "👶 أطفال",
};

function displayPrice(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? `$${number.toFixed(2)}` : String(value);
}
function imageUrl(value: unknown) {
  return typeof value === "string" && value.trim() ? value : FALLBACK_IMAGE;
}

// ── AI Search hook ──────────────────────────────────────────────
function useAISearch(query: string, products: any[]) {
  const [aiResults, setAiResults] = useState<any[] | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (query.length < 4) { setAiResults(null); return; }
    timerRef.current = setTimeout(async () => {
      setAiLoading(true);
      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: [{
              role: "user",
              content: `من القائمة التالية من المنتجات، اختر أفضل 6 تناسب طلب المستخدم: "${query}"\n\nالمنتجات (IDs):\n${products.slice(0, 60).map(p => `${p.id}: ${p.title} (${p.category}) $${p.price}`).join("\n")}\n\nأجب بـ JSON فقط: {"ids": ["id1","id2",...]}`
            }],
          }),
        });
        const data = await res.json();
        const text = data.content || data.reply || "";
        const match = text.match(/\{[\s\S]*\}/);
        if (match) {
          const parsed = JSON.parse(match[0]);
          const ids: string[] = parsed.ids || [];
          const filtered = ids.map((id: string) => products.find(p => p.id === id)).filter(Boolean);
          setAiResults(filtered.length > 0 ? filtered : null);
        }
      } catch { setAiResults(null); }
      finally { setAiLoading(false); }
    }, 700);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [query, products.length]);

  return { aiResults, aiLoading };
}

export default function Products() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [sort, setSort] = useState<"default" | "price_asc" | "price_desc" | "rating">("default");
  const [aiMode, setAiMode] = useState(false);

  const productsQuery = trpc.products.all.useQuery(undefined, { retry: 2, staleTime: 5 * 60 * 1000 });
  const products = productsQuery.data ?? [];

  const categories = useMemo(() => {
    const cats = new Set(products.map(p => p.category).filter(Boolean));
    return Array.from(cats).sort();
  }, [products]);

  const { aiResults, aiLoading } = useAISearch(aiMode ? searchTerm : "", products);

  const filteredProducts = useMemo(() => {
    if (aiMode && aiResults) return aiResults;
    const q = searchTerm.trim().toLocaleLowerCase();
    let list = products.filter(p => {
      const title = String(p.title ?? "").toLocaleLowerCase();
      const cat = String(p.category ?? "").toLocaleLowerCase();
      return (!q || title.includes(q) || cat.includes(q)) &&
             (!selectedCategory || p.category === selectedCategory);
    });
    if (sort === "price_asc")  list = [...list].sort((a, b) => Number(a.price) - Number(b.price));
    if (sort === "price_desc") list = [...list].sort((a, b) => Number(b.price) - Number(a.price));
    if (sort === "rating")     list = [...list].sort((a, b) => Number(b.rating) - Number(a.rating));
    return list;
  }, [products, searchTerm, selectedCategory, sort, aiMode, aiResults]);

  return (
    <div dir="rtl" className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/70 backdrop-blur sticky top-0 z-40">
        <div className="container flex items-center justify-between gap-4 py-4">
          <div className="flex items-center gap-3">
            <a href="/" className="text-muted-foreground hover:text-primary transition-colors"><ArrowLeft className="h-5 w-5" /></a>
            <div>
              <h1 className="text-2xl font-bold text-gradient">كتالوج المنتجات</h1>
              <p className="text-xs text-muted-foreground">{products.length} منتج · بيانات حقيقية</p>
            </div>
          </div>
          <Button
            variant={aiMode ? "default" : "outline"}
            size="sm"
            onClick={() => setAiMode(v => !v)}
            className="gap-2"
          >
            <Sparkles className="h-4 w-4" />
            {aiMode ? "بحث AI مفعّل" : "تفعيل بحث AI"}
          </Button>
        </div>
      </header>

      <main className="container space-y-6 py-6">

        {/* Affiliate disclosure */}
        <p className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground">
          قد يحصل Neo Pulse Hub على عمولة عند إتمام عملية شراء مؤهلة عبر بعض الروابط. الدفع والشحن والضمان يتمون لدى المتجر الشريك.
        </p>

        {/* Search + filters */}
        <div className="space-y-3">
          <div className="relative">
            {aiLoading
              ? <Loader2 className="absolute right-3 top-3 h-4 w-4 animate-spin text-primary" />
              : aiMode
                ? <Sparkles className="absolute right-3 top-3 h-4 w-4 text-primary" />
                : <Search className="absolute right-3 top-3 h-4 w-4 text-muted-foreground" />
            }
            <Input
              dir="rtl"
              placeholder={aiMode ? "صف ما تبحث عنه... (AI يفهم العربية)" : "ابحث عن منتج أو فئة..."}
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pr-10 input-neon"
            />
          </div>

          {/* Category filters */}
          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant={selectedCategory === null ? "default" : "outline"} onClick={() => setSelectedCategory(null)}>
              الكل ({products.length})
            </Button>
            {categories.map(cat => (
              <Button key={cat} size="sm" variant={selectedCategory === cat ? "default" : "outline"} onClick={() => setSelectedCategory(cat)}>
                {CATEGORY_LABELS[cat!] ?? cat}
              </Button>
            ))}
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
            {[
              { key: "default", label: "الافتراضي" },
              { key: "price_asc", label: "السعر ↑" },
              { key: "price_desc", label: "السعر ↓" },
              { key: "rating", label: "⭐ الأعلى تقييماً" },
            ].map(({ key, label }) => (
              <Button key={key} size="sm" variant={sort === key ? "default" : "ghost"} onClick={() => setSort(key as any)}>
                {label}
              </Button>
            ))}
          </div>
        </div>

        {/* AI mode indicator */}
        {aiMode && searchTerm.length >= 4 && (
          <div className="flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-4 py-2 text-sm text-primary">
            <Sparkles className="h-4 w-4" />
            {aiLoading ? "AI يحلل طلبك..." : aiResults ? `AI وجد ${aiResults.length} منتج مناسب` : "اكتب وصفاً أطول للحصول على نتائج AI"}
          </div>
        )}

        {/* Loading */}
        {productsQuery.isLoading && (
          <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p>جارٍ تحميل الكتالوج...</p>
          </div>
        )}

        {/* Error */}
        {productsQuery.isError && (
          <Card className="mx-auto flex max-w-lg flex-col items-center gap-4 p-8 text-center">
            <RefreshCw className="h-8 w-8 text-destructive" />
            <h2 className="font-semibold">تعذر تحميل المنتجات</h2>
            <Button onClick={() => productsQuery.refetch()}>إعادة المحاولة</Button>
          </Card>
        )}

        {/* Empty */}
        {!productsQuery.isLoading && !productsQuery.isError && filteredProducts.length === 0 && (
          <Card className="mx-auto flex max-w-lg flex-col items-center gap-3 p-10 text-center">
            <PackageSearch className="h-10 w-10 text-muted-foreground" />
            <h2 className="font-semibold">لا توجد منتجات مطابقة</h2>
            <p className="text-sm text-muted-foreground">جرّب تفعيل بحث AI أو كلمة بحث أخرى.</p>
          </Card>
        )}

        {/* Products grid */}
        {!productsQuery.isLoading && !productsQuery.isError && filteredProducts.length > 0 && (
          <>
            <p className="text-sm text-muted-foreground">
              {aiMode && aiResults ? "🤖 نتائج AI · " : ""}
              {filteredProducts.length} منتج
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filteredProducts.map(product => {
                const price = displayPrice(product.price);
                return (
                  <Card key={product.id} className="group overflow-hidden border-primary/20 bg-card transition-all hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg">
                    <div className="relative overflow-hidden">
                      <img
                        src={imageUrl(product.image)}
                        alt={product.title}
                        className="h-44 w-full object-cover transition-transform duration-300 group-hover:scale-105"
                        loading="lazy"
                        onError={e => { e.currentTarget.src = FALLBACK_IMAGE; }}
                      />
                      {product.category && (
                        <Badge className="absolute right-2 top-2 bg-background/80 text-foreground backdrop-blur text-xs">
                          {CATEGORY_LABELS[product.category] ?? product.category}
                        </Badge>
                      )}
                    </div>
                    <div className="p-4 space-y-3">
                      <h2 className="line-clamp-2 font-semibold text-sm leading-snug">{product.title}</h2>
                      <div className="flex items-center justify-between gap-2">
                        {price
                          ? <span className="text-xl font-black text-primary">{price}</span>
                          : <span className="text-xs text-muted-foreground">السعر غير متوفر</span>
                        }
                        {product.rating && (
                          <span className="flex items-center gap-1 text-xs text-yellow-400">
                            <Star className="h-3 w-3 fill-current" /> {product.rating}
                          </span>
                        )}
                      </div>
                      {product.reviews
                        ? <p className="text-xs text-muted-foreground">{Number(product.reviews).toLocaleString()} مراجعة</p>
                        : null
                      }
                      {product.url && (
                        <Button size="sm" className="w-full gap-2" asChild>
                          <a href={product.url} target="_blank" rel="noopener noreferrer sponsored">
                            عرض المنتج <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
