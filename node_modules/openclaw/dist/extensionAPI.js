import { b as resolveAgentDir, x as resolveAgentWorkspaceDir } from "./agent-scope-Df_s1jDI.js";
import { n as DEFAULT_MODEL, r as DEFAULT_PROVIDER } from "./defaults-xppxcKrw.js";
import { i as resolveSessionFilePath, u as resolveStorePath } from "./paths-CEkZRIk4.js";
import { t as loadSessionStore } from "./store-load-DVYHxNc9.js";
import { i as saveSessionStore } from "./store-CX_a-msa.js";
import "./sessions-ZhmJo-Kv.js";
import { p as resolveThinkingDefault } from "./model-selection-sqz--Abu.js";
import { t as resolveAgentTimeoutMs } from "./timeout-Dp_SkpaV.js";
import { n as resolveAgentIdentity } from "./identity-EQy_7cW-.js";
import { l as ensureAgentWorkspace } from "./workspace-vjItI7Mv.js";
import { t as runEmbeddedPiAgent } from "./pi-embedded-RhaMl0u2.js";
//#region src/extensionAPI.ts
if (process.env.VITEST !== "true" && process.env.OPENCLAW_SUPPRESS_EXTENSION_API_WARNING !== "1") process.emitWarning("openclaw/extension-api is deprecated. Migrate to api.runtime.agent.* or focused openclaw/plugin-sdk/<subpath> imports. See https://docs.openclaw.ai/plugins/sdk-migration", {
	code: "OPENCLAW_EXTENSION_API_DEPRECATED",
	detail: "This compatibility bridge is temporary. Bundled plugins should use the injected plugin runtime instead of importing host-side agent helpers directly. Migration guide: https://docs.openclaw.ai/plugins/sdk-migration"
});
//#endregion
export { DEFAULT_MODEL, DEFAULT_PROVIDER, ensureAgentWorkspace, loadSessionStore, resolveAgentDir, resolveAgentIdentity, resolveAgentTimeoutMs, resolveAgentWorkspaceDir, resolveSessionFilePath, resolveStorePath, resolveThinkingDefault, runEmbeddedPiAgent, saveSessionStore };
