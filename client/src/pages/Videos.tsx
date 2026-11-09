import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, Play, Video } from "lucide-react";

const videos = [
  {
    title: "How to choose the right smart device",
    titleAr: "كيف تختار الجهاز الذكي المناسب؟",
    description: "A practical framework for comparing compatibility, privacy, support, and real-world value before buying.",
    descriptionAr: "طريقة عملية لمقارنة التوافق والخصوصية والدعم والقيمة الحقيقية قبل الشراء.",
    query: "smart device buying guide Neo Pulse Hub",
    category: "Buying guides",
  },
  {
    title: "AI tools for everyday productivity",
    titleAr: "أدوات الذكاء الاصطناعي للإنتاجية اليومية",
    description: "Short explainers covering useful workflows, safe automation, and transparent product recommendations.",
    descriptionAr: "شروحات قصيرة عن سير العمل المفيد والأتمتة الآمنة وترشيحات المنتجات الشفافة.",
    query: "AI productivity tools tutorial",
    category: "AI & productivity",
  },
  {
    title: "Smart home setup checklist",
    titleAr: "قائمة فحص إعداد المنزل الذكي",
    description: "A simple checklist for connectivity, security updates, interoperability, and energy use.",
    descriptionAr: "قائمة بسيطة للتوصيل وتحديثات الأمان والتوافق واستهلاك الطاقة.",
    query: "smart home setup checklist",
    category: "Smart home",
  },
];

export default function Videos() {
  return (
    <div dir="rtl" className="min-h-screen bg-background grid-pattern">
      <header className="border-b border-border bg-card/70 backdrop-blur">
        <div className="container py-8">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-primary/15 p-3"><Video className="h-6 w-6 text-primary" /></div>
            <div>
              <h1 className="text-3xl font-bold text-gradient">فيديوهات Neo Pulse Hub</h1>
              <p className="mt-1 text-sm text-muted-foreground">شروحات مختصرة تساعدك على اتخاذ قرارات تقنية أفضل</p>
            </div>
          </div>
        </div>
      </header>
      <main className="container py-8">
        <section className="mb-8 rounded-2xl border border-primary/20 bg-card/70 p-6">
          <Badge className="mb-3 bg-primary/15 text-primary">محتوى أصلي قادم</Badge>
          <h2 className="text-2xl font-bold">مكتبة فيديوهات للمتسوق الذكي</h2>
          <p className="mt-3 max-w-3xl leading-7 text-muted-foreground">
            نبدأ بصفحة منظمة قابلة للربط بقناة YouTube أو TikTok الرسمية. لا نعرض فيديوهات وهمية ولا نرفع ملفات كبيرة إلى الخادم؛ كل بطاقة تقود إلى بحث موثوق إلى أن تضيف روابطك الرسمية.
          </p>
        </section>
        <div className="grid gap-5 md:grid-cols-3">
          {videos.map((video) => (
            <Card key={video.title} className="overflow-hidden border-primary/20 bg-card/80 transition hover:-translate-y-1 hover:border-primary/60">
              <div className="flex aspect-video items-center justify-center bg-gradient-to-br from-primary/20 via-secondary/10 to-background">
                <Play className="h-12 w-12 rounded-full bg-primary p-3 text-primary-foreground" />
              </div>
              <CardHeader>
                <Badge variant="outline" className="w-fit">{video.category}</Badge>
                <CardTitle className="mt-2 text-xl">{video.titleAr}</CardTitle>
                <p className="text-sm text-muted-foreground" dir="ltr">{video.title}</p>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-6 text-muted-foreground">{video.descriptionAr}</p>
                <p className="mt-2 text-xs leading-5 text-muted-foreground" dir="ltr">{video.description}</p>
                <Button asChild className="mt-5 w-full gap-2">
                  <a href={`https://www.youtube.com/results?search_query=${encodeURIComponent(video.query)}`} target="_blank" rel="noreferrer">
                    استكشاف الفيديوهات <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
