import { r as buildChannelConfigSchema } from "../../config-schema-TgszMKRa.js";
import { t as DEFAULT_ACCOUNT_ID } from "../../account-id-vYgQddVH.js";
import { i as IMessageConfigSchema } from "../../zod-schema.providers-whatsapp-Bz-FRH5z.js";
import { p as formatTrimmedAllowFromEntries } from "../../channel-config-helpers-mYqAcdtC.js";
import { c as getChatChannelMeta } from "../../core-D416gENI.js";
import { t as createPluginRuntimeStore } from "../../runtime-store-DsJ2GIEY.js";
import { t as resolveChannelMediaMaxBytes } from "../../media-limits-CW8VvpNb.js";
import { t as PAIRING_APPROVED_MESSAGE } from "../../pairing-message-BuV4sohp.js";
import { c as collectStatusIssuesFromLastError, r as buildComputedAccountStatusSnapshot } from "../../status-helpers-B9xc_mSy.js";
import "../../media-runtime-BX6_wefs.js";
import { t as chunkTextForOutbound } from "../../text-chunking-CQxXCFXJ.js";
import "../../channel-status-CZGM0j5K.js";
import { f as looksLikeIMessageTargetId, h as resolveIMessageConfigDefaultTo, m as resolveIMessageConfigAllowFrom, p as normalizeIMessageMessagingTarget } from "../../conversation-id-DzhQitN-.js";
import { n as resolveIMessageGroupToolPolicy, t as resolveIMessageGroupRequireMention } from "../../group-policy-BSm322X2.js";
import "../../config-api-Bc1KIBDj.js";
import { t as probeIMessage } from "../../probe-DGfoCahw.js";
import { n as sendMessageIMessage, t as monitorIMessageProvider } from "../../monitor-1GPABxmB.js";
//#region extensions/imessage/src/runtime.ts
const { setRuntime: setIMessageRuntime, getRuntime: getIMessageRuntime } = createPluginRuntimeStore({
	pluginId: "imessage",
	errorMessage: "iMessage runtime not initialized"
});
//#endregion
export { DEFAULT_ACCOUNT_ID, IMessageConfigSchema, PAIRING_APPROVED_MESSAGE, buildChannelConfigSchema, buildComputedAccountStatusSnapshot, chunkTextForOutbound, collectStatusIssuesFromLastError, formatTrimmedAllowFromEntries, getChatChannelMeta, looksLikeIMessageTargetId, monitorIMessageProvider, normalizeIMessageMessagingTarget, probeIMessage, resolveChannelMediaMaxBytes, resolveIMessageConfigAllowFrom, resolveIMessageConfigDefaultTo, resolveIMessageGroupRequireMention, resolveIMessageGroupToolPolicy, sendMessageIMessage, setIMessageRuntime };
