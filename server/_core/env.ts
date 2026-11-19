export const ENV = {
  appId:        process.env.VITE_APP_ID ?? "",
  cookieSecret: process.env.JWT_SECRET ?? "",
  databaseUrl:  process.env.DATABASE_URL ?? "",
  oAuthServerUrl: process.env.OAUTH_SERVER_URL ?? "",
  ownerOpenId:  process.env.OWNER_OPEN_ID ?? "",
  isProduction: process.env.NODE_ENV === "production",

  // AI API — أولوية: GEMINI → GROQ → OPENAI → Forge (legacy)
  forgeApiKey: (
    process.env.GEMINI_API_KEY ||
    process.env.GROQ_API_KEY   ||
    process.env.OPENAI_API_KEY ||
    process.env.BUILT_IN_FORGE_API_KEY ||
    ""
  ),
  forgeApiUrl: (
    process.env.GEMINI_API_KEY ? "https://generativelanguage.googleapis.com/v1beta/openai" :
    process.env.GROQ_API_KEY   ? "https://api.groq.com/openai"                             :
    process.env.OPENAI_API_KEY ? "https://api.openai.com"                                   :
    process.env.BUILT_IN_FORGE_API_URL || "https://forge.manus.im"
  ),

  // AI model selection
  aiModel: (
    process.env.GEMINI_API_KEY ? "gemini-2.0-flash"      :
    process.env.GROQ_API_KEY   ? "llama-3.3-70b-versatile" :
    process.env.OPENAI_API_KEY ? "gpt-4o-mini"             :
    "gpt-4o-mini"
  ),
};
