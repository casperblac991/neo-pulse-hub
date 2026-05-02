//#region src/auto-reply/reply/dispatch-acp.runtime.ts
let dispatchAcpPromise = null;
let dispatchAcpCommandBypassPromise = null;
function loadDispatchAcp() {
	dispatchAcpPromise ??= import("./dispatch-acp-BkksAp9H.js");
	return dispatchAcpPromise;
}
function loadDispatchAcpCommandBypass() {
	dispatchAcpCommandBypassPromise ??= import("./dispatch-acp-command-bypass-CQzVWrjk.js");
	return dispatchAcpCommandBypassPromise;
}
async function shouldBypassAcpDispatchForCommand(...args) {
	return (await loadDispatchAcpCommandBypass()).shouldBypassAcpDispatchForCommand(...args);
}
async function tryDispatchAcpReply(...args) {
	return await (await loadDispatchAcp()).tryDispatchAcpReply(...args);
}
//#endregion
export { shouldBypassAcpDispatchForCommand, tryDispatchAcpReply };
