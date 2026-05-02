import { n as AcpRuntimeError, r as isAcpRuntimeError } from "../errors-B6Q4Zgyd.js";
import { n as getAcpSessionManager, t as __testing$1 } from "../manager-C8fiiv51.js";
import { a as unregisterAcpRuntimeBackend, i as requireAcpRuntimeBackend, n as getAcpRuntimeBackend, r as registerAcpRuntimeBackend, t as __testing$2 } from "../registry-Bj09X5sS.js";
import { n as readAcpSessionEntry } from "../session-meta-CwbItcDH.js";
import { t as tryDispatchAcpReplyHook } from "../acp-runtime-backend-D_mt0yll.js";
//#region src/plugin-sdk/acp-runtime.ts
const __testing = new Proxy({}, {
	get(_target, prop, receiver) {
		if (Reflect.has(__testing$1, prop)) return Reflect.get(__testing$1, prop, receiver);
		return Reflect.get(__testing$2, prop, receiver);
	},
	has(_target, prop) {
		return Reflect.has(__testing$1, prop) || Reflect.has(__testing$2, prop);
	},
	ownKeys() {
		return Array.from(new Set([...Reflect.ownKeys(__testing$1), ...Reflect.ownKeys(__testing$2)]));
	},
	getOwnPropertyDescriptor(_target, prop) {
		if (Reflect.has(__testing$1, prop) || Reflect.has(__testing$2, prop)) return {
			configurable: true,
			enumerable: true
		};
	}
});
//#endregion
export { AcpRuntimeError, __testing, getAcpRuntimeBackend, getAcpSessionManager, isAcpRuntimeError, readAcpSessionEntry, registerAcpRuntimeBackend, requireAcpRuntimeBackend, tryDispatchAcpReplyHook, unregisterAcpRuntimeBackend };
