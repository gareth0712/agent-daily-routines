import { createReadStream, existsSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";

const root = process.cwd();
const port = Number(process.env.PORT || 4173);
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8" };

createServer((request, response) => {
  const requestPath = request.url === "/" ? "/public/index.html" : request.url;
  const relative = normalize(requestPath).replace(/^(\.\.[/\\])+/, "").replace(/^[/\\]/, "");
  const file = join(root, relative);
  if (!existsSync(file)) {
    response.writeHead(404).end("Not found");
    return;
  }
  response.writeHead(200, { "content-type": types[extname(file)] || "text/plain; charset=utf-8" });
  createReadStream(file).pipe(response);
}).listen(port, "127.0.0.1", () => console.log(`ACTIVITY_URL=http://127.0.0.1:${port}`));
