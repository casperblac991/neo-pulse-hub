import { t as definePluginEntry } from "../../plugin-entry-rrZRIs0T.js";
import "../../api-i0pSFDbo.js";
import { n as migrateMemoryWikiLegacyConfig } from "../../config-compat-CTgUW_36.js";
//#region extensions/memory-wiki/setup-api.ts
var setup_api_default = definePluginEntry({
	id: "memory-wiki",
	name: "Memory Wiki Setup",
	description: "Lightweight Memory Wiki setup hooks",
	register(api) {
		api.registerConfigMigration((config) => migrateMemoryWikiLegacyConfig(config));
	}
});
//#endregion
export { setup_api_default as default };
