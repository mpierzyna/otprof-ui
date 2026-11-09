// SPDX-FileCopyrightText: 2026 Maximilian Pierzyna
//
// SPDX-License-Identifier: GPL-3.0-or-later

// The software bundled into the app with its licenses, below the text of the licenses page (content/licenses.md):
// third-party-licenses.json, written by Vite when the app is built (build.license in vite.config.ts), so it lists
// exactly what the build contains. Loaded once, when the licenses page is first shown.

import { BASE } from "./router";

interface Entry {
  name: string;
  version: string;
  identifier?: string; // SPDX license expression
  text?: string; // the package's license file
}

let shown = false;

export async function showThirdPartyLicenses(el: HTMLElement) {
  if (shown) return;
  shown = true;
  const add = <K extends keyof HTMLElementTagNameMap>(parent: HTMLElement, tag: K, text?: string) => {
    const e = parent.appendChild(document.createElement(tag));
    if (text !== undefined) e.textContent = text;
    return e;
  };
  add(el, "h3", "Third-party software");
  const intro = add(el, "p");
  let entries: Entry[];
  try {
    const r = await fetch(`${BASE}third-party-licenses.json`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    entries = (await r.json()) as Entry[];
  } catch {
    intro.textContent = "The list of the software in this page is written when the app is built (npm run build).";
    return;
  }
  intro.textContent = "This page contains the following open-source software, under these licenses:";
  for (const p of entries) {
    const d = add(el, "details");
    d.className = "license-entry";
    const s = add(d, "summary", `${p.name} ${p.version}`);
    if (p.identifier) add(s, "span", p.identifier).className = "license-id";
    add(d, "pre", p.text ?? "No license file in the package.");
  }
}
