<!--
SPDX-FileCopyrightText: 2026 Maximilian Pierzyna

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Texts of the app

Markdown, rendered into `index.html` when the app is built (`vite.config.ts`, plugin `content`): edit, then push and
deploy. `npm run dev` reloads on every change. Links starting with `/forecast` or `/climatology` set the view (e.g.
`/forecast/r0?lat=52&lon=5&z=1000&t=12`), `/licenses` opens the licenses page, other links open in a new tab. Footnotes: `text[^1]` and, anywhere in the file, `[^1]: the note` (numbered in order, listed below the text). LaTeX: `$C_n^2$` inline, `$$...$$` displayed (MathJax, rendered at build time); a
literal dollar sign: `\$`.

| file | shown |
|---|---|
| `title.md` | the title (inline markdown; plain text in the browser tab and link previews) |
| `subtitle.md` | below the title (inline markdown; plain text as the description of the page in link previews and search results) |
| `disclaimer.md` | the callout above the panels and in the download dialog; its first heading is the callout's title |
| `about.md` | the notes card ("What am I seeing?"), last: the general part |
| `forecast.md` | the notes card in the forecast, first |
| `climatology.md` | the notes card in the climatology, first |
| `download.md` | the download dialog: its first heading is the dialog's title, the rest is shown above the buttons |
| `licenses.md` | the licenses page (tab at the right, `/licenses`), followed by the bundled software and its licenses (generated when the app is built) |
| `footer.md` | the footer below the panels: the keys (inline markdown) |
| `credit.md` | the footer on every page: who made it (inline markdown) |

Labels and units of the variables are in `public/config.json`; short hints of the plots are in `src/main.ts`.
