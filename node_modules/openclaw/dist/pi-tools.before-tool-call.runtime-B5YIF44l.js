import { c as logToolLoopAction } from "./diagnostic-CSWy_gId.js";
import { n as getDiagnosticSessionState } from "./diagnostic-session-state-Kx1s6rMK.js";
import { n as recordToolCall, r as recordToolCallOutcome, t as detectToolCallLoop } from "./tool-loop-detection-auLhl3HD.js";
//#region src/agents/pi-tools.before-tool-call.runtime.ts
const beforeToolCallRuntime = {
	getDiagnosticSessionState,
	logToolLoopAction,
	detectToolCallLoop,
	recordToolCall,
	recordToolCallOutcome
};
//#endregion
export { beforeToolCallRuntime };
