import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowLeft, BookOpen, Link2, Play, Sparkles, Store } from "lucide-react";

const destinations = [
  { href: "/products", title: "المنتجات الذكية", text: "اكتشف كتالوجًا موحدًا ببيانات حقيقية وروابط المتاجر الشريكة.", icon: Store },
  { href: "/blogs", title: "المدونة والأدلة", text: "مقارنات وشروحات بالعربية والإنجليزية قبل اتخاذ قرار الشراء.", icon: BookOpen },
  { href: "/videos", title: "الفيديوهات", text: "شروحات قصيرة عن الأجهزة والذكاء الاصطناعي والمنزل الذكي.", icon: Play },
];

export default function Landing() {
  return (
    <div dir="rtl" className="min-h-screen bg-background grid-pattern">
      <header className="border-b border-border bg-card/70 backdrop-blur">
        <div className="container flex items-center justify-between gap-4 py-5">
          <div className="flex items-center gap-2 font-bold"><Sparkles className="h-5 w-5 text-primary" /> Neo Pulse Hub</div>
          <div className="flex gap-2">
            <Button asChild variant="outline" size="sm"><a href="/affiliate-programs"><Link2 className="ml-2 h-4 w-4" />الأفلييت</a></Button>
            <Button asChild size="sm"><a href="/products">استكشف المنتجات</a></Button>
          </div>
        </div>
      </header>
      <main>
        <section className="container grid gap-10 py-16 lg:grid-cols-[1.15fr_0.85fr] lg:items-center lg:py-24">
          <div>
            <Badge className="mb-5 bg-primary/15 text-primary">Global smart technology marketplace</Badge>
            <h1 className="max-w-3xl text-4xl font-black leading-tight sm:text-6xl">اكتشف التقنية المفيدة قبل أن تشتري</h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">Neo Pulse Hub يجمع المنتجات الذكية والأدلة العملية ومحتوى الذكاء الاصطناعي في تجربة واحدة بالعربية والإنجليزية.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg"><a href="/products">ابدأ الاستكشاف <ArrowLeft className="mr-2 h-4 w-4" /></a></Button>
              <Button asChild variant="outline" size="lg"><a href="/blogs">اقرأ الأدلة</a></Button>
            </div>
          </div>
          <Card className="glow-cyan overflow-hidden border-primary/30 bg-card/80">
            <CardContent className="p-6">
              <p className="text-sm text-primary">شفافية أولًا</p>
              <h2 className="mt-3 text-2xl font-bold">بيانات حقيقية، روابط رسمية، وعمولات معلنة</h2>
              <p className="mt-4 leading-7 text-muted-foreground">قد نحصل على عمولة عند إتمام عملية شراء مؤهلة عبر بعض الروابط. السعر والدفع والشحن والضمان يحددها المتجر الشريك.</p>
            </CardContent>
          </Card>
        </section>
        <section className="container grid gap-4 pb-16 md:grid-cols-3">
          {destinations.map(({ href, title, text, icon: Icon }) => (
            <a href={href} key={href} className="group">
              <Card className="h-full border-primary/15 bg-card/70 transition duration-200 group-hover:-translate-y-1 group-hover:border-primary/60">
                <CardContent className="p-6"><Icon className="h-7 w-7 text-primary" /><h2 className="mt-5 text-xl font-bold">{title}</h2><p className="mt-3 leading-7 text-muted-foreground">{text}</p><span className="mt-5 inline-flex items-center text-sm text-primary">فتح القسم <ArrowLeft className="mr-2 h-4 w-4" /></span></CardContent>
              </Card>
            </a>
          ))}
        </section>
      </main>
    </div>
  );
}
