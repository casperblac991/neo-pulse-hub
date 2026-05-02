import { t as definePluginEntry } from "../../plugin-entry-rrZRIs0T.js";
import { n as buildFalImageGenerationProvider } from "../../image-generation-provider-P_gqO3XV.js";
import { t as createFalProvider } from "../../provider-registration-DDc2buee.js";
import { n as buildFalVideoGenerationProvider } from "../../video-generation-provider-s21rzUrO.js";
var fal_default = definePluginEntry({
	id: "fal",
	name: "fal Provider",
	description: "Bundled fal image and video generation provider",
	register(api) {
		api.registerProvider(createFalProvider());
		api.registerImageGenerationProvider(buildFalImageGenerationProvider());
		api.registerVideoGenerationProvider(buildFalVideoGenerationProvider());
	}
});
//#endregion
export { fal_default as default };
