import { describe, expect, it } from "vitest";
import { initTRPC, TRPCError } from "@trpc/server";
import { UNAUTHED_ERR_MSG, NOT_ADMIN_ERR_MSG } from "@shared/const";
import type { TrpcContext } from "./context";

const t = initTRPC.context<TrpcContext>().create();

const requireUser = t.middleware(async opts => {
  const { ctx, next } = opts;

  if (!ctx.user) {
    throw new TRPCError({ code: "UNAUTHORIZED", message: UNAUTHED_ERR_MSG });
  }

  return next({
    ctx: {
      ...ctx,
      user: ctx.user,
    },
  });
});

const protectedProcedure = t.procedure.use(requireUser);

const adminProcedure = t.procedure.use(
  t.middleware(async opts => {
    const { ctx, next } = opts;

    if (!ctx.user || ctx.user.role !== 'admin') {
      throw new TRPCError({ code: "FORBIDDEN", message: NOT_ADMIN_ERR_MSG });
    }

    return next({
      ctx: {
        ...ctx,
        user: ctx.user,
      },
    });
  }),
);

function createMockContext(user: TrpcContext["user"]): TrpcContext {
  return {
    user,
    req: {} as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };
}

describe("trpc middleware", () => {
  describe("protectedProcedure middleware", () => {
    it("allows request when user is authenticated", async () => {
      const ctx = createMockContext({
        id: 1,
        openId: "user-123",
        email: "user@example.com",
        name: "Test User",
        loginMethod: "manus",
        role: "user",
        createdAt: new Date(),
        updatedAt: new Date(),
        lastSignedIn: new Date(),
      });

      const caller = t.router({
        protected: protectedProcedure.query(({ ctx }) => ctx.user),
      }).createCaller(ctx);

      const result = await caller.protected();
      expect(result).toBeDefined();
      expect(result.openId).toBe("user-123");
    });

    it("throws UNAUTHORIZED when user is null", async () => {
      const ctx = createMockContext(null);

      const caller = t.router({
        protected: protectedProcedure.query(({ ctx }) => ctx.user),
      }).createCaller(ctx);

      await expect(caller.protected()).rejects.toMatchObject({
        code: "UNAUTHORIZED",
        message: UNAUTHED_ERR_MSG,
      });
    });
  });

  describe("adminProcedure middleware", () => {
    it("allows request when user is admin", async () => {
      const ctx = createMockContext({
        id: 1,
        openId: "admin-123",
        email: "admin@example.com",
        name: "Admin User",
        loginMethod: "manus",
        role: "admin",
        createdAt: new Date(),
        updatedAt: new Date(),
        lastSignedIn: new Date(),
      });

      const caller = t.router({
        admin: adminProcedure.query(({ ctx }) => ctx.user),
      }).createCaller(ctx);

      const result = await caller.admin();
      expect(result).toBeDefined();
      expect(result.role).toBe("admin");
    });

    it("throws FORBIDDEN when user is not admin", async () => {
      const ctx = createMockContext({
        id: 1,
        openId: "user-123",
        email: "user@example.com",
        name: "Test User",
        loginMethod: "manus",
        role: "user",
        createdAt: new Date(),
        updatedAt: new Date(),
        lastSignedIn: new Date(),
      });

      const caller = t.router({
        admin: adminProcedure.query(({ ctx }) => ctx.user),
      }).createCaller(ctx);

      await expect(caller.admin()).rejects.toMatchObject({
        code: "FORBIDDEN",
        message: NOT_ADMIN_ERR_MSG,
      });
    });

    it("throws FORBIDDEN when user is null", async () => {
      const ctx = createMockContext(null);

      const caller = t.router({
        admin: adminProcedure.query(({ ctx }) => ctx.user),
      }).createCaller(ctx);

      await expect(caller.admin()).rejects.toMatchObject({
        code: "FORBIDDEN",
        message: NOT_ADMIN_ERR_MSG,
      });
    });
  });
});