import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, ExternalLink, Loader2, RefreshCw, PackageSearch } from "lucide-react";
import { useMemo, useState } from "react";

const FALLBACK_IMAGE = "https://placehold.co/800x600/0a0d1a/60a5fa?text=NEO+PULSE+HUB";

function displayPrice(value: unknown) {
  if (value === null || value === undefined || value === "") return "السعر غير متوفر";
  const number = Number(value);
  return Number.isFinite(number) ? `$${number.toFixed(2)}` : String(value);
}

function imageUrl(value: unknown) {
  return typeof value === "string" && value.trim() ? value : FALLBACK_IMAGE;
}

export default function Products() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const productsQuery = trpc.products.all.useQuery(undefined, {
    retry: 2,
    staleTime: 5 * 60 * 1000,
  });
  const products = productsQuery.data ?? [];

  const categories = useMemo(() => {
    const cats = new Set(products.map((product) => product.category).filter(Boolean));
    return Array.from(cats).sort();
  }, [products]);

  const filteredProducts = useMemo(() => {
    const query = searchTerm.trim().toLocaleLowerCase();
    return products.filter((product) => {
      const title = String(product.title ?? "").toLocaleLowerCase();
      const category = String(product.category ?? "").toLocaleLowerCase();
      const matchesSearch = !query || title.includes(query) || category.includes(query);
      const matchesCategory = !selectedCategory || product.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [products, searchTerm, selectedCategory]);

  return (
    <div dir="rtl" className="min-h-screen bg-background grid-pattern">
      <header className="border-b border-border bg-card/70 backdrop-blur">
        <div className="container py-6">
          <h1 className="text-3xl font-bold text-gradient">كتالوج المنتجات</h1>
          <p className="mt-1 text-sm text-muted-foreground">منتجات موحّدة من مصدر الكتالوج المركزي</p>
        </div>
      </header>

      <main className="container space-y-6 py-8">
        <section className="space-y-4" aria-label="خيارات البحث والتصفية">
          <div className="relative">
            <Search className="absolute right-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              dir="rtl"
              aria-label="البحث في المنتجات"
              placeholder="ابحث عن منتج أو فئة..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="pr-10 input-neon"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant={selectedCategory === null ? "default" : "outline"} onClick={() => setSelectedCategory(null)}>
              جميع الفئات
            </Button>
            {categories.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </Button>
            ))}
          </div>
        </section>

        {productsQuery.isLoading && (
          <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground" role="status">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p>جارٍ تحميل الكتالوج...</p>
          </div>
        )}

        {productsQuery.isError && (
          <Card className="mx-auto flex max-w-lg flex-col items-center gap-4 p-8 text-center">
            <RefreshCw className="h-8 w-8 text-destructive" />
            <div>
              <h2 className="font-semibold">تعذر تحميل المنتجات</h2>
              <p className="mt-2 text-sm text-muted-foreground">تحقق من الاتصال ثم أعد المحاولة. لا توجد جلسة دخول مطلوبة لعرض الكتالوج.</p>
            </div>
            <Button onClick={() => productsQuery.refetch()}>إعادة المحاولة</Button>
          </Card>
        )}

        {!productsQuery.isLoading && !productsQuery.isError && filteredProducts.length === 0 && (
          <Card className="mx-auto flex max-w-lg flex-col items-center gap-3 p-10 text-center">
            <PackageSearch className="h-10 w-10 text-muted-foreground" />
            <h2 className="font-semibold">لا توجد منتجات مطابقة</h2>
            <p className="text-sm text-muted-foreground">جرّب كلمة بحث أخرى أو أزل الفلتر الحالي.</p>
          </Card>
        )}

        {!productsQuery.isLoading && !productsQuery.isError && filteredProducts.length > 0 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredProducts.map((product) => (
              <Card key={product.id} className="overflow-hidden border-primary/20 bg-card transition-all hover:-translate-y-0.5 hover:border-primary/50">
                <img
                  src={imageUrl(product.image)}
                  alt={product.title}
                  className="h-48 w-full object-cover"
                  loading="lazy"
                  onError={(event) => {
                    event.currentTarget.src = FALLBACK_IMAGE;
                  }}
                />
                <div className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <h2 className="line-clamp-2 font-semibold text-foreground">{product.title}</h2>
                    {product.category && <Badge variant="outline">{product.category}</Badge>}
                  </div>
                  <div className="mt-4 flex items-center justify-between gap-3">
                    <span className="text-lg font-bold text-primary">{displayPrice(product.price)}</span>
                    {product.rating && <Badge className="border-yellow-500/30 bg-yellow-500/20 text-yellow-500">⭐ {product.rating}</Badge>}
                  </div>
                  {product.reviews ? <p className="mt-2 text-xs text-muted-foreground">{product.reviews.toLocaleString()} مراجعة</p> : null}
                  {product.url && (
                    <Button size="sm" className="mt-4 w-full" asChild>
                      <a href={product.url} target="_blank" rel="noopener noreferrer">
                        عرض المنتج <ExternalLink className="ms-2 h-3 w-3" />
                      </a>
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
