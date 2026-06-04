import { describe, expect, it } from "vitest";
import { getSessionCookieOptions } from "./_core/cookies";
import type { Request } from "express";

function createMockRequest(overrides: Partial<Request> = {}): Request {
  return {
    protocol: "http",
    headers: {},
    hostname: "localhost",
    ...overrides,
  } as unknown as Request;
}

describe("cookies", () => {
  describe("getSessionCookieOptions", () => {
    it("returns secure false for http protocol", () => {
      const req = createMockRequest({ protocol: "http" });
      const options = getSessionCookieOptions(req);

      expect(options.httpOnly).toBe(true);
      expect(options.path).toBe("/");
      expect(options.sameSite).toBe("none");
      expect(options.secure).toBe(false);
    });

    it("returns secure true for https protocol", () => {
      const req = createMockRequest({ protocol: "https" });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(true);
    });

    it("returns secure true when x-forwarded-proto is https", () => {
      const req = createMockRequest({
        protocol: "http",
        headers: { "x-forwarded-proto": "https" },
      });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(true);
    });

    it("returns secure true when x-forwarded-proto is an array containing https", () => {
      const req = createMockRequest({
        protocol: "http",
        headers: { "x-forwarded-proto": ["https", "http"] },
      });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(true);
    });

    it("returns secure false when x-forwarded-proto does not contain https", () => {
      const req = createMockRequest({
        protocol: "http",
        headers: { "x-forwarded-proto": "http" },
      });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(false);
    });

    it("handles comma-separated x-forwarded-proto header", () => {
      const req = createMockRequest({
        protocol: "http",
        headers: { "x-forwarded-proto": "https, http" },
      });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(true);
    });

    it("handles x-forwarded-proto with trailing spaces", () => {
      const req = createMockRequest({
        protocol: "http",
        headers: { "x-forwarded-proto": "  HTTPS  , http" },
      });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(true);
    });

    it("returns secure false when x-forwarded-proto header is missing", () => {
      const req = createMockRequest({
        protocol: "http",
        headers: {},
      });
      const options = getSessionCookieOptions(req);

      expect(options.secure).toBe(false);
    });
  });
});