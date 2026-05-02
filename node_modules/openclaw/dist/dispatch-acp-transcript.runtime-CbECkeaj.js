import { p as resolveSessionAgentId } from "./agent-scope-Df_s1jDI.js";
import { u as resolveStorePath } from "./paths-CEkZRIk4.js";
import { t as loadSessionStore } from "./store-load-DVYHxNc9.js";
import { l as resolveSessionStoreEntry } from "./store-CX_a-msa.js";
import "./sessions-ZhmJo-Kv.js";
import { n as resolveAcpSessionCwd } from "./session-identifiers-DmMmYBWr.js";
import { o as persistAcpTurnTranscript } from "./attempt-execution-BKYlZFfb.js";
//#region src/auto-reply/reply/dispatch-acp-transcript.runtime.ts
async function persistAcpDispatchTranscript(params) {
	const promptText = params.promptText.trim();
	const finalText = params.finalText.trim();
	if (!promptText && !finalText) return;
	const sessionAgentId = resolveSessionAgentId({
		sessionKey: params.sessionKey,
		config: params.cfg
	});
	const storePath = resolveStorePath(params.cfg.session?.store, { agentId: sessionAgentId });
	const sessionStore = loadSessionStore(storePath, { skipCache: true });
	const sessionEntry = resolveSessionStoreEntry({
		store: sessionStore,
		sessionKey: params.sessionKey
	}).existing;
	const sessionId = sessionEntry?.sessionId;
	if (!sessionId) throw new Error(`unknown ACP session key: ${params.sessionKey}`);
	await persistAcpTurnTranscript({
		body: promptText,
		transcriptBody: promptText,
		finalText,
		sessionId,
		sessionKey: params.sessionKey,
		sessionEntry,
		sessionStore,
		storePath,
		sessionAgentId,
		threadId: params.threadId,
		sessionCwd: resolveAcpSessionCwd(params.meta) ?? process.cwd()
	});
}
//#endregion
export { persistAcpDispatchTranscript };
