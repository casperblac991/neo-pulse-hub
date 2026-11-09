import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { registerStorageProxy } from "./storageProxy";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";
import { affiliateDisclosure, getPublicAffiliateStatus, listAffiliatePrograms } from "../affiliate-registry";

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startServer() {
  console.log(`[neo-pulse] booting production server; PORT=${process.env.PORT || "3000"}`);
  const app = express();
  const server = createServer(app);
  // Keep API payloads bounded; binary uploads should use object storage directly.
  app.use(express.json({ limit: "1mb", strict: true }));
  app.use(express.urlencoded({ limit: "100kb", extended: false, parameterLimit: 100 }));
  registerStorageProxy(app);
  registerOAuthRoutes(app);
  app.get("/healthz", (_req, res) => {
    res.status(200).json({
      status: "ok",
      service: "neo-pulse-hub",
      environment: process.env.NODE_ENV || "development",
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    });
  });
  app.get("/api/affiliate/programs", (_req, res) => {
    res.status(200).json({
      success: true,
      programs: listAffiliatePrograms(),
      disclosure: affiliateDisclosure,
    });
  });
  app.get("/api/affiliate/status", (_req, res) => {
    res.status(200).json({
      success: true,
      networks: getPublicAffiliateStatus(),
      note: "Credential presence is reported without exposing secret values. Network activation still requires explicit approval.",
    });
  });
  const siteUrl = (process.env.SITE_URL || "https://neo-pulse-hub.it.com").replace(/\/$/, "");
  app.get("/robots.txt", (_req, res) => {
    res.type("text/plain").send([
      "User-agent: *",
      "Allow: /",
      "Disallow: /api/",
      "Disallow: /copilot",
      `Sitemap: ${siteUrl}/sitemap.xml`,
      "",
    ].join("\n"));
  });
  app.get("/sitemap.xml", (_req, res) => {
    const publicRoutes = ["/", "/products", "/blogs", "/videos", "/affiliate-programs"];
    const urls = publicRoutes
      .map((route) => `  <url><loc>${siteUrl}${route}</loc><changefreq>${route === "/" ? "daily" : "weekly"}</changefreq><priority>${route === "/" ? "1.0" : "0.7"}</priority></url>`)
      .join("\n");
    res.type("application/xml").send(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>`);
  });
  // tRPC API
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
