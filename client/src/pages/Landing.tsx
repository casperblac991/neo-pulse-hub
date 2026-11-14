import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  ArrowLeft, BookOpen, Link2, Play, Sparkles, Store,
  Star, TrendingUp, Users, ShoppingCart, Zap, Globe,
} from "lucide-react";
import { useEffect, useState } from "react";

const destinations = [
  { href: "/products",           title: "المنتجات الذكية",    text: "كتالوج موحد بروابط Amazon و AliExpress و eBay الحقيقية.",           icon: Store },
  { href: "/blogs",              title: "الأدلة والمقارنات", text: "مقالات بالعربية والإنجليزية تساعدك تختار قبل الشراء.",              icon: BookOpen },
  { href: "/videos",             title: "الفيديوهات",         text: "شروحات قصيرة عن الأجهزة والذكاء الاصطناعي.",                        icon: Play },
  { href: "/affiliate-programs", title: "شبكات الأفلييت",    text: "Amazon · eBay · AliExpress · Awin · CJ — روابط مفعّلة مباشرة.",    icon: Link2 },
];

const stats = [
  { label: "منتج في الكتالوج",  value: "318+",  icon: ShoppingCart },
  { label: "شبكة أفلييت",       value: "7",     icon: Globe },
  { label: "مقالة ودليل",       value: "50+",   icon: TrendingUp },
  { label: "زيارة شهرية",       value: "∞",     icon: Users },
];

const networks = [
  { name: "Amazon Associates", commission: "1–10%",  color: "text-orange-400",  signup: "https://affiliate-program.amazon.com/" },
  { name: "eBay Partner Network", commission: "1–6%", color: "text-blue-400",   signup: "https://partnernetwork.ebay.com/" },
  { name: "AliExpress Portals",  commission: "3–9%", color: "text-red-400",     signup: "https://portals.aliexpress.com/" },
  { name: "Awin",                commission: "2–15%", color: "text-green-400",  signup: "https://www.awin.com/" },
  { name: "CJ Affiliate",        commission: "2–10%", color: "text-purple-400", signup: "https://www.cj.com/" },
  { name: "Impact.com",          commission: "3–12%", color: "text-cyan-400",   signup: "https://impact.com/partners/affiliate-partners/" },
  { name: "Rakuten Advertising", commission: "1–8%",  color: "text-pink-400",   signup: "https://rakutenadvertising.com/affiliate/" },
];

export default function Landing() {
  const [products, setProducts] = useState<{ name_ar?: string; price?: number; rating?: number; image?: string; affiliate_url?: string }[]>([]);

  useEffect(() => {
    fetch("/api/products")
      .then(r => r.json())
      .then(d => setProducts((d.products ?? d).slice(0, 6)))
      .catch(() => {});
  }, []);

  return (
    <div dir="rtl" className="min-h-screen bg-background">

      {/* ── Navbar ── */}
      <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur">
        <div className="container flex items-center justify-between gap-4 py-4">
          <div className="flex items-center gap-2 text-xl font-black">
            <Sparkles className="h-5 w-5 text-primary" />
            <span className="text-gradient">Neo Pulse Hub</span>
          </div>
          <nav className="hidden items-center gap-6 text-sm font-medium md:flex">
            <a href="/products"           className="hover:text-primary transition-colors">المنتجات</a>
            <a href="/blogs"              className="hover:text-primary transition-colors">الأدلة</a>
            <a href="/affiliate-programs" className="hover:text-primary transition-colors">الأفلييت</a>
          </nav>
          <div className="flex gap-2">
            <Button asChild variant="outline" size="sm">
              <a href="/affiliate-programs"><Link2 className="ml-2 h-4 w-4" />شبكات الأفلييت</a>
            </Button>
            <Button asChild size="sm">
              <a href="/products">استكشف المنتجات</a>
            </Button>
          </div>
        </div>
      </header>

      <main>

        {/* ── Hero ── */}
        <section className="container grid gap-10 py-16 lg:grid-cols-[1.2fr_0.8fr] lg:items-center lg:py-24">
          <div>
            <Badge className="mb-5 bg-primary/15 text-primary">
              <Zap className="ml-1 h-3 w-3" /> منصة أفلييت عالمية · تقنية ذكية
            </Badge>
            <h1 className="max-w-3xl text-4xl font-black leading-tight sm:text-6xl">
              اكتشف، قارن، واكسب من كل بيع
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              Neo Pulse Hub يجمع أفضل المنتجات التقنية مع روابط أفلييت من <strong>Amazon · eBay · AliExpress · Awin</strong> في تجربة واحدة بالعربية والإنجليزية.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <a href="/products">تصفح المنتجات <ArrowLeft className="mr-2 h-4 w-4" /></a>
              </Button>
              <Button asChild variant="outline" size="lg">
                <a href="/affiliate-programs">سجّل في الأفلييت</a>
              </Button>
            </div>
          </div>
          {/* Stats card */}
          <Card className="glow-cyan overflow-hidden border-primary/30 bg-card/80">
            <CardContent className="p-6">
              <p className="text-sm font-semibold text-primary">الأرقام الحقيقية</p>
              <div className="mt-4 grid grid-cols-2 gap-4">
                {stats.map(({ label, value, icon: Icon }) => (
                  <div key={label} className="rounded-xl border border-border bg-background/60 p-4 text-center">
                    <Icon className="mx-auto mb-2 h-5 w-5 text-primary" />
                    <p className="text-2xl font-black text-primary">{value}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{label}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>

        {/* ── Affiliate Networks ── */}
        <section className="border-y border-border bg-card/40 py-12">
          <div className="container">
            <div className="mb-8 text-center">
              <h2 className="text-2xl font-bold">7 شبكات أفلييت جاهزة للتفعيل</h2>
              <p className="mt-2 text-sm text-muted-foreground">سجّل في كل شبكة مرة واحدة — المنصة تُدمج روابطك تلقائياً</p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {networks.map(net => (
                <a
                  key={net.name}
                  href={net.signup}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="group flex items-center justify-between rounded-xl border border-border bg-card/70 px-4 py-3 transition hover:-translate-y-0.5 hover:border-primary/50 hover:shadow-md"
                >
                  <div>
                    <p className="text-sm font-semibold">{net.name}</p>
                    <p className={`text-xs font-bold ${net.color}`}>عمولة {net.commission}</p>
                  </div>
                  <ArrowLeft className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </a>
              ))}
            </div>
            <p className="mt-6 text-center text-xs text-muted-foreground">
              بعد التسجيل، أضف معرّفاتك في Render Environment Variables وتفعّل تلقائياً ✅
            </p>
          </div>
        </section>

        {/* ── How to earn ── */}
        <section className="container py-16">
          <div className="mb-10 text-center">
            <h2 className="text-3xl font-bold">كيف تكسب دخلاً من المنصة؟</h2>
            <p className="mt-3 text-muted-foreground">3 خطوات بسيطة لتحويل الزوار إلى دخل حقيقي</p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { step: "01", title: "سجّل في الأفلييت", text: "أنشئ حسابات في Amazon Associates وAliExpress وeBay. كل واحدة تأخذ 10 دقائق وتُقبل خلال 24–48 ساعة.", color: "text-orange-400" },
              { step: "02", title: "أضف المعرّفات على Render", text: "ضع AMAZON_ASSOCIATE_TAG وALIEXPRESS_PUBLISHER_ID في Environment Variables — المنصة تُفعّل الروابط فوراً.", color: "text-blue-400" },
              { step: "03", title: "استقبل العمولات", text: "كل زائر يضغط رابطاً ويشتري خلال 24–90 يوم = عمولة لك. Amazon تدفع شهرياً، AliExpress كل 20 يوم.", color: "text-green-400" },
            ].map(({ step, title, text, color }) => (
              <Card key={step} className="border-primary/20 bg-card/80">
                <CardContent className="p-6">
                  <p className={`text-5xl font-black ${color} opacity-30`}>{step}</p>
                  <h3 className="mt-3 text-xl font-bold">{title}</h3>
                  <p className="mt-3 leading-7 text-muted-foreground text-sm">{text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* ── Featured products ── */}
        {products.length > 0 && (
          <section className="border-t border-border bg-card/30 py-14">
            <div className="container">
              <div className="mb-8 flex items-center justify-between">
                <h2 className="text-2xl font-bold">منتجات مميزة</h2>
                <Button asChild variant="outline" size="sm"><a href="/products">عرض الكل</a></Button>
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {products.map((p, i) => (
                  <Card key={i} className="overflow-hidden border-primary/15 bg-card/70 transition hover:-translate-y-1 hover:border-primary/40">
                    {p.image && (
                      <div className="aspect-video overflow-hidden bg-muted">
                        <img src={p.image} alt={p.name_ar ?? ""} className="h-full w-full object-cover" loading="lazy" />
                      </div>
                    )}
                    <CardContent className="p-4">
                      <p className="font-semibold line-clamp-2">{p.name_ar}</p>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-lg font-black text-primary">${p.price}</span>
                        {p.rating && (
                          <span className="flex items-center gap-1 text-xs text-yellow-400">
                            <Star className="h-3 w-3 fill-current" /> {p.rating}
                          </span>
                        )}
                      </div>
                      {p.affiliate_url && (
                        <Button asChild size="sm" className="mt-3 w-full" variant="outline">
                          <a href={p.affiliate_url} target="_blank" rel="noreferrer noopener sponsored">
                            عرض على المتجر
                          </a>
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ── Sections grid ── */}
        <section className="container grid gap-4 py-14 md:grid-cols-2 lg:grid-cols-4">
          {destinations.map(({ href, title, text, icon: Icon }) => (
            <a href={href} key={href} className="group">
              <Card className="h-full border-primary/15 bg-card/70 transition duration-200 group-hover:-translate-y-1 group-hover:border-primary/60">
                <CardContent className="p-6">
                  <Icon className="h-7 w-7 text-primary" />
                  <h2 className="mt-5 text-xl font-bold">{title}</h2>
                  <p className="mt-3 text-sm leading-7 text-muted-foreground">{text}</p>
                  <span className="mt-5 inline-flex items-center text-sm text-primary">
                    فتح القسم <ArrowLeft className="mr-2 h-4 w-4" />
                  </span>
                </CardContent>
              </Card>
            </a>
          ))}
        </section>

        {/* ── Footer ── */}
        <footer className="border-t border-border bg-card/50 py-8">
          <div className="container flex flex-col items-center gap-3 text-center text-xs text-muted-foreground">
            <p className="font-semibold text-sm"><Sparkles className="inline h-4 w-4 text-primary ml-1" />Neo Pulse Hub</p>
            <p>قد نحصل على عمولة عند إتمام عملية شراء مؤهلة عبر روابط الأفلييت. السعر والشحن والضمان تحددها المتاجر الشريكة.</p>
            <p>© {new Date().getFullYear()} Neo Pulse Hub · جميع الحقوق محفوظة</p>
          </div>
        </footer>

      </main>
    </div>
  );
}
