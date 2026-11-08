import { describe, expect, it } from "vitest";
import {
  affiliateDisclosure,
  buildAffiliateLink,
  getAffiliateProgram,
  listAffiliatePrograms,
} from "./affiliate-registry";

describe("affiliate registry", () => {
  it("lists only explicitly configured programs", () => {
    const programs = listAffiliatePrograms();
    expect(programs.length).toBeGreaterThanOrEqual(3);
    expect(programs.every(program => program.requiresApproval)).toBe(true);
    expect(programs.every(program => program.status === "pending_approval")).toBe(true);
  });

  it("finds a known program", () => {
    expect(getAffiliateProgram("amazon-associates")?.officialUrl).toContain("amazon");
    expect(getAffiliateProgram("not-a-network")).toBeUndefined();
  });

  it("does not invent tracking links before approval and credentials", () => {
    expect(buildAffiliateLink("amazon-associates", "https://amazon.example/item")).toBeNull();
    expect(buildAffiliateLink("not-a-network", "https://example.com/item")).toBeNull();
    expect(buildAffiliateLink("amazon-associates", "javascript:alert(1)")).toBeNull();
  });

  it("provides an explicit disclosure", () => {
    expect(affiliateDisclosure).toContain("عمولة");
  });
});
