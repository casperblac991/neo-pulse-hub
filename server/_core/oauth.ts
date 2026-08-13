import { COOKIE_NAME, ONE_YEAR_MS } from "@shared/const";
import type { Express, Request, Response } from "express";
import * as db from "../db";
import { getSessionCookieOptions } from "./cookies";
import { sdk } from "./sdk";

function getQueryParam(req: Request, key: string): string | undefined {
  const value = req.query[key];
  return typeof value === "string" ? value : undefined;
}

export function registerOAuthRoutes(app: Express) {
  app.get("/api/oauth/callback", async (req: Request, res: Response) => {
    const code = getQueryParam(req, "code");
    const state = getQueryParam(req, "state");

    if (!code || !state) {
      res.status(400).json({ error: "code and state are required" });
      return;
    }

    try {
      const tokenResponse = await sdk.exchangeCodeForToken(code, state);
      const userInfo = await sdk.getUserInfo(tokenResponse.accessToken);

      if (!userInfo.openId) {
        res.status(400).json({ error: "openId missing from user info" });
        return;
      }

      await db.upsertUser({
        openId: userInfo.openId,
        name: userInfo.name || null,
        email: userInfo.email ?? null,
        loginMethod: userInfo.loginMethod ?? userInfo.platform ?? null,
        lastSignedIn: new Date(),
      });

      // Sync to marketing list if email exists
      if (userInfo.email) {
        try {
          const { execSync } = require('child_process');
          const payload = JSON.stringify({
            name: userInfo.name || 'User',
            email: userInfo.email,
            source: 'oauth_login',
            timestamp: new Date().toISOString()
          });
          // Call the existing subscription logic via a small script or direct file write
          const subscribersPath = '/home/ubuntu/neo-pulse-hub/data/subscribers.json';
          const fs = require('fs');
          if (fs.existsSync(subscribersPath)) {
            const data = JSON.parse(fs.readFileSync(subscribersPath, 'utf8'));
            if (!data.subscribers.find(s => s.email === userInfo.email)) {
                data.subscribers.push(JSON.parse(payload));
                fs.writeFileSync(subscribersPath, JSON.stringify(data, null, 2));
                console.log(`[OAuth] Synced new subscriber: ${userInfo.email}`);
            }
          }
        } catch (e) {
          console.error("[OAuth] Marketing sync failed", e);
        }
      }

      const sessionToken = await sdk.createSessionToken(userInfo.openId, {
        name: userInfo.name || "",
        expiresInMs: ONE_YEAR_MS,
      });

      const cookieOptions = getSessionCookieOptions(req);
      res.cookie(COOKIE_NAME, sessionToken, { ...cookieOptions, maxAge: ONE_YEAR_MS });

      res.redirect(302, "/");
    } catch (error) {
      console.error("[OAuth] Callback failed", error);
      res.status(500).json({ error: "OAuth callback failed" });
    }
  });
}
