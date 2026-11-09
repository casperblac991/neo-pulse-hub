import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, Link2, Loader2, ShieldCheck } from "lucide-react";

type Program = {
  id: string;
  name: string;
  officialUrl: string;
  status: string;
  credentialConfigured: boolean;
  markets: string[];
};

export default function AffiliatePrograms() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [disclosure, setDisclosure] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/affiliate/programs")
      .then((response) => response.json())
      .then((payload) => {
        setPrograms(payload.programs ?? []);
        setDisclosure(payload.disclosure ?? "");
      })
      .catch(() => setPrograms([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div dir="rtl" className="min-h-screen bg-background grid-pattern">
      <header className="border-b border-border bg-card/70 backdrop-blur">
        <div className="container py-8">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-primary/15 p-3"><Link2 className="h-6 w-6 text-primary" /></div>
            <div>
              <h1 className="text-3xl font-bold text-gradient">شبكات الأفلييت العالمية</h1>
              <p className="mt-1 text-sm text-muted-foreground">روابط رسمية فقط، وبيانات اعتماد تبقى في Render ولا تظهر للزوار</p>
            </div>
          </div>
        </div>
      </header>
      <main className="container space-y-6 py-8">
        <section className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-6">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-emerald-400" />
            <div>
              <h2 className="font-semibold">كيف تعمل المنظومة؟</h2>
              <p className="mt-2 text-sm leading-7 text-muted-foreground">
                لا يمكن جمع كل الشركات أو إنشاء حسابات نيابة عنك تلقائيًا. كل شبكة تحتاج قبولًا رسميًا وشروطًا خاصة. بعد قبولك، نضيف معرف الناشر أو API الرسمي إلى Render، ثم نفعّل الشبكة بموافقة صريحة ونحوّل روابط المنتجات من خلال قواعدها الرسمية فقط.
              </p>
              {disclosure && <p className="mt-3 text-xs text-muted-foreground">{disclosure}</p>}
            </div>
          </div>
        </section>
        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {programs.map((program) => (
              <Card key={program.id} className="border-primary/20 bg-card/80">
                <CardHeader>
                  <div className="flex items-start justify-between gap-3">
                    <CardTitle className="text-lg">{program.name}</CardTitle>
                    <Badge className={program.status === "approved" ? "status-success" : "status-pending"}>
                      {program.status === "approved" ? "مفعّلة" : "بانتظار القبول"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">الأسواق: {program.markets.join("، ")}</p>
                  <p className="mt-3 text-xs text-muted-foreground">
                    حالة بيانات الاعتماد: {program.credentialConfigured ? "موجودة في الخادم" : "لم تتم إضافتها بعد"}
                  </p>
                  <Button asChild variant="outline" className="mt-5 w-full gap-2">
                    <a href={program.officialUrl} target="_blank" rel="noreferrer">
                      فتح الموقع الرسمي <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
