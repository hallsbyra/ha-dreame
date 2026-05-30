import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";

const packagedCardPath = resolve(
  import.meta.dirname,
  "../../../custom_components/ha_dreame/frontend/ha-dreame-queue-card.js",
);

let stats;
try {
  stats = statSync(packagedCardPath);
} catch (err) {
  throw new Error(`Packaged card asset is missing: ${packagedCardPath}`, { cause: err });
}

if (!stats.isFile()) {
  throw new Error(`Packaged card asset is not a file: ${packagedCardPath}`);
}

const contents = readFileSync(packagedCardPath, "utf8");
if (!contents.includes("ha-dreame-queue-card")) {
  throw new Error("Packaged card asset does not define the HA Dreame card element");
}

const packagedCardDir = dirname(packagedCardPath);
const editorChunks = readdirSync(packagedCardDir).filter((filename) =>
  /^ha-dreame-queue-card-editor-.+\.js$/.test(filename),
);

if (!editorChunks.length) {
  throw new Error("Packaged card editor chunk is missing");
}

if (!editorChunks.some((filename) => contents.includes(filename))) {
  throw new Error("Packaged card asset does not reference the editor chunk");
}
