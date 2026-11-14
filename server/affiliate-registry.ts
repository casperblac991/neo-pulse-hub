export type AffiliateNetwork =
  | "amazon-associates"
  | "ebay-partner-network"
  | "awin"
  | "cj-affiliate"
  | "impact"
  | "rakuten-advertising"
  | "aliexpress";

export type AffiliateProgramStatus = "pending_approval" | "approved" | "disabled";

export type AffiliateProgram = {
  id: AffiliateNetwork;
  name: string;
  officialUrl: string;
  status: AffiliateProgramStatus;
  markets: string[];
  requiresApproval: boolean;
  disclosureRequired: boolean;
};

const programs: AffiliateProgram[] = [
  {
    id: "amazon-associates",
    name: "Amazon Associates",
    officialUrl: "https://affiliate-program.amazon.com/",
    status: "pending_approval",
    markets: ["AE", "SA", "ES", "US", "GB", "DE", "FR", "IT"],
    requiresApproval: true,
    disclosureRequired: true,
  },
  {
    id: "ebay-partner-network",
    name: "eBay Partner Network",
    officialUrl: "https://partnernetwork.ebay.com/",
    status: "pending_approval",
    markets: ["ES", "US", "GB", "DE", "FR", "IT", "CA", "AU"],
    requiresApproval: true,
    disclosureRequired: true,
  },
  {
    id: "awin",
    name: "Awin",
    officialUrl: "https://www.awin.com/",
    status: "pending_approval",
    markets: ["ES", "GB", "DE", "FR", "IT", "NL", "US"],
    requiresApproval: true,
    disclosureRequired: true,
  },
  {
    id: "cj-affiliate",
    name: "CJ Affiliate",
    officialUrl: "https://www.cj.com/",
    status: "pending_approval",
    markets: ["US", "CA", "GB", "ES", "DE", "FR"],
    requiresApproval: true,
    disclosureRequired: true,
  },
  {
    id: "impact",
    name: "impact.com",
    officialUrl: "https://impact.com/partners/affiliate-partners/",
    status: "pending_approval",
    markets: ["US", "GB", "ES", "DE", "FR", "AE", "SA"],
    requiresApproval: true,
    disclosureRequired: true,
  },
  {
    id: "rakuten-advertising",
    name: "Rakuten Advertising",
    officialUrl: "https://rakutenadvertising.com/affiliate/",
    status: "pending_approval",
    markets: ["US", "CA", "GB", "ES", "DE", "FR", "JP", "AU"],
    requiresApproval: true,
    disclosureRequired: true,
  },
  {
    id: "aliexpress",
    name: "AliExpress Affiliate Program",
    officialUrl: "https://portals.aliexpress.com/",
    status: "pending_approval",
    markets: ["GLOBAL"],
    requiresApproval: true,
    disclosureRequired: true,
  },
];

const environmentKeys: Record<AffiliateNetwork, string> = {
  "amazon-associates":   "AMAZON_ASSOCIATE_TAG",
  "ebay-partner-network":"EBAY_CAMPAIGN_ID",
  "awin":                "AWIN_PUBLISHER_ID",
  "cj-affiliate":        "CJ_PUBLISHER_ID",
  "impact":              "IMPACT_PARTNER_ID",
  "rakuten-advertising": "RAKUTEN_PUBLISHER_ID",
  "aliexpress":          "ALIEXPRESS_PUBLISHER_ID",
};

export function listAffiliatePrograms(): AffiliateProgram[] {
  return programs.map(program => ({ ...program, markets: [...program.markets] }));
}

export function getAffiliateProgram(id: string): AffiliateProgram | undefined {
  return programs.find(program => program.id === id);
}

export function getAffiliateReadiness() {
  return programs.map(program => ({
    ...program,
    credentialConfigured: Boolean(process.env[environmentKeys[program.id as AffiliateNetwork]]),
    credentialVariable: environmentKeys[program.id as AffiliateNetwork],
  }));
}

export function getPublicAffiliateStatus() {
  const approved = new Set(
    (process.env.AFFILIATE_APPROVED_NETWORKS || "")
      .split(",")
      .map(v => v.trim())
      .filter(Boolean),
  );
  return programs.map(program => ({
    id: program.id,
    name: program.name,
    officialUrl: program.officialUrl,
    status: approved.has(program.id) ? "approved" : program.status,
    credentialConfigured: Boolean(process.env[environmentKeys[program.id as AffiliateNetwork]]),
    markets: program.markets,
  }));
}

/**
 * يبني رابط أفلييت حقيقي بعد تفعيل الشبكة وإضافة المعرّف في Render.
 * يُرجع null إذا لم تكن الشبكة مفعّلة أو المعرّف غير موجود.
 */
export function buildAffiliateLink(network: string, destination: string): string | null {
  const program = getAffiliateProgram(network);
  if (!program) return null;

  const approved = new Set(
    (process.env.AFFILIATE_APPROVED_NETWORKS || "").split(",").map(v => v.trim()).filter(Boolean),
  );
  if (!approved.has(network)) return null;

  let url: URL;
  try {
    url = new URL(destination);
  } catch {
    return null;
  }
  if (url.protocol !== "https:") return null;

  const credential = process.env[environmentKeys[program.id]];
  if (!credential) return null;

  // ── Amazon Associates ──────────────────────────────────
  if (network === "amazon-associates") {
    url.searchParams.set("tag", credential);
    url.searchParams.set("linkCode", "ogi");
    return url.toString();
  }

  // ── AliExpress Portals ─────────────────────────────────
  if (network === "aliexpress") {
    return `https://s.click.aliexpress.com/e/_affiliateLink?pid=${credential}&url=${encodeURIComponent(destination)}`;
  }

  // ── eBay Partner Network ───────────────────────────────
  if (network === "ebay-partner-network") {
    return `https://rover.ebay.com/rover/1/${credential}/1/?ff3=4&toolid=10001&campid=${credential}&customid=&lgeo=1&vectorid=229466&item=${encodeURIComponent(destination)}`;
  }

  // ── Awin deep-link ─────────────────────────────────────
  if (network === "awin") {
    return `https://www.awin1.com/cread.php?awinmid=&awinaffid=${credential}&linkid=&p=${encodeURIComponent(destination)}`;
  }

  // ── CJ Affiliate ──────────────────────────────────────
  if (network === "cj-affiliate") {
    return `https://www.tkqlhce.com/click-${credential}-0?url=${encodeURIComponent(destination)}`;
  }

  // Other networks: return destination unchanged until integrated
  return destination;
}

export const affiliateDisclosure =
  "قد يحصل Neo Pulse Hub على عمولة عند إتمام عملية شراء مؤهلة عبر هذا الرابط. السعر والشحن والضمان يحددها المتجر الشريك مباشرةً.";
