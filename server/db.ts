import { eq, desc } from "drizzle-orm";
import fs from "fs";
import { drizzle } from "drizzle-orm/mysql2";
import path from "path";
import { InsertUser, users, automationTasks, InsertAutomationTask, executionLogs, InsertExecutionLog, products, InsertProduct, blogPosts, InsertBlogPost, telegramCampaigns, InsertTelegramCampaign, systemHealth, InsertSystemHealth } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

const projectRoot = process.cwd();

function readLegacyProducts() {
  try {
    const source = JSON.parse(fs.readFileSync(path.join(projectRoot, "products.json"), "utf8"));
    if (!Array.isArray(source)) return [];
    return source.map((item) => ({
      id: String(item.id),
      title: String(item.name?.ar || item.name?.en || item.title || "منتج تقني"),
      price: item.price == null ? null : Math.round(Number(item.price)),
      rating: item.rating == null ? null : String(item.rating),
      reviews: item.reviews == null ? null : Number(item.reviews),
      category: item.category || null,
      image: item.image || null,
      gallery: item.gallery ? JSON.stringify(item.gallery) : null,
      specifications: item.specifications ? JSON.stringify(item.specifications) : null,
      globalPrices: item.global_prices ? JSON.stringify(item.global_prices) : null,
      url: item.affiliate_amazon || item.url || null,
      features: item.features ? JSON.stringify(item.features) : null,
      descriptions: item.descriptions ? JSON.stringify(item.descriptions) : null,
      createdAt: item.updated_at ? new Date(item.updated_at) : new Date(0),
      updatedAt: item.updated_at ? new Date(item.updated_at) : new Date(0),
    }));
  } catch (error) {
    console.warn("[Legacy Catalog] Unable to read products.json:", error);
    return [];
  }
}

function readLegacyBlogs() {
  try {
    const directory = path.join(projectRoot, "blog");
    return fs.readdirSync(directory).filter((file) => file.endsWith(".md")).map((file) => {
      const raw = fs.readFileSync(path.join(directory, file), "utf8");
      const frontmatter = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
      const metadata = Object.fromEntries((frontmatter?.[1] || "").split("\n").flatMap((line) => {
        const separator = line.indexOf(":");
        return separator === -1 ? [] : [[line.slice(0, separator).trim(), line.slice(separator + 1).trim()]];
      }));
      const createdAt = metadata.createdAt ? new Date(metadata.createdAt) : new Date(0);
      return {
        id: file.replace(/\.md$/, ""),
        title: metadata.title || file.replace(/\.md$/, ""),
        language: String(metadata.language || "en").toUpperCase() === "AR" ? "AR" as const : "EN" as const,
        productId: metadata.productId || null,
        content: frontmatter?.[2] || raw,
        slug: metadata.slug || file.replace(/\.md$/, ""),
        keywords: metadata.keywords ? JSON.stringify(metadata.keywords.split(",").map((value) => value.trim())) : null,
        createdAt,
        updatedAt: createdAt,
      };
    });
  } catch (error) {
    console.warn("[Legacy Blog] Unable to read blog files:", error);
    return [];
  }
}

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
  if (!db) return readLegacyProducts();
  const rows = await db.select().from(products).orderBy(desc(products.createdAt));
  return rows.length > 0 ? rows : readLegacyProducts();
}

export async function getProductsByCategory(category: string) {
  const db = await getDb();
  if (!db) return readLegacyProducts().filter((product) => product.category === category);
  const rows = await db.select().from(products).where(eq(products.category, category)).orderBy(desc(products.createdAt));
  return rows.length > 0 ? rows : readLegacyProducts().filter((product) => product.category === category);
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
  if (!db) return readLegacyBlogs();
  const rows = await db.select().from(blogPosts).orderBy(desc(blogPosts.createdAt));
  return rows.length > 0 ? rows : readLegacyBlogs();
}

export async function getBlogPostsByLanguage(language: 'EN' | 'AR') {
  const db = await getDb();
  if (!db) return readLegacyBlogs().filter((post) => post.language === language);
  const rows = await db.select().from(blogPosts).where(eq(blogPosts.language, language)).orderBy(desc(blogPosts.createdAt));
  return rows.length > 0 ? rows : readLegacyBlogs().filter((post) => post.language === language);
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
