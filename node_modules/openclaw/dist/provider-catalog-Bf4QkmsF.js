import { r as buildCerebrasCatalogModels, t as CEREBRAS_BASE_URL } from "./models-C5yif8aG.js";
//#region extensions/cerebras/provider-catalog.ts
function buildCerebrasProvider() {
	return {
		baseUrl: CEREBRAS_BASE_URL,
		api: "openai-completions",
		models: buildCerebrasCatalogModels()
	};
}
//#endregion
export { buildCerebrasProvider as t };
