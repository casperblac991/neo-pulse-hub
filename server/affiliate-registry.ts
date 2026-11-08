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
  "amazon-associates": "AMAZON_ASSOCIATE_TAG",
  "ebay-partner-network": "EBAY_CAMPAIGN_ID",
  awin: "AWIN_PUBLISHER_ID",
  "cj-affiliate": "CJ_PUBLISHER_ID",
  impact: "IMPACT_PARTNER_ID",
  "rakuten-advertising": "RAKUTEN_PUBLISHER_ID",
  aliexpress: "ALIEXPRESS_PUBLISHER_ID",
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
    credentialConfigured: Boolean(process.env[environmentKeys[program.id]]),
    credentialVariable: environmentKeys[program.id],
  }));
}

export function getPublicAffiliateStatus() {
  const approved = new Set(
    (process.env.AFFILIATE_APPROVED_NETWORKS || "")
      .split(",")
      .map(value => value.trim())
      .filter(Boolean),
  );
  return programs.map(program => ({
    id: program.id,
    name: program.name,
    status: approved.has(program.id) ? "approved" : program.status,
    credentialConfigured: Boolean(process.env[environmentKeys[program.id]]),
    markets: program.markets,
  }));
}

export function buildAffiliateLink(network: string, destination: string): string | null {
  const program = getAffiliateProgram(network);
  if (!program || program.status !== "approved") return null;

  let url: URL;
  try {
    url = new URL(destination);
  } catch {
    return null;
  }
  if (url.protocol !== "https:") return null;

  const credential = process.env[environmentKeys[program.id]];
  if (!credential) return null;

  // Network-specific link generation must be implemented only after the account
  // is approved and its current official API/link rules are configured.
  // Never guess tracking parameters or expose credentials to the browser.
  return null;
}

export const affiliateDisclosure =
  "قد يحصل Neo Pulse Hub على عمولة عند إتمام عملية شراء مؤهلة عبر هذا الرابط.";
