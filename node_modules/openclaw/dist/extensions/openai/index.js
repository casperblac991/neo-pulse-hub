import { a as buildProviderToolCompatFamilyHooks } from "../../provider-tools-BKvJyJUV.js";
import { t as definePluginEntry } from "../../plugin-entry-rrZRIs0T.js";
import { r as resolvePluginConfigObject } from "../../plugin-config-runtime-aIhfvY7t.js";
import { t as buildOpenAICodexCliBackend } from "../../cli-backend-ChRLKzir.js";
import { t as buildOpenAIImageGenerationProvider } from "../../image-generation-provider-DZepZAun.js";
import { n as openaiCodexMediaUnderstandingProvider, r as openaiMediaUnderstandingProvider } from "../../media-understanding-provider-CbZ0wWfT.js";
import { t as openAiMemoryEmbeddingProviderAdapter } from "../../memory-embedding-adapter-HJa2oi1R.js";
import { t as buildOpenAICodexProviderPlugin } from "../../openai-codex-provider-e4Gp5UVw.js";
import { t as buildOpenAIProvider } from "../../openai-provider-BsrUQqUG.js";
import { i as resolveOpenAISystemPromptContribution, r as resolveOpenAIPromptOverlayMode } from "../../prompt-overlay-B_38c4DC.js";
import { t as buildOpenAIRealtimeTranscriptionProvider } from "../../realtime-transcription-provider-5wU1TE66.js";
import { t as buildOpenAIRealtimeVoiceProvider } from "../../realtime-voice-provider-CMgTlVSR.js";
import { t as buildOpenAISpeechProvider } from "../../speech-provider-CdsALWlH.js";
import { t as buildOpenAIVideoGenerationProvider } from "../../video-generation-provider-BxrYnYEl.js";
//#region extensions/openai/index.ts
var openai_default = definePluginEntry({
	id: "openai",
	name: "OpenAI Provider",
	description: "Bundled OpenAI provider plugins",
	register(api) {
		const openAIToolCompatHooks = buildProviderToolCompatFamilyHooks("openai");
		const buildProviderWithPromptContribution = (provider) => ({
			...provider,
			...openAIToolCompatHooks,
			resolveSystemPromptContribution: (ctx) => {
				const pluginConfig = resolvePluginConfigObject(ctx.config, "openai") ?? (ctx.config ? void 0 : api.pluginConfig);
				return resolveOpenAISystemPromptContribution({
					config: ctx.config,
					legacyPluginConfig: pluginConfig,
					mode: resolveOpenAIPromptOverlayMode(pluginConfig),
					modelProviderId: provider.id,
					modelId: ctx.modelId
				});
			}
		});
		api.registerCliBackend(buildOpenAICodexCliBackend());
		api.registerProvider(buildProviderWithPromptContribution(buildOpenAIProvider()));
		api.registerProvider(buildProviderWithPromptContribution(buildOpenAICodexProviderPlugin()));
		api.registerMemoryEmbeddingProvider(openAiMemoryEmbeddingProviderAdapter);
		api.registerImageGenerationProvider(buildOpenAIImageGenerationProvider());
		api.registerRealtimeTranscriptionProvider(buildOpenAIRealtimeTranscriptionProvider());
		api.registerRealtimeVoiceProvider(buildOpenAIRealtimeVoiceProvider());
		api.registerSpeechProvider(buildOpenAISpeechProvider());
		api.registerMediaUnderstandingProvider(openaiMediaUnderstandingProvider);
		api.registerMediaUnderstandingProvider(openaiCodexMediaUnderstandingProvider);
		api.registerVideoGenerationProvider(buildOpenAIVideoGenerationProvider());
	}
});
//#endregion
export { openai_default as default };
