import { useState } from "react";
import { Sparkles, BarChart3, Lightbulb, Megaphone, ArrowRight } from "lucide-react";
import { AIChatBox, type Message } from "@/components/AIChatBox";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";

const suggestions = [
  "حلل أفضل فرص النمو في المنتجات الحالية",
  "اقترح خطة محتوى عربية لهذا الأسبوع",
  "ما المنتجات التي تحتاج تحسين وصفها أو صورها؟",
  "أنشئ حملة تسويقية لمنتج ذكي مناسب للعائلات",
];

export default function Copilot() {
  const { loading, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const chat = trpc.ai.chat.useMutation();

  const sendMessage = (content: string) => {
    const nextMessages: Message[] = [...messages, { role: "user", content }];
    setMessages(nextMessages);
    chat.mutate(
      { messages: nextMessages.map(({ role, content: value }) => ({ role: role as "user" | "assistant", content: value })) },
      {
        onSuccess: (response) => {
          setMessages((current) => [...current, { role: "assistant", content: response.content }]);
        },
        onError: (error) => {
          setMessages((current) => [
            ...current,
            { role: "assistant", content: `تعذر تنفيذ الطلب حاليًا: ${error.message}` },
          ]);
        },
      }
    );
  };

  if (loading) return <div className="min-h-screen bg-background grid-pattern flex items-center justify-center"><Sparkles className="h-10 w-10 animate-pulse text-primary" /></div>;
  if (!isAuthenticated) {
    return <div className="min-h-screen bg-background grid-pattern flex items-center justify-center p-6"><Card className="max-w-md p-8 text-center space-y-5"><Sparkles className="mx-auto h-12 w-12 text-primary" /><h1 className="text-2xl font-bold">Neo Copilot</h1><p className="text-muted-foreground">سجّل الدخول لاستخدام المساعد الذكي وتحليل بيانات المنصة.</p><Button asChild><a href={getLoginUrl()}>تسجيل الدخول <ArrowRight className="ms-2 h-4 w-4" /></a></Button></Card></div>;
  }

  return (
    <div dir="rtl" className="min-h-screen bg-background grid-pattern">
      <header className="border-b border-border bg-card/70 backdrop-blur">
        <div className="container py-6 flex items-center justify-between gap-4">
          <div><div className="flex items-center gap-3"><div className="rounded-2xl bg-primary/15 p-3"><Sparkles className="h-6 w-6 text-primary" /></div><div><h1 className="text-3xl font-bold text-gradient">Neo Copilot</h1><p className="mt-1 text-sm text-muted-foreground">مركز الذكاء الاصطناعي لاتخاذ قرارات أسرع وأدق</p></div></div></div>
          <div className="hidden md:flex items-center gap-2 text-xs text-emerald-400"><span className="h-2 w-2 rounded-full bg-emerald-400" /> متصل ببيانات المنصة</div>
        </div>
      </header>
      <main className="container py-8 space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          {[{ icon: BarChart3, title: "تحليل الأداء", text: "استخرج فرص النمو من المنتجات والمقالات والحملات." }, { icon: Lightbulb, title: "قرارات ذكية", text: "حوّل البيانات إلى توصيات عملية قابلة للتنفيذ." }, { icon: Megaphone, title: "تسويق أسرع", text: "ولّد أفكار المحتوى والحملات بصوت علامتك التجارية." }].map(({ icon: Icon, title, text }) => <Card key={title} className="border-primary/15 bg-card/70 p-5"><Icon className="mb-4 h-5 w-5 text-primary" /><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-muted-foreground">{text}</p></Card>)}
        </section>
        <AIChatBox messages={messages} onSendMessage={sendMessage} isLoading={chat.isPending} height="min(680px, calc(100vh - 260px))" placeholder="اكتب سؤالك عن المنتجات أو المحتوى أو النمو..." emptyStateMessage="ابدأ بسؤال Neo Copilot عن منصتك" suggestedPrompts={suggestions} />
      </main>
    </div>
  );
}
