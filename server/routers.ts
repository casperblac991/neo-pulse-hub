import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { z } from "zod";
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
