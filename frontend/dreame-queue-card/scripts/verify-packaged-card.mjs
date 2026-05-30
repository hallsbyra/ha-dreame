import { readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";

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
