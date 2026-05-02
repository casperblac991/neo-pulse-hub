import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Automation Tasks Table - Tracks scheduled tasks
 */
export const automationTasks = mysqlTable("automation_tasks", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 64 }).notNull().unique(), // fetch-products, generate-content, publish-social, sync-github
  status: mysqlEnum("status", ["running", "success", "error", "pending", "disabled"]).default("pending").notNull(),
  lastRun: timestamp("lastRun"),
  nextRun: timestamp("nextRun"),
  lastError: text("lastError"),
  successCount: int("successCount").default(0).notNull(),
  errorCount: int("errorCount").default(0).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type AutomationTask = typeof automationTasks.$inferSelect;
export type InsertAutomationTask = typeof automationTasks.$inferInsert;

/**
 * Execution Logs Table - Stores detailed logs for each task execution
 */
export const executionLogs = mysqlTable("execution_logs", {
  id: int("id").autoincrement().primaryKey(),
  taskId: int("taskId").notNull(),
  taskName: varchar("taskName", { length: 64 }).notNull(),
  status: mysqlEnum("status", ["success", "error", "warning", "info"]).notNull(),
  message: text("message"),
  details: text("details"), // JSON stringified details
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  duration: int("duration"), // milliseconds
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type ExecutionLog = typeof executionLogs.$inferSelect;
export type InsertExecutionLog = typeof executionLogs.$inferInsert;

/**
 * Products Table - Stores fetched products
 */
export const products = mysqlTable("products", {
  id: varchar("id", { length: 64 }).primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  price: int("price"),
  rating: varchar("rating", { length: 10 }),
  reviews: int("reviews"),
  category: varchar("category", { length: 64 }),
  image: text("image"),
  url: text("url"),
  features: text("features"), // JSON array
  descriptions: text("descriptions"), // JSON with en/ar
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Product = typeof products.$inferSelect;
export type InsertProduct = typeof products.$inferInsert;

/**
 * Blog Posts Table - Stores generated blog content
 */
export const blogPosts = mysqlTable("blog_posts", {
  id: varchar("id", { length: 64 }).primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  language: mysqlEnum("language", ["EN", "AR"]).notNull(),
  productId: varchar("productId", { length: 64 }),
  content: text("content"),
  slug: varchar("slug", { length: 255 }),
  keywords: text("keywords"), // JSON array
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type BlogPost = typeof blogPosts.$inferSelect;
export type InsertBlogPost = typeof blogPosts.$inferInsert;

/**
 * Telegram Campaigns Table - Tracks sent campaigns
 */
export const telegramCampaigns = mysqlTable("telegram_campaigns", {
  id: varchar("id", { length: 64 }).primaryKey(),
  message: text("message").notNull(),
  status: mysqlEnum("status", ["sent", "failed", "pending"]).default("pending").notNull(),
  deliveryStatus: mysqlEnum("deliveryStatus", ["delivered", "failed", "pending"]).default("pending").notNull(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  error: text("error"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type TelegramCampaign = typeof telegramCampaigns.$inferSelect;
export type InsertTelegramCampaign = typeof telegramCampaigns.$inferInsert;

/**
 * System Health Table - Tracks service status
 */
export const systemHealth = mysqlTable("system_health", {
  id: int("id").autoincrement().primaryKey(),
  service: varchar("service", { length: 64 }).notNull(), // openclaw, openai, telegram, amazon
  status: mysqlEnum("status", ["online", "offline", "degraded", "unknown"]).default("unknown").notNull(),
  lastCheck: timestamp("lastCheck").defaultNow().notNull(),
  details: text("details"), // JSON with response time, error message, etc
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type SystemHealth = typeof systemHealth.$inferSelect;
export type InsertSystemHealth = typeof systemHealth.$inferInsert;