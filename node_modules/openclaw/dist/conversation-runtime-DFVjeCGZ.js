import "./session-binding-service-YEea7Du6.js";
import "./binding-registry-CTa0x_Oa.js";
import "./conversation-binding-D5vT6OPL.js";
import "./session-Eayw0wpO.js";
import "./pairing-store-TGJflbSJ.js";
import "./dm-policy-shared-CoVEPzMS.js";
import "./binding-targets-Do361TLf.js";
import "./binding-routing-DEeSJYu7.js";
import "./thread-bindings-policy-BU4XaupC.js";
import "./pairing-labels-su0fmfl_.js";
//#region src/channels/session-meta.ts
let inboundSessionRuntimePromise = null;
function loadInboundSessionRuntime() {
	inboundSessionRuntimePromise ??= import("./inbound.runtime-DHm9Qouk.js");
	return inboundSessionRuntimePromise;
}
async function recordInboundSessionMetaSafe(params) {
	const runtime = await loadInboundSessionRuntime();
	const storePath = runtime.resolveStorePath(params.cfg.session?.store, { agentId: params.agentId });
	try {
		await runtime.recordSessionMetaFromInbound({
			storePath,
			sessionKey: params.sessionKey,
			ctx: params.ctx
		});
	} catch (err) {
		params.onError?.(err);
	}
}
//#endregion
export { recordInboundSessionMetaSafe as t };
