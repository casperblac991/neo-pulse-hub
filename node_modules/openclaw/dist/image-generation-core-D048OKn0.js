import "./subsystem-DwIxKdWw.js";
import "./provider-env-vars-8ZfhVxtG.js";
import "./failover-error-DInpU3ie.js";
import "./provider-model-shared-B8f0npIw.js";
import "./provider-registry-DLG4r1Ec.js";
import "./runtime-shared-B5QAMc3I.js";
import "./provider-model-defaults-Begs764N.js";
//#region src/plugin-sdk/image-generation-core.ts
let imageGenerationCoreAuthRuntimePromise;
async function loadImageGenerationCoreAuthRuntime() {
	imageGenerationCoreAuthRuntimePromise ??= import("./image-generation-core.auth.runtime-qjO2JYxi.js");
	return imageGenerationCoreAuthRuntimePromise;
}
async function resolveApiKeyForProvider(...args) {
	return (await loadImageGenerationCoreAuthRuntime()).resolveApiKeyForProvider(...args);
}
//#endregion
export { resolveApiKeyForProvider as t };
