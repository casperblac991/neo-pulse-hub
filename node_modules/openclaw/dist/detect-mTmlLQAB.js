import { t as detectZaiEndpoint$1 } from "./provider-zai-endpoint-DTWY0Sx-.js";
import "./runtime-api-CV1nhV13.js";
//#region extensions/zai/detect.ts
let detectZaiEndpointImpl = detectZaiEndpoint$1;
function setDetectZaiEndpointForTesting(fn) {
	detectZaiEndpointImpl = fn ?? detectZaiEndpoint$1;
}
async function detectZaiEndpoint(...args) {
	return await detectZaiEndpointImpl(...args);
}
//#endregion
export { setDetectZaiEndpointForTesting as n, detectZaiEndpoint as t };
