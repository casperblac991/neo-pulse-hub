import { o as resolveDefaultModelForAgent } from "./model-selection-sqz--Abu.js";
import { n as resolveCodexNativeWebSearchConfig } from "./codex-native-web-search.shared-BOr5wLiC.js";
import { i as isCodexNativeSearchEligibleModel, n as hasAvailableCodexAuth } from "./codex-native-web-search-core-4ulbkZXY.js";
//#region src/agents/codex-native-web-search.ts
function isCodexNativeWebSearchRelevant(params) {
	if (resolveCodexNativeWebSearchConfig(params.config).enabled) return true;
	if (hasAvailableCodexAuth(params)) return true;
	const defaultModel = resolveDefaultModelForAgent({
		cfg: params.config,
		agentId: params.agentId
	});
	const configuredProvider = params.config.models?.providers?.[defaultModel.provider];
	const configuredModelApi = configuredProvider?.models?.find((candidate) => candidate.id === defaultModel.model)?.api;
	return isCodexNativeSearchEligibleModel({
		modelProvider: defaultModel.provider,
		modelApi: configuredModelApi ?? configuredProvider?.api
	});
}
//#endregion
export { isCodexNativeWebSearchRelevant as t };
