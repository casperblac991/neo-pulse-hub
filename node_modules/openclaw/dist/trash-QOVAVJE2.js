import { n as resolvePreferredOpenClawTmpDir } from "./tmp-openclaw-dir-CLT3-4-C.js";
import "./temp-path-Bgsg2mFV.js";
import { t as movePathToTrash$1 } from "./browser-trash-l_VgCHUj.js";
import "./browser-config-BHDpXuLm.js";
import os from "node:os";
//#region extensions/browser/src/browser/trash.ts
async function movePathToTrash(targetPath) {
	return await movePathToTrash$1(targetPath, { allowedRoots: [os.homedir(), resolvePreferredOpenClawTmpDir()] });
}
//#endregion
export { movePathToTrash as t };
