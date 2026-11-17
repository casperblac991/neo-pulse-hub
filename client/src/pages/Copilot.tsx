import { useState } from "react";
import {
  Sparkles, BarChart3, Lightbulb, Megaphone, ArrowRight, ArrowLeft,
  TrendingUp, Package, FileText, Zap, Star, DollarSign,
} from "lucide-react";
import { AIChatBox, type Message } from "@/components/AIChatBox";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";

const QUICK_ACTIONS = [
  { icon: TrendingUp,  label: "أفضل فرص النمو",        prompt: "حلل بيانات المنصة وأخبرني بأفضل 3 فرص نمو يمكن استغلالها هذا الأسبوع" },
  { icon: Package,     label: "منتجات تحتاج تحسين",    prompt: "أي المنتجات تحتاج تحسين في الوصف أو الصور أو السعر لزيادة المبيعات؟" },
  { icon: FileText,    label: "خطة محتوى أسبوعية",     prompt: "اقترح خطة محتوى عربية لهذا الأسبوع تناسب منصة منتجات ذكية وأفيليت" },
  { icon: Megaphone,   label: "حملة تسويقية جاهزة",    prompt: "أنشئ حملة تسويقية كاملة لمنتج ذكي (نص + عنوان + CTA) مناسبة لإنستغرام وتيليجرام" },
  { icon: DollarSign,  label: "زيادة عمولات الأفيليت", prompt: "كيف أزيد نسبة التحويل في روابط الأفيليت؟ أعطني خطوات عملية محددة" },
  { icon: Star,        label: "SEO للمنتجات",           prompt: "اكتب لي وصفاً محسّناً لـ SEO لأفضل 3 منتجات في الكتالوج مناسب للبحث العربي" },
];

export default function Copilot() {
  const { loading, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const chat = trpc.ai.chat.useMutation();

  const sendMessage = (content: string) => {
    const nextMessages: Message[] = [...messages, { role: "user", content }];
    setMessages(nextMessages);
    chat.mutate(
      { messages: nextMessages.map(({ role, content: v }) => ({ role: role as "user" | "assistant", content: v })) },
      {
        onSuccess: res => setMessages(cur => [...cur, { role: "assistant", content: res.content }]),
        onError: err => setMessages(cur => [...cur, { role: "assistant", content: `تعذر تنفيذ الطلب: ${err.message}` }]),
      }
    );
  };

  if (loading) return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <Sparkles className="h-10 w-10 animate-pulse text-primary" />
    </div>
  );

  if (!isAuthenticated) return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="max-w-md p-8 text-center space-y-5">
        <div className="mx-auto rounded-2xl bg-primary/15 p-4 w-fit"><Sparkles className="h-10 w-10 text-primary" /></div>
        <h1 className="text-2xl font-bold">Neo Copilot</h1>
        <p className="text-muted-foreground text-sm leading-7">المساعد الذكي المتصل ببيانات منصتك — يحلل المنتجات، يقترح المحتوى، ويساعدك تكسب أكثر من الأفيليت.</p>
        <Button asChild className="w-full">
          <a href={getLoginUrl()}>تسجيل الدخول <ArrowRight className="ms-2 h-4 w-4" /></a>
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
            <a href="/" className="text-muted-foreground hover:text-primary transition-colors"><ArrowLeft className="h-5 w-5" /></a>
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-primary/15 p-2"><Sparkles className="h-5 w-5 text-primary" /></div>
              <div>
                <h1 className="text-xl font-bold">Neo Copilot</h1>
                <p className="text-xs text-muted-foreground">مساعد ذكي متصل ببيانات منصتك</p>
              </div>
            </div>
          </div>
          <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/20">
            <span className="ml-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 inline-block" />
            متصل بالبيانات
          </Badge>
        </div>
      </header>

      <main className="container py-6 space-y-6">
        {/* Capabilities */}
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            { icon: BarChart3, title: "تحليل البيانات",   text: "يقرأ كتالوج المنتجات والمقالات ويستخرج فرص النمو" },
            { icon: Lightbulb, title: "قرارات ذكية",      text: "توصيات عملية للأفيليت والمحتوى والتسعير" },
            { icon: Megaphone, title: "محتوى جاهز",       text: "نصوص تسويقية وSEO وحملات بصوتك" },
          ].map(({ icon: Icon, title, text }) => (
            <Card key={title} className="border-primary/15 bg-card/70 p-4">
              <Icon className="mb-3 h-5 w-5 text-primary" />
              <h2 className="font-semibold text-sm">{title}</h2>
              <p className="mt-1 text-xs leading-5 text-muted-foreground">{text}</p>
            </Card>
          ))}
        </div>

        {/* Quick actions */}
        {messages.length === 0 && (
          <div>
            <p className="text-sm text-muted-foreground mb-3">إجراءات سريعة:</p>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {QUICK_ACTIONS.map(({ icon: Icon, label, prompt }) => (
                <button
                  key={label}
                  onClick={() => sendMessage(prompt)}
                  disabled={chat.isPending}
                  className="flex items-center gap-3 rounded-xl border border-border bg-card/70 p-3 text-right transition hover:border-primary/40 hover:bg-card disabled:opacity-50"
                >
                  <div className="rounded-lg bg-primary/10 p-2 shrink-0"><Icon className="h-4 w-4 text-primary" /></div>
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat */}
        <AIChatBox
          messages={messages}
          onSendMessage={sendMessage}
          isLoading={chat.isPending}
          height="min(640px, calc(100vh - 320px))"
          placeholder="اسأل عن المنتجات، المحتوى، الأفيليت، التحليل..."
          emptyStateMessage="Neo Copilot جاهز — اختر إجراءاً أو اكتب سؤالك"
          suggestedPrompts={[
            "ما أفضل 5 منتجات للترويج لها؟",
            "اقترح عنواناً لمقال SEO عربي",
            "كيف أزيد دخل الأفيليت؟",
            "حلل أداء المنصة الحالي",
          ]}
        />
      </main>
    </div>
  );
}
