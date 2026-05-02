import "./utils-DvkbxKCZ.js";
import "./types.secrets-BHp0Y_k0.js";
import "./setup-helpers-C80aTqI-.js";
import "./setup-wizard-helpers-4xSddeax.js";
import "./setup-binary-BfRh1fOD.js";
import "./setup-wizard-proxy-DAN1aLUu.js";
//#region src/plugin-sdk/resolution-notes.ts
/** Format a short note that separates successfully resolved targets from unresolved passthrough values. */
function formatResolvedUnresolvedNote(params) {
	if (params.resolved.length === 0 && params.unresolved.length === 0) return;
	return [params.resolved.length > 0 ? `Resolved: ${params.resolved.join(", ")}` : void 0, params.unresolved.length > 0 ? `Unresolved (kept as typed): ${params.unresolved.join(", ")}` : void 0].filter(Boolean).join("\n");
}
//#endregion
export { formatResolvedUnresolvedNote as t };
