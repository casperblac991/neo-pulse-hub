import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sparkles, Package, FileText, TrendingUp, Zap, ArrowLeft,
  DollarSign, Users, Eye, Link2, BarChart3, ExternalLink,
  AlertCircle, CheckCircle, Clock, RefreshCw,
} from "lucide-react";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import { useMemo } from "react";

export default function Home() {
  const { loading, isAuthenticated, user } = useAuth();
  const productsQuery = trpc.products.all.useQuery(undefined, { staleTime: 60_000 });
  const products = productsQuery.data ?? [];

  const stats = useMemo(() => {
    const totalProducts = products.length;
    const categories = new Set(products.map(p => p.category).filter(Boolean)).size;
    const withUrls = products.filter(p => p.url).length;
    const avgRating = products.reduce((s, p) => s + Number(p.rating || 0), 0) / (totalProducts || 1);
    return { totalProducts, categories, withUrls, avgRating: avgRating.toFixed(1) };
  }, [products]);

  const affiliateNetworks = [
    { name: "Amazon Associates", var: "AMAZON_ASSOCIATE_TAG",    signup: "https://affiliate-program.amazon.com/", commission: "1–10%" },
    { name: "AliExpress",        var: "ALIEXPRESS_PUBLISHER_ID", signup: "https://portals.aliexpress.com/",       commission: "3–9%"  },
    { name: "eBay Partner",      var: "EBAY_CAMPAIGN_ID",        signup: "https://partnernetwork.ebay.com/",      commission: "1–6%"  },
    { name: "Awin",              var: "AWIN_PUBLISHER_ID",       signup: "https://www.awin.com/",                 commission: "2–15%" },
    { name: "CJ Affiliate",      var: "CJ_PUBLISHER_ID",         signup: "https://www.cj.com/",                   commission: "2–10%" },
    { name: "Impact.com",        var: "IMPACT_PARTNER_ID",       signup: "https://impact.com/partners/affiliate-partners/", commission: "3–12%" },
    { name: "Rakuten",           var: "RAKUTEN_PUBLISHER_ID",    signup: "https://rakutenadvertising.com/affiliate/", commission: "1–8%" },
  ];

  if (loading) return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <Sparkles className="h-10 w-10 animate-pulse text-primary" />
    </div>
  );

  if (!isAuthenticated) return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="max-w-md p-8 text-center space-y-5">
        <div className="mx-auto rounded-2xl bg-primary/15 p-4 w-fit">
          <BarChart3 className="h-10 w-10 text-primary" />
        </div>
        <h1 className="text-2xl font-bold">لوحة التحكم</h1>
        <p className="text-muted-foreground text-sm leading-7">
          سجّل الدخول لعرض إحصائيات منصتك وإدارة قنوات الأفيليت.
        </p>
        <Button asChild className="w-full">
          <a href={getLoginUrl()}>تسجيل الدخول <Zap className="ms-2 h-4 w-4" /></a>
        </Button>
      </Card>
    </div>
  );

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
              <h1 className="text-xl font-bold">لوحة التحكم</h1>
              <p className="text-xs text-muted-foreground">مرحباً {user?.name ?? "بك"} 👋</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button asChild variant="outline" size="sm">
              <a href="/copilot"><Sparkles className="ml-2 h-4 w-4" />Neo Copilot</a>
            </Button>
            <Button asChild size="sm">
              <a href="/products"><Package className="ml-2 h-4 w-4" />المنتجات</a>
            </Button>
          </div>
        </div>
      </header>

      <main className="container space-y-8 py-8">

        {/* KPI Stats */}
        <section>
          <h2 className="mb-4 text-lg font-bold">📊 إحصائيات المنصة</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: Package,    label: "إجمالي المنتجات",    value: stats.totalProducts, color: "text-blue-400",   sub: "في الكتالوج" },
              { icon: TrendingUp, label: "فئات المنتجات",      value: stats.categories,    color: "text-green-400",  sub: "فئة مختلفة" },
              { icon: Link2,      label: "روابط أفيليت",       value: stats.withUrls,      color: "text-purple-400", sub: "منتج بروابط" },
              { icon: Eye,        label: "متوسط التقييم",      value: stats.avgRating,     color: "text-yellow-400", sub: "من 5 نجوم" },
            ].map(({ icon: Icon, label, value, color, sub }) => (
              <Card key={label} className="border-primary/20 bg-card/80">
                <CardContent className="p-5">
                  <Icon className={`h-5 w-5 ${color} mb-3`} />
                  <p className={`text-3xl font-black ${color}`}>{value}</p>
                  <p className="mt-1 text-sm font-medium">{label}</p>
                  <p className="text-xs text-muted-foreground">{sub}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Affiliate status */}
        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold">💰 شبكات الأفيليت</h2>
            <Button asChild variant="outline" size="sm">
              <a href="/affiliate-programs">إدارة الكل</a>
            </Button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {affiliateNetworks.map(net => (
              <Card key={net.name} className="border-primary/15 bg-card/80">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <p className="font-semibold text-sm">{net.name}</p>
                    <Badge className="bg-yellow-500/15 text-yellow-400 border-yellow-500/20 text-xs shrink-0">
                      <Clock className="h-3 w-3 ml-1" /> بانتظار
                    </Badge>
                  </div>
                  <p className="text-xs text-green-400 font-semibold mb-3">عمولة {net.commission}</p>
                  <code className="block text-xs bg-muted rounded px-2 py-1 text-muted-foreground mb-3 break-all">
                    {net.var}
                  </code>
                  <Button asChild variant="outline" size="sm" className="w-full gap-1 text-xs">
                    <a href={net.signup} target="_blank" rel="noreferrer noopener">
                      سجّل <ExternalLink className="h-3 w-3" />
                    </a>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          {/* Render setup hint */}
          <Card className="mt-4 border-blue-500/20 bg-blue-500/5">
            <CardContent className="p-4 text-sm">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-blue-400">بعد التسجيل في أي شبكة:</p>
                  <ol className="mt-2 space-y-1 text-muted-foreground text-xs">
                    <li>1. اذهب لـ <a href="https://dashboard.render.com" target="_blank" rel="noreferrer" className="text-primary underline">dashboard.render.com</a> ← neo-pulse-hub ← Environment</li>
                    <li>2. أضف المتغير (الاسم موضح فوق) بالقيمة التي حصلت عليها من الشبكة</li>
                    <li>3. أضف اسم الشبكة إلى <code className="bg-muted px-1 rounded">AFFILIATE_APPROVED_NETWORKS</code></li>
                    <li>4. اضغط Save — الروابط تتفعّل تلقائياً ✅</li>
                  </ol>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Quick nav */}
        <section>
          <h2 className="mb-4 text-lg font-bold">🚀 الوصول السريع</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { href: "/products",           icon: Package,    label: "كتالوج المنتجات",  sub: `${stats.totalProducts} منتج`,  color: "text-blue-400"   },
              { href: "/blogs",              icon: FileText,   label: "المقالات والأدلة",  sub: "محتوى SEO",                   color: "text-green-400"  },
              { href: "/copilot",            icon: Sparkles,   label: "Neo Copilot AI",   sub: "مساعد ذكي",                   color: "text-purple-400" },
              { href: "/affiliate-programs", icon: Link2,      label: "شبكات الأفيليت",   sub: "7 شبكات",                     color: "text-yellow-400" },
            ].map(({ href, icon: Icon, label, sub, color }) => (
              <a key={href} href={href}>
                <Card className="border-primary/15 bg-card/70 p-4 transition hover:-translate-y-1 hover:border-primary/50 hover:shadow-md cursor-pointer">
                  <Icon className={`h-6 w-6 ${color} mb-3`} />
                  <p className="font-semibold text-sm">{label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{sub}</p>
                </Card>
              </a>
            ))}
          </div>
        </section>

        {/* Top products preview */}
        {products.length > 0 && (
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold">🛍️ أعلى المنتجات تقييماً</h2>
              <Button asChild variant="ghost" size="sm">
                <a href="/products">عرض الكل</a>
              </Button>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[...products]
                .sort((a, b) => Number(b.rating) - Number(a.rating))
                .slice(0, 6)
                .map(p => (
                  <Card key={p.id} className="border-primary/15 bg-card/80 flex items-center gap-3 p-3">
                    <img
                      src={p.image || "https://placehold.co/80x80/0a0d1a/60a5fa?text=N"}
                      alt={p.title}
                      className="h-12 w-12 rounded-lg object-cover shrink-0"
                      loading="lazy"
                      onError={e => { e.currentTarget.src = "https://placehold.co/80x80/0a0d1a/60a5fa?text=N"; }}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium line-clamp-1">{p.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        {p.price && <span className="text-sm font-bold text-primary">${p.price}</span>}
                        {p.rating && <span className="text-xs text-yellow-400">⭐ {p.rating}</span>}
                      </div>
                    </div>
                    {p.url && (
                      <a href={p.url} target="_blank" rel="noreferrer noopener sponsored" className="text-muted-foreground hover:text-primary transition-colors shrink-0">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                  </Card>
                ))
              }
            </div>
          </section>
        )}

      </main>
    </div>
  );
}
