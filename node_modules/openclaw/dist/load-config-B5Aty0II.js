import { h as readSourceConfigSnapshotForWrite, i as getRuntimeConfig } from "./io-DaEsZ_NY.js";
import { _ as setRuntimeConfigSnapshot } from "./runtime-snapshot-CRVyvdTg.js";
import "./config-DMj91OAB.js";
import "./command-secret-gateway-DPEBq4q4.js";
import { i as getModelsCommandSecretTargetIds } from "./command-secret-targets-BqlyieXD.js";
import { t as resolveCommandConfigWithSecrets } from "./command-config-resolution-BsasJwVj.js";
//#region src/commands/models/load-config.ts
async function loadSourceConfigSnapshot(fallback) {
	try {
		const { snapshot } = await readSourceConfigSnapshotForWrite();
		if (snapshot.valid) return snapshot.sourceConfig;
	} catch {}
	return fallback;
}
async function loadModelsConfigWithSource(params) {
	const runtimeConfig = getRuntimeConfig();
	const sourceConfig = await loadSourceConfigSnapshot(runtimeConfig);
	const { resolvedConfig, diagnostics } = await resolveCommandConfigWithSecrets({
		config: runtimeConfig,
		commandName: params.commandName,
		targetIds: getModelsCommandSecretTargetIds(),
		runtime: params.runtime
	});
	setRuntimeConfigSnapshot(resolvedConfig, sourceConfig);
	return {
		sourceConfig,
		resolvedConfig,
		diagnostics
	};
}
async function loadModelsConfig(params) {
	return (await loadModelsConfigWithSource(params)).resolvedConfig;
}
//#endregion
export { loadModelsConfigWithSource as n, loadModelsConfig as t };
