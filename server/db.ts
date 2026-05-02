import { eq, desc } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, users, automationTasks, InsertAutomationTask, executionLogs, InsertExecutionLog, products, InsertProduct, blogPosts, InsertBlogPost, telegramCampaigns, InsertTelegramCampaign, systemHealth, InsertSystemHealth } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

/**
 * Automation Tasks Queries
 */
export async function getAutomationTasks() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(automationTasks).orderBy(automationTasks.name);
}

export async function getAutomationTaskByName(name: string) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(automationTasks).where(eq(automationTasks.name, name)).limit(1);
  return result[0];
}

export async function updateAutomationTask(name: string, data: Partial<InsertAutomationTask>) {
  const db = await getDb();
  if (!db) return;
  await db.update(automationTasks).set(data).where(eq(automationTasks.name, name));
}

/**
 * Execution Logs Queries
 */
export async function getExecutionLogs(limit: number = 100) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(executionLogs).orderBy(desc(executionLogs.timestamp)).limit(limit);
}

export async function getExecutionLogsByTask(taskName: string, limit: number = 50) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(executionLogs).where(eq(executionLogs.taskName, taskName)).orderBy(desc(executionLogs.timestamp)).limit(limit);
}

export async function createExecutionLog(data: InsertExecutionLog) {
  const db = await getDb();
  if (!db) return;
  await db.insert(executionLogs).values(data);
}

/**
 * Products Queries
 */
export async function getAllProducts() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(products).orderBy(desc(products.createdAt));
}

export async function getProductsByCategory(category: string) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(products).where(eq(products.category, category)).orderBy(desc(products.createdAt));
}

export async function createProduct(data: InsertProduct) {
  const db = await getDb();
  if (!db) return;
  await db.insert(products).values(data).onDuplicateKeyUpdate({ set: data });
}

/**
 * Blog Posts Queries
 */
export async function getAllBlogPosts() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(blogPosts).orderBy(desc(blogPosts.createdAt));
}

export async function getBlogPostsByLanguage(language: 'EN' | 'AR') {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(blogPosts).where(eq(blogPosts.language, language)).orderBy(desc(blogPosts.createdAt));
}

export async function createBlogPost(data: InsertBlogPost) {
  const db = await getDb();
  if (!db) return;
  await db.insert(blogPosts).values(data).onDuplicateKeyUpdate({ set: data });
}

/**
 * Telegram Campaigns Queries
 */
export async function getAllTelegramCampaigns() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(telegramCampaigns).orderBy(desc(telegramCampaigns.timestamp));
}

export async function createTelegramCampaign(data: InsertTelegramCampaign) {
  const db = await getDb();
  if (!db) return;
  await db.insert(telegramCampaigns).values(data);
}

/**
 * System Health Queries
 */
export async function getSystemHealth() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(systemHealth).orderBy(desc(systemHealth.lastCheck));
}

export async function getSystemHealthByService(service: string) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(systemHealth).where(eq(systemHealth.service, service)).orderBy(desc(systemHealth.lastCheck)).limit(1);
  return result[0];
}

export async function updateSystemHealth(service: string, data: Partial<InsertSystemHealth>) {
  const db = await getDb();
  if (!db) return;
  const existing = await getSystemHealthByService(service);
  if (existing) {
    await db.update(systemHealth).set(data).where(eq(systemHealth.id, existing.id));
  } else {
    await db.insert(systemHealth).values({ service, ...data } as InsertSystemHealth);
  }
}

// TODO: add additional feature queries here as your schema grows.
