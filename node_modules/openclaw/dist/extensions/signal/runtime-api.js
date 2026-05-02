import { t as formatDocsLink } from "../../links-BszRQhGa.js";
import { t as formatCliCommand } from "../../command-format-BORwwHyH.js";
import { l as normalizeE164 } from "../../utils-DvkbxKCZ.js";
import { r as buildChannelConfigSchema } from "../../config-schema-TgszMKRa.js";
import { n as normalizeAccountId, t as DEFAULT_ACCOUNT_ID } from "../../account-id-vYgQddVH.js";
import { o as SignalConfigSchema } from "../../zod-schema.providers-whatsapp-Bz-FRH5z.js";
import { a as chunkText } from "../../chunk-DVS_k7cI.js";
import { n as deleteAccountFromConfigSection, r as setAccountEnabledInConfigSection } from "../../config-helpers-By32plyz.js";
import { n as formatPairingApproveHint } from "../../helpers-DaiQyy4G.js";
import "../../text-runtime-ysqqY1vr.js";
import { n as emptyPluginConfigSchema } from "../../config-schema-C0_wxQFt.js";
import { s as migrateBaseNameToDefaultAccount, t as applyAccountNameToChannelSection } from "../../setup-helpers-C80aTqI-.js";
import { c as getChatChannelMeta } from "../../core-D416gENI.js";
import { t as createPluginRuntimeStore } from "../../runtime-store-DsJ2GIEY.js";
import { n as resolveAllowlistProviderRuntimeGroupPolicy, r as resolveDefaultGroupPolicy } from "../../runtime-group-policy-DFxs5PT-.js";
import { t as resolveChannelMediaMaxBytes } from "../../media-limits-CW8VvpNb.js";
import { t as PAIRING_APPROVED_MESSAGE } from "../../pairing-message-BuV4sohp.js";
import { c as collectStatusIssuesFromLastError, d as createDefaultChannelRuntimeState, n as buildBaseChannelStatusSummary, t as buildBaseAccountStatusSnapshot } from "../../status-helpers-B9xc_mSy.js";
import { t as detectBinary } from "../../detect-binary-BAMe7J20.js";
import "../../setup-tools-B-Zy0TER.js";
import "../../reply-runtime-Cl43gAni.js";
import "../../media-runtime-BX6_wefs.js";
import "../../channel-status-CZGM0j5K.js";
import { i as resolveSignalAccount, n as listSignalAccountIds, r as resolveDefaultSignalAccountId, t as listEnabledSignalAccounts } from "../../accounts-BzE20VTb.js";
import { d as looksLikeSignalTargetId, f as normalizeSignalMessagingTarget } from "../../identity-QSFZa1LA.js";
import { n as sendReactionSignal, t as removeReactionSignal } from "../../reaction-runtime-api-Dz76HSoQ.js";
import { n as resolveSignalReactionLevel, t as signalMessageActions } from "../../message-actions-C5aXQ0YW.js";
import "../../config-api-CECv-vkm.js";
import { r as installSignalCli } from "../../install-signal-cli-DZ0fCZrU.js";
import { t as monitorSignalProvider } from "../../monitor-D141zc1R.js";
import { t as sendMessageSignal } from "../../send-CEQ3xFRw.js";
import { t as probeSignal } from "../../probe-BQrVRsIz.js";
//#region extensions/signal/src/runtime.ts
const { setRuntime: setSignalRuntime, clearRuntime: clearSignalRuntime, getRuntime: getSignalRuntime } = createPluginRuntimeStore({
	pluginId: "signal",
	errorMessage: "Signal runtime not initialized"
});
//#endregion
export { DEFAULT_ACCOUNT_ID, PAIRING_APPROVED_MESSAGE, SignalConfigSchema, applyAccountNameToChannelSection, buildBaseAccountStatusSnapshot, buildBaseChannelStatusSummary, buildChannelConfigSchema, chunkText, collectStatusIssuesFromLastError, createDefaultChannelRuntimeState, deleteAccountFromConfigSection, detectBinary, emptyPluginConfigSchema, formatCliCommand, formatDocsLink, formatPairingApproveHint, getChatChannelMeta, installSignalCli, listEnabledSignalAccounts, listSignalAccountIds, looksLikeSignalTargetId, migrateBaseNameToDefaultAccount, monitorSignalProvider, normalizeAccountId, normalizeE164, normalizeSignalMessagingTarget, probeSignal, removeReactionSignal, resolveAllowlistProviderRuntimeGroupPolicy, resolveChannelMediaMaxBytes, resolveDefaultGroupPolicy, resolveDefaultSignalAccountId, resolveSignalAccount, resolveSignalReactionLevel, sendMessageSignal, sendReactionSignal, setAccountEnabledInConfigSection, setSignalRuntime, signalMessageActions };
