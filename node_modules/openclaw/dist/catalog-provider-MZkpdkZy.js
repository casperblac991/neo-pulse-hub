import { c as normalizeOptionalString } from "./string-coerce-Bje8XVt9.js";
import { a as coerceSecretRef } from "./types.secrets-BHp0Y_k0.js";
import { h as resolveNonEnvSecretRefApiKeyMarker } from "./model-auth-markers-B37LoUoY.js";
import "./provider-auth-D5LV_T9H.js";
import "./text-runtime-ysqqY1vr.js";
import { a as resolveCloudflareAiGatewayBaseUrl, i as buildCloudflareAiGatewayModelDefinition } from "./models-OBE6lpBp.js";
//#region extensions/cloudflare-ai-gateway/catalog-provider.ts
function resolveCloudflareAiGatewayApiKey(cred) {
	if (!cred || cred.type !== "api_key") return;
	const keyRef = coerceSecretRef(cred.keyRef);
	const keyRefId = normalizeOptionalString(keyRef?.id);
	if (keyRef && keyRefId) return keyRef.source === "env" ? keyRefId : resolveNonEnvSecretRefApiKeyMarker(keyRef.source);
	return normalizeOptionalString(cred.key);
}
function resolveCloudflareAiGatewayMetadata(cred) {
	if (!cred || cred.type !== "api_key") return {};
	return {
		accountId: normalizeOptionalString(cred.metadata?.accountId),
		gatewayId: normalizeOptionalString(cred.metadata?.gatewayId)
	};
}
function buildCloudflareAiGatewayCatalogProvider(params) {
	const apiKey = normalizeOptionalString(params.envApiKey) ?? resolveCloudflareAiGatewayApiKey(params.credential);
	if (!apiKey) return null;
	const { accountId, gatewayId } = resolveCloudflareAiGatewayMetadata(params.credential);
	if (!accountId || !gatewayId) return null;
	const baseUrl = resolveCloudflareAiGatewayBaseUrl({
		accountId,
		gatewayId
	});
	if (!baseUrl) return null;
	return {
		baseUrl,
		api: "anthropic-messages",
		apiKey,
		models: [buildCloudflareAiGatewayModelDefinition()]
	};
}
//#endregion
export { resolveCloudflareAiGatewayApiKey as n, resolveCloudflareAiGatewayMetadata as r, buildCloudflareAiGatewayCatalogProvider as t };
