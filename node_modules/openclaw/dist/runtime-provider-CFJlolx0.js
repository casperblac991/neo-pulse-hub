import { t as resolveMemoryBackendConfig } from "./backend-config-iFxw4t3s.js";
import "./memory-core-host-runtime-files-iewVGsvo.js";
import { n as getMemorySearchManager, t as closeAllMemorySearchManagers } from "./memory-mxD4Jzcs.js";
//#region extensions/memory-core/src/runtime-provider.ts
const memoryRuntime = {
	async getMemorySearchManager(params) {
		const { manager, error } = await getMemorySearchManager(params);
		return {
			manager,
			error
		};
	},
	resolveMemoryBackendConfig(params) {
		return resolveMemoryBackendConfig(params);
	},
	async closeAllMemorySearchManagers() {
		await closeAllMemorySearchManagers();
	}
};
//#endregion
export { memoryRuntime as t };
