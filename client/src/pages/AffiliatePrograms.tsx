import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, Link2, Loader2, ShieldCheck, CheckCircle, Clock, ArrowLeft } from "lucide-react";

type Program = {
  id: string;
  name: string;
  officialUrl: string;
  status: string;
  credentialConfigured: boolean;
  markets: string[];
};

const signupGuides: Record<string, { commission: string; time: string; pays: string; steps: string[] }> = {
  "amazon-associates": {
    commission: "1–10%", time: "24–48 ساعة", pays: "شهرياً (60 يوم تأخير)",
    steps: ["اذهب إلى الرابط أدناه", "سجّل بحساب Amazon عادي", "أضف موقعك neo-pulse-hub.it.com", "احصل على Associate Tag مثل neopulse-20", "أضفه في Render: AMAZON_ASSOCIATE_TAG"],
  },
  "ebay-partner-network": {
    commission: "1–6%", time: "فوري", pays: "شهرياً",
    steps: ["اذهب إلى الرابط أدناه", "سجّل بحساب eBay", "أضف موقعك", "احصل على Campaign ID", "أضفه في Render: EBAY_CAMPAIGN_ID"],
  },
  "aliexpress": {
    commission: "3–9%", time: "فوري", pays: "كل 20 يوم",
    steps: ["اذهب إلى portals.aliexpress.com", "سجّل بحساب AliExpress", "اختر Publisher Portal", "احصل على Publisher ID", "أضفه في Render: ALIEXPRESS_PUBLISHER_ID"],
  },
  "awin": {
    commission: "2–15%", time: "2–5 أيام", pays: "شهرياً",
    steps: ["اذهب إلى الرابط أدناه", "ادفع رسوم £5 مرة واحدة (تُرجع)", "أضف موقعك للمراجعة", "احصل على Publisher ID", "أضفه في Render: AWIN_PUBLISHER_ID"],
  },
  "cj-affiliate": {
    commission: "2–10%", time: "1–3 أيام", pays: "شهرياً",
    steps: ["اذهب إلى cj.com", "سجّل كـ Publisher", "أضف موقعك", "احصل على Publisher ID", "أضفه في Render: CJ_PUBLISHER_ID"],
  },
  "impact": {
    commission: "3–12%", time: "1–3 أيام", pays: "شهرياً",
    steps: ["اذهب إلى الرابط أدناه", "سجّل كـ Affiliate Partner", "أضف موقعك", "احصل على Partner ID", "أضفه في Render: IMPACT_PARTNER_ID"],
  },
  "rakuten-advertising": {
    commission: "1–8%", time: "2–5 أيام", pays: "شهرياً",
    steps: ["اذهب إلى الرابط أدناه", "سجّل كـ Publisher", "أضف موقعك للمراجعة", "احصل على Publisher ID", "أضفه في Render: RAKUTEN_PUBLISHER_ID"],
  },
};

export default function AffiliatePrograms() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [disclosure, setDisclosure] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/affiliate/programs")
      .then(r => r.json())
      .then(payload => {
        setPrograms(payload.programs ?? []);
        setDisclosure(payload.disclosure ?? "");
      })
      .catch(() => setPrograms([]))
      .finally(() => setLoading(false));
  }, []);

  const totalApproved = programs.filter(p => p.status === "approved").length;
  const totalConfigured = programs.filter(p => p.credentialConfigured).length;

  return (
    <div dir="rtl" className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/70 backdrop-blur sticky top-0 z-40">
        <div className="container flex items-center justify-between gap-4 py-4">
          <div className="flex items-center gap-3">
            <a href="/" className="text-muted-foreground hover:text-primary transition-colors">
              <ArrowLeft className="h-5 w-5" />
            </a>
            <div className="flex items-center gap-2">
              <div className="rounded-xl bg-primary/15 p-2"><Link2 className="h-5 w-5 text-primary" /></div>
              <div>
                <h1 className="text-xl font-bold">شبكات الأفلييت</h1>
                <p className="text-xs text-muted-foreground">7 شبكات عالمية · عمولات حقيقية</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-muted-foreground">مفعّلة: <strong className="text-green-400">{totalApproved}</strong>/7</span>
            <span className="text-muted-foreground">مُعرَّفة: <strong className="text-blue-400">{totalConfigured}</strong>/7</span>
          </div>
        </div>
      </header>

      <main className="container space-y-8 py-8">

        {/* How it works */}
        <section className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-6">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-emerald-400" />
            <div>
              <h2 className="font-bold text-lg">خطوات الربح من الأفلييت</h2>
              <div className="mt-3 grid gap-3 sm:grid-cols-3 text-sm">
                <div className="rounded-xl bg-background/50 p-3">
                  <p className="font-semibold text-primary">① سجّل</p>
                  <p className="mt-1 text-muted-foreground">في كل شبكة تهمك (Amazon أسهل بداية)</p>
                </div>
                <div className="rounded-xl bg-background/50 p-3">
                  <p className="font-semibold text-primary">② أضف المعرّف</p>
                  <p className="mt-1 text-muted-foreground">في Render Environment Variables بالاسم الموضح</p>
                </div>
                <div className="rounded-xl bg-background/50 p-3">
                  <p className="font-semibold text-primary">③ استقبل العمولات</p>
                  <p className="mt-1 text-muted-foreground">كل شراء عبر روابطك = عمولة تصل لحسابك</p>
                </div>
              </div>
              {disclosure && <p className="mt-4 text-xs text-muted-foreground border-t border-border pt-3">{disclosure}</p>}
            </div>
          </div>
        </section>

        {/* Programs grid */}
        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {programs.map(program => {
              const guide = signupGuides[program.id];
              const isOpen = selected === program.id;
              return (
                <Card key={program.id} className={`border-primary/20 bg-card/80 transition ${isOpen ? "border-primary/60" : ""}`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <CardTitle className="text-base">{program.name}</CardTitle>
                      <div className="flex flex-col items-end gap-1">
                        <Badge className={program.status === "approved" ? "bg-green-500/15 text-green-400 border-green-500/20" : "bg-yellow-500/15 text-yellow-400 border-yellow-500/20"}>
                          {program.status === "approved" ? <><CheckCircle className="ml-1 h-3 w-3" />مفعّلة</> : <><Clock className="ml-1 h-3 w-3" />بانتظار التسجيل</>}
                        </Badge>
                        {program.credentialConfigured && (
                          <Badge className="bg-blue-500/15 text-blue-400 border-blue-500/20 text-xs">✓ Render</Badge>
                        )}
                      </div>
                    </div>
                    {guide && (
                      <div className="flex gap-3 text-xs text-muted-foreground">
                        <span className="text-green-400 font-semibold">عمولة {guide.commission}</span>
                        <span>·</span>
                        <span>قبول {guide.time}</span>
                        <span>·</span>
                        <span>دفع {guide.pays}</span>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground">
                      الأسواق: {program.markets.slice(0, 5).join("، ")}{program.markets.length > 5 ? "..." : ""}
                    </p>
                  </CardHeader>
                  <CardContent className="space-y-3">

                    {/* Steps (expandable) */}
                    {guide && (
                      <div>
                        <button
                          onClick={() => setSelected(isOpen ? null : program.id)}
                          className="text-xs text-primary hover:underline"
                        >
                          {isOpen ? "إخفاء الخطوات ▲" : "عرض خطوات التسجيل ▼"}
                        </button>
                        {isOpen && (
                          <ol className="mt-3 space-y-1.5 text-xs text-muted-foreground">
                            {guide.steps.map((s, i) => (
                              <li key={i} className="flex gap-2">
                                <span className="shrink-0 font-bold text-primary">{i + 1}.</span>
                                <span>{s}</span>
                              </li>
                            ))}
                          </ol>
                        )}
                      </div>
                    )}

                    <Button asChild variant="outline" className="w-full gap-2 text-sm">
                      <a href={program.officialUrl} target="_blank" rel="noreferrer noopener">
                        سجّل الآن <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>

                    {!program.credentialConfigured && (
                      <p className="text-center text-xs text-muted-foreground">
                        بعد التسجيل أضف المعرّف في Render ← Environment Variables
                      </p>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Render setup guide */}
        <section className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-6">
          <h2 className="font-bold text-lg mb-4">🔧 كيف تُضيف المعرّفات على Render؟</h2>
          <ol className="space-y-2 text-sm text-muted-foreground">
            <li><span className="font-semibold text-foreground">1.</span> اذهب إلى <a href="https://dashboard.render.com" target="_blank" rel="noreferrer" className="text-primary underline">dashboard.render.com</a></li>
            <li><span className="font-semibold text-foreground">2.</span> افتح service <strong>neo-pulse-hub</strong></li>
            <li><span className="font-semibold text-foreground">3.</span> اضغط <strong>Environment</strong> من القائمة الجانبية</li>
            <li><span className="font-semibold text-foreground">4.</span> أضف المتغير المناسب (انظر جدول أدناه) واضغط Save</li>
            <li><span className="font-semibold text-foreground">5.</span> أضف اسم الشبكة إلى <code className="bg-muted px-1 rounded text-xs">AFFILIATE_APPROVED_NETWORKS</code> مثل: <code className="bg-muted px-1 rounded text-xs">amazon-associates,aliexpress</code></li>
          </ol>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="py-2 text-right font-semibold">الشبكة</th>
                  <th className="py-2 text-right font-semibold">اسم المتغير في Render</th>
                  <th className="py-2 text-right font-semibold">مثال على القيمة</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                {[
                  ["Amazon Associates",    "AMAZON_ASSOCIATE_TAG",   "neopulse-20"],
                  ["eBay Partner Network", "EBAY_CAMPAIGN_ID",       "5338956789"],
                  ["AliExpress",           "ALIEXPRESS_PUBLISHER_ID","12345678"],
                  ["Awin",                 "AWIN_PUBLISHER_ID",      "987654"],
                  ["CJ Affiliate",         "CJ_PUBLISHER_ID",        "11223344"],
                  ["Impact.com",           "IMPACT_PARTNER_ID",      "impact_xyz"],
                  ["Rakuten",              "RAKUTEN_PUBLISHER_ID",   "123456"],
                ].map(([net, key, ex]) => (
                  <tr key={key} className="border-b border-border/50">
                    <td className="py-2">{net}</td>
                    <td className="py-2"><code className="bg-muted px-1 rounded">{key}</code></td>
                    <td className="py-2 text-muted-foreground/60">{ex}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>
  );
}
