import fs from "fs";
import path from "path";

const docsDir = path.resolve("public");

const files = fs
  .readdirSync(docsDir)
  .filter(file => file !== "index.json");

const output = {
  count: files.length,
  files
};

fs.writeFileSync(
  path.join(docsDir, "index.json"),
  JSON.stringify(output, null, 2)
);

console.log(`Index gerado com ${files.length} ficheiros.`);