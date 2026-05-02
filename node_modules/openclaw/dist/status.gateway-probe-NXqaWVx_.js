import { t as pickGatewaySelfPresence } from "./gateway-presence-Bd77A5g4.js";
import { t as resolveGatewayProbeTarget } from "./probe-target-crHt5pZZ.js";
import { r as resolveGatewayProbeAuthSafeWithSecretInputs } from "./probe-auth-xgoU5Obd.js";
//#region src/commands/status.gateway-probe.ts
async function resolveGatewayProbeAuthResolution(cfg) {
	return resolveGatewayProbeAuthSafeWithSecretInputs({
		cfg,
		mode: resolveGatewayProbeTarget(cfg).mode,
		env: process.env
	});
}
async function resolveGatewayProbeAuth(cfg) {
	return (await resolveGatewayProbeAuthResolution(cfg)).auth;
}
//#endregion
export { pickGatewaySelfPresence, resolveGatewayProbeAuth, resolveGatewayProbeAuthResolution };
