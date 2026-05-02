import { n as resolveAgentModelPrimaryValue } from "./model-input-BhAB75wV.js";
import { n as logConfigUpdated } from "./logging-C2QxMjAB.js";
import { t as applyDefaultModelPrimaryUpdate, u as updateConfig } from "./shared-CV4D0i3q.js";
//#region src/commands/models/set-image.ts
async function modelsSetImageCommand(modelRaw, runtime) {
	const updated = await updateConfig((cfg) => {
		return applyDefaultModelPrimaryUpdate({
			cfg,
			modelRaw,
			field: "imageModel"
		});
	});
	logConfigUpdated(runtime);
	runtime.log(`Image model: ${resolveAgentModelPrimaryValue(updated.agents?.defaults?.imageModel) ?? modelRaw}`);
}
//#endregion
export { modelsSetImageCommand };
