// SPDX-FileCopyrightText: 2026 Maximilian Pierzyna
//
// SPDX-License-Identifier: GPL-3.0-or-later

// Notes of the data shown (meta.json "notes"): plain text, one paragraph per block of lines. The texts of the app are
// markdown rendered when it is built (vite.config.ts); the browser renders no markdown.

/** `text` into `el`, as paragraphs separated by blank lines; `el` is hidden without text. */
export function showNotes(el: HTMLElement, text?: string) {
  const paragraphs = (text ?? "").split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
  el.replaceChildren(...paragraphs.map((p) => Object.assign(document.createElement("p"), { textContent: p })));
  el.hidden = !paragraphs.length;
}
