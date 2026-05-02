import { r as createLegacyPrivateNetworkDoctorContract } from "./ssrf-policy-BrfaCKk1.js";
import "./ssrf-runtime-VEIen5SK.js";
//#region extensions/tlon/src/doctor-contract.ts
const contract = createLegacyPrivateNetworkDoctorContract({ channelKey: "tlon" });
const legacyConfigRules = contract.legacyConfigRules;
const normalizeCompatibilityConfig = contract.normalizeCompatibilityConfig;
//#endregion
export { normalizeCompatibilityConfig as n, legacyConfigRules as t };
