import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { z } from "zod";
import { invokeLLM } from "./_core/llm";
import {
  getAutomationTasks,
  getAutomationTaskByName,
  updateAutomationTask,
  getExecutionLogs,
  getExecutionLogsByTask,
  getAllProducts,
  getProductsByCategory,
  getAllBlogPosts,
  getBlogPostsByLanguage,
  getAllTelegramCampaigns,
  getSystemHealth,
  getSystemHealthByService,
} from "./db";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Automation Dashboard APIs
  automation: router({
    tasks: protectedProcedure.query(async () => {
      return await getAutomationTasks();
    }),
    taskByName: protectedProcedure.input(z.string()).query(async ({ input }) => {
      return await getAutomationTaskByName(input);
    }),
    updateTask: protectedProcedure
      .input(z.object({ name: z.string(), data: z.any() }))
      .mutation(async ({ input }) => {
        await updateAutomationTask(input.name, input.data);
        return { success: true };
      }),
  }),

  logs: router({
    recent: protectedProcedure.input(z.number().optional()).query(async ({ input }) => {
      return await getExecutionLogs(input || 100);
    }),
    byTask: protectedProcedure
      .input(z.object({ taskName: z.string(), limit: z.number().optional() }))
      .query(async ({ input }) => {
        return await getExecutionLogsByTask(input.taskName, input.limit || 50);
      }),
  }),

  products: router({
    all: protectedProcedure.query(async () => {
      return await getAllProducts();
    }),
    byCategory: protectedProcedure.input(z.string()).query(async ({ input }) => {
      return await getProductsByCategory(input);
    }),
  }),

  blogs: router({
    all: protectedProcedure.query(async () => {
      return await getAllBlogPosts();
    }),
    byLanguage: protectedProcedure.input(z.enum(["EN", "AR"])).query(async ({ input }) => {
      return await getBlogPostsByLanguage(input);
    }),
  }),

  campaigns: router({
    all: protectedProcedure.query(async () => {
      return await getAllTelegramCampaigns();
    }),
  }),

  ai: router({
    chat: protectedProcedure
      .input(
        z.object({
          messages: z.array(
            z.object({
              role: z.enum(["user", "assistant"]),
              content: z.string().min(1).max(6000),
            })
          ).min(1).max(20),
        })
      )
      .mutation(async ({ input }) => {
        const [products, blogs] = await Promise.all([
          getAllProducts(),
          getAllBlogPosts(),
        ]);
        const productContext = products
          .slice(0, 40)
          .map((p) => `${p.title} | الفئة: ${p.category || "غير محدد"} | السعر: ${p.price || "غير محدد"} | التقييم: ${p.rating || "غير محدد"}`)
          .join("\\n");
        const blogContext = blogs
          .slice(0, 20)
          .map((b) => `${b.title} (${b.language})`)
          .join("\\n");

        const result = await invokeLLM({
          messages: [
            {
              role: "system",
              content: `أنت Neo Copilot، مساعد تشغيل وتحليل لمنصة Neo Pulse Hub المتخصصة في منتجات التقنية والذكاء الاصطناعي. أجب بالعربية ما لم يطلب المستخدم غير ذلك. كن عمليًا ودقيقًا، ولا تختلق أسعارًا أو مخزونًا أو أرقامًا غير موجودة. يمكنك تحليل البيانات التالية واقتراح تحسينات تسويقية ومحتوى ومنتجات، لكن لا تنفذ شراءً أو نشرًا خارجيًا دون تأكيد المستخدم.\\n\\nالمنتجات المتاحة:\\n${productContext || "لا توجد بيانات منتجات حالياً"}\\n\\nالمقالات المتاحة:\\n${blogContext || "لا توجد مقالات حالياً"}`,
            },
            ...input.messages.map((message) => ({
              role: message.role as "user" | "assistant",
              content: message.content,
            })),
          ],
          maxTokens: 1600,
        });

        const content = result.choices?.[0]?.message?.content;
        if (typeof content !== "string" || !content.trim()) {
          throw new Error("لم يتمكن المساعد من إنشاء رد صالح");
        }
        return { content };
      }),
  }),

  health: router({
    all: protectedProcedure.query(async () => {
      return await getSystemHealth();
    }),
    byService: protectedProcedure.input(z.string()).query(async ({ input }) => {
      return await getSystemHealthByService(input);
    }),
  }),
});

export type AppRouter = typeof appRouter;
