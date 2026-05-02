import { t as createPluginRuntimeStore } from "./runtime-store-DsJ2GIEY.js";
import "./channel-policy-BdSmbFNg.js";
import "./channel-pairing-BKaD8p37.js";
import "./inbound-reply-dispatch-CCcIOov9.js";
import "./ssrf-runtime-VEIen5SK.js";
//#region extensions/nextcloud-talk/src/runtime.ts
const { setRuntime: setNextcloudTalkRuntime, getRuntime: getNextcloudTalkRuntime } = createPluginRuntimeStore({
	pluginId: "nextcloud-talk",
	errorMessage: "Nextcloud Talk runtime not initialized"
});
//#endregion
export { setNextcloudTalkRuntime as n, getNextcloudTalkRuntime as t };
