import "./net-BdZuiQba.js";
import "./auth-DY4vhaN6.js";
import "./client-CLNzli6Y.js";
import "./protocol-XZXHSVIZ.js";
import "./operator-approvals-client-mfuqWI-p.js";
import "./gateway-rpc-2b6HiR5p.js";
import "./node-command-policy-D-Eyj6T3.js";
import "./nodes.helpers-CGd9GKU9.js";
import "./startup-auth-ConzYI6T.js";
//#region src/gateway/channel-status-patches.ts
function createConnectedChannelStatusPatch(at = Date.now()) {
	return {
		connected: true,
		lastConnectedAt: at,
		lastEventAt: at
	};
}
function createTransportActivityStatusPatch(at = Date.now()) {
	return { lastTransportActivityAt: at };
}
//#endregion
export { createTransportActivityStatusPatch as n, createConnectedChannelStatusPatch as t };
