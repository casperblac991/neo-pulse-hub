//#region src/commands/doctor.ts
async function doctorCommand(runtime, options) {
	await (await import("./doctor-health-B0Dv0ICC.js")).doctorCommand(runtime, options);
}
//#endregion
export { doctorCommand as t };
