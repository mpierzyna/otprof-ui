// SPDX-FileCopyrightText: 2026 Maximilian Pierzyna
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { Marked, type MarkedExtension, type Token, type TokensList } from "marked";
import markedFootnote from "marked-footnote";
import { liteAdaptor } from "mathjax-full/js/adaptors/liteAdaptor.js";
import { RegisterHTMLHandler } from "mathjax-full/js/handlers/html.js";
import { TeX } from "mathjax-full/js/input/tex.js";
import { AllPackages } from "mathjax-full/js/input/tex/AllPackages.js";
import { mathjax } from "mathjax-full/js/mathjax.js";
import { SVG } from "mathjax-full/js/output/svg.js";
import { type Connect, defineConfig, type Plugin } from "vite";
import { ICONS, type IconName } from "./src/icons";

// Development data (default: the pipelines' web data, pipeline/data/webui) served at /data/ by the dev and preview
// servers only, so it never ends up in the build: in production the web server delivers it at the same path.
const DEV_DATA = resolve(__dirname, process.env.OTPROF_UI_DATA ?? "../pipeline/data/webui");
const TYPES: Record<string, string> = { ".json": "application/json", ".md": "text/markdown; charset=utf-8" };

function devData(): Plugin {
  const serve = (server: { middlewares: Connect.Server }) => {
    server.middlewares.use("/data", (req, res, next) => {
      const path = resolve(DEV_DATA, `.${decodeURIComponent((req.url ?? "/").split("?")[0])}`);
      if (!path.startsWith(DEV_DATA) || !existsSync(path) || !statSync(path).isFile()) return next();
      res.setHeader("Content-Type", TYPES[path.slice(path.lastIndexOf("."))] ?? "application/octet-stream");
      createReadStream(path).pipe(res);
    });
  };
  return { name: "dev-data", configureServer: serve, configurePreviewServer: serve };
}

// The bundled software with its licenses (license page) exists only in a build (build.license below): the dev server
// serves the one of the last build in dist/, if any (npm run build to update it)
const THIRD_PARTY = "third-party-licenses.json";
function devLicenses(): Plugin {
  return {
    name: "dev-licenses",
    configureServer(server) {
      const file = resolve(__dirname, "dist", THIRD_PARTY);
      server.middlewares.use(`${server.config.base}${THIRD_PARTY}`, (_req, res, next) => {
        if (!existsSync(file)) return next();
        res.setHeader("Content-Type", "application/json");
        createReadStream(file).pipe(res);
      });
    },
  };
}

// Texts of the app (content/*.md, see content/README.md) rendered into index.html at build time:
// <!--content:NAME--> the markdown of content/NAME.md, <!--content:NAME:inline--> as inline markdown (title),
// <!--content:NAME:text--> as plain text (<title>), <!--content:NAME:heading--> its first heading (inline) and
// <!--content:NAME:body--> the rest. Links not starting with /forecast, /climatology (those set the view), /licenses or #
// (footnotes, [^1]) open in a new tab. All markdown is rendered here: the app ships no markdown renderer.
const CONTENT = resolve(__dirname, "content");

// LaTeX in the texts: $...$ inline, $$...$$ displayed, rendered by MathJax to SVG at build time (no fonts or scripts in
// the browser; the SVG takes the text colour). A literal dollar sign: \$.
function math(): MarkedExtension {
  const adaptor = liteAdaptor();
  RegisterHTMLHandler(adaptor);
  const doc = mathjax.document("", { InputJax: new TeX({ packages: AllPackages }), OutputJax: new SVG({ fontCache: "local" }) });
  const tex = (src: string, display: boolean) => adaptor.outerHTML(doc.convert(src, { display }));
  return {
    extensions: [
      {
        name: "math",
        level: "inline",
        start: (src) => src.indexOf("$"),
        tokenizer(src) {
          // No space inside the delimiters and no digit after the closing one, so prices like $5 and $10 stay text
          const m = /^(\$\$?)(?!\s)((?:\\.|[^\\$])+?)(?<!\s)\1(?!\d)/.exec(src);
          return m ? { type: "math", raw: m[0], text: m[2], display: m[1].length === 2 } : undefined;
        },
        renderer: (t) => tex(t.text, t.display),
      },
    ],
  };
}
const MATH = math();
// A new parser per text: footnotes ([^1], marked-footnote) keep state, and their ids get the text's name as prefix, so
// that two texts in the page (forecast, climatology) do not share ids
const markedFor = (name: string) => new Marked(MATH, markedFootnote({ prefixId: `fn-${name}-` }));

// Icons (src/icons.ts: Material Icons, Apache-2.0) into index.html: <!--icon:NAME--> the <path> of the icon, <!--icon:NAME#ID-->
// with that id
function icon(name: string, id?: string) {
  const d = ICONS[name as IconName];
  if (!d) throw new Error(`icon:${name}: unknown icon`);
  return `<path${id ? ` id="${id}"` : ""} d="${d}" />`;
}

function content(): Plugin {
  // Links within the page (#: footnotes) and to the app's own paths stay in the page
  const external = (html: string) => html.replace(/<a href="(?!\/(?:forecast|climatology|licenses)\b|#)/g, '<a target="_blank" rel="noopener noreferrer" href="');
  const render = (name: string, part = "") => {
    const md = readFileSync(resolve(CONTENT, `${name}.md`), "utf-8");
    const marked = markedFor(name);
    if (part === "inline") return external(marked.parseInline(md.trim(), { async: false }));
    if (part === "text") return marked.parseInline(md.trim(), { async: false }).replace(/<[^>]*>/g, "");
    const lexed = marked.lexer(md);
    // The footnotes come first from the lexer (marked.parse moves them, the lexer alone does not): to the end
    const notes = lexed.filter((t) => t.type === "footnotes");
    const tokens = [...lexed.filter((t) => t.type !== "footnotes"), ...notes];
    // Without the links from a footnote back to its markers (↩): the texts are short, and a footnote used several times
    // gets one per use
    const parse = (ts: Token[]) =>
      external(marked.parser(Object.assign(ts, { links: lexed.links }) as TokensList)).replace(/\s*<a [^>]*data-fn-[\w-]+-backref[^>]*>[\s\S]*?<\/a>/g, ""); // fmt: skip
    const k = tokens.findIndex((t) => t.type === "heading");
    if (part === "heading") return k < 0 ? "" : external(marked.parseInline((tokens[k] as Token & { text: string }).text, { async: false })); // fmt: skip
    if (part === "body") return parse(tokens.filter((_, i) => i !== k));
    if (part) throw new Error(`content:${name}:${part}: unknown part`);
    return parse(tokens);
  };
  return {
    name: "content",
    transformIndexHtml: (html) =>
      html
        .replace(/<!--content:([\w-]+)(?::(\w+))?-->/g, (_, name: string, part?: string) => render(name, part))
        .replace(/<!--icon:(\w+)(?:#([\w-]+))?-->/g, (_, name: string, id?: string) => icon(name, id)),
    configureServer(server) {
      server.watcher.add(CONTENT);
      server.watcher.on("change", (file) => file.startsWith(CONTENT) && server.ws.send({ type: "full-reload" }));
    },
  };
}

// The app has paths of its own (/forecast/.., /climatology/.., /licenses), so its files have absolute URLs: it is served from the root
// of the web server, or from OTPROF_BASE (e.g. /otprof/, then adjust the routes in nginx.conf too).
// Dev server on another interface (e.g. to open it on a phone):  npm run dev -- --host <ip>
export default defineConfig({
  base: process.env.OTPROF_BASE ?? "/",
  // The software bundled into the app, with its licenses: shown on the licenses page (src/licenses.ts)
  build: { chunkSizeWarningLimit: 1500, license: { fileName: THIRD_PARTY } },
  server: { port: 5173, strictPort: true },
  preview: { port: 4173, strictPort: true },
  plugins: [devData(), devLicenses(), content()],
});
