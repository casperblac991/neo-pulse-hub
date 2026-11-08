const credentials = {
  "amazon-associates": ["AMAZON_ASSOCIATE_TAG", "AMAZON_PAAPI_ACCESS_KEY", "AMAZON_PAAPI_SECRET_KEY"],
  "ebay-partner-network": ["EBAY_CAMPAIGN_ID", "EBAY_CLIENT_ID", "EBAY_CLIENT_SECRET"],
  awin: ["AWIN_PUBLISHER_ID", "AWIN_API_TOKEN"],
  "cj-affiliate": ["CJ_PUBLISHER_ID", "CJ_API_TOKEN"],
  impact: ["IMPACT_PARTNER_ID", "IMPACT_API_TOKEN"],
  "rakuten-advertising": ["RAKUTEN_PUBLISHER_ID", "RAKUTEN_API_TOKEN"],
  aliexpress: ["ALIEXPRESS_PUBLISHER_ID", "ALIEXPRESS_API_TOKEN"],
};

const approved = new Set(
  (process.env.AFFILIATE_APPROVED_NETWORKS || "")
    .split(",")
    .map(value => value.trim())
    .filter(Boolean),
);

const report = Object.entries(credentials).map(([network, keys]) => ({
  network,
  approved: approved.has(network),
  configured: keys.every(key => Boolean(process.env[key])),
  missing: keys.filter(key => !process.env[key]),
}));

console.log(JSON.stringify({
  ok: true,
  networks: report,
  warning: "This check does not call any provider API and never prints secret values.",
}, null, 2));
