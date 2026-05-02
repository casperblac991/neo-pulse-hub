import { r as registerCoreCliCommands } from "./command-registry-core-D7ksM5gN.js";
import { n as registerSubCliCommands } from "./register.subclis-6aNnH4u4.js";
//#region src/cli/program/command-registry.ts
function registerProgramCommands(program, ctx, argv = process.argv) {
	registerCoreCliCommands(program, ctx, argv);
	registerSubCliCommands(program, argv);
}
//#endregion
export { registerProgramCommands as t };
