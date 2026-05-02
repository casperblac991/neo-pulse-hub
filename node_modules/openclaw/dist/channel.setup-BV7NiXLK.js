import { t as createZalouserPluginBase } from "./shared-CNgF4m8q.js";
import { n as zalouserSetupAdapter } from "./setup-core-_kiUCW7H.js";
import { t as zalouserSetupWizard } from "./setup-surface-DjgtP6od.js";
//#region extensions/zalouser/src/channel.setup.ts
const zalouserSetupPlugin = { ...createZalouserPluginBase({
	setupWizard: zalouserSetupWizard,
	setup: zalouserSetupAdapter
}) };
//#endregion
export { zalouserSetupPlugin as t };
