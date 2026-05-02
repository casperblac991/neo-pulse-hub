import { n as buildManifestModelProviderConfig } from "./provider-catalog-shared-D-H5Odso.js";
import { t as modelCatalog } from "./openclaw.plugin-pC47fKI4.js";
//#region extensions/mistral/provider-catalog.ts
function buildMistralProvider() {
	return buildManifestModelProviderConfig({
		providerId: "mistral",
		catalog: modelCatalog.providers.mistral
	});
}
//#endregion
export { buildMistralProvider as t };
