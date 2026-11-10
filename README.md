<!--
SPDX-FileCopyrightText: 2026 Maximilian Pierzyna

SPDX-License-Identifier: GPL-3.0-or-later
-->

# OTProf UI

Static web app showing OTProf optical turbulence forecasts and a 20-year climatology over the Netherlands.
Forecasts are derived from the NOAA [Global Forecast System](https://registry.opendata.aws/noaa-gfs-bdp-pds/) and the climatology is based on [ECMWF's ERA5 pressure level](https://doi.org/10.24381/cds.bd0915c6) data.

This repository is part of a set of repositories:
- [`otprof`](https://github.com/mpierzyna/otprof): Code to train a new OTProf model or run a pretrained model. A snapshot of this repository is available on Zenodo (DOI: 10.5281/zenodo.24084350). The weights of OTProf, pretrained on the Netherlands, are available on Hugging Face (https://huggingface.co/maxiimilian/otprof-sqfh).
- [`otprof-wrf`](https://github.com/mpierzyna/otprof-wrf): Code to generate the WRF-based $C_n^2$ training data. The generated training dataset and a snapshot of the `otprof-wrf` code are available on Zenodo (DOI: 10.5281/zenodo.23733024).
- [`otprof-ui`](https://github.com/mpierzyna/otprof-ui) (**this repository**): Code of the web UI to show OTProf-based $C_n^2$ forecasts and climatology. Check it out at [**https://otprof.mpier.eu**](https://otprof.mpier.eu)!

📝 The **article** presenting the method in detail and evaluating its performance is available on arXiv: [arXiv:2604.09346](https://arxiv.org/abs/2604.09346).
Please refer to the [License](#license) and [How to cite](#how-to-cite) sections if you would like to use this software or its products for your own work.

This software has been developed by [**Maximilian Pierzyna**](https://orcid.org/0000-0002-0596-8374), Technische Universiteit Delft.

## Overview

This repository contains both halves of the website: the **pipelines** that run OTProf on new GFS forecasts and on
ERA5, and the **web app** that shows their results. The pipelines write static files, and any static web server (e.g.
nginx) delivers them together with the built app. No code runs on the server; all interaction happens in the browser.

```
GFS (every 6 h) ──► pipeline/forecast/    ──┐
                                            ├──► static data files ──► web server ──► web app (browser)
ERA5 (one-off)  ──► pipeline/climatology/ ──┘    docs/DATA_FORMAT.md
```

### What the web app shows

- **Live forecast:** maps of $C_n^2$, the Fried parameter $r_0$ and the scintillation index $\sigma_I^2$ over the 5-day
  forecast and over height, vertical profiles and time-height plots at any grid point, and every forecast run for
  download as NetCDF.
- **Climatology:** monthly statistics of the same variables from ERA5, for all hours, day or night, with their annual
  and diurnal cycles at any grid point (box or violin plots), also for download as NetCDF.
- **Shareable views:** the URL holds the variable, time, height and location shown, so any view can be linked.

### Repository layout

```
web/          the web app (Vite + TypeScript, MapLibre GL, d3)
  content/    texts of the app as markdown (title, disclaimer, about, licenses), see web/content/README.md
  public/     config.json: variables (labels, units, colour maps), defaults of the view
pipeline/     the pipelines writing the data, see pipeline/README.md
  forecast/     GFS forecasts, every 6 h
  climatology/  ERA5 climatology, one-off
  otprof/       the model (git submodule)
docs/         DATA_FORMAT.md: the contract between the pipelines and the web app
Dockerfile, docker-compose.yml, nginx.conf    the deployment
```

## Getting started

Clone with the submodule (needed for the pipelines only):

```sh
git clone --recurse-submodules https://github.com/mpierzyna/otprof-ui.git
# or, in an existing clone:
git submodule update --init
```

### Data

The web app needs data from the pipelines, in `pipeline/data/webui/` by default. How to run the forecast and the
climatology pipelines, and how to upload their data to the web server, is described in
[`pipeline/README.md`](pipeline/README.md). The format of the data is specified in
[`docs/DATA_FORMAT.md`](docs/DATA_FORMAT.md).

### Web app

```sh
cd web && npm install
npm run dev                                       # http://localhost:5173, pipeline/data/webui served at /data/
OTPROF_UI_DATA=<data dir> npm run dev           # other data
npm run build && npm run preview -- --host <ip>   # production build, http://<ip>:4173
```

The dev and preview servers serve the data at `/data/`; the build does not contain them. To look at the app from
another device (e.g. a phone), use the preview: the dev server reloads the page whenever its live-reload connection
drops (screen lock, app switch, network change) or a source file changes.

The app needs WebGL (MapLibre). The basemap is Natural Earth 1:10m, cut to the region in
`web/scripts/make_basemap.mjs` (widen it for larger domains); it is generated before `dev` and `build`.

**Texts:** edit the markdown in `web/content/` (rendered into `index.html` at build time). Notes of a single forecast
run come from its `meta.json` (`"notes"`, plain text). Links like `[text](/forecast/r0?lat=52&lon=5&z=1000&t=12)` set the view.

## Deployment

### With Docker

The server runs a clone of this repository. `Dockerfile` builds the app in a Node stage and puts `web/dist/` with
`nginx.conf` into an nginx image. `docker-compose.yml` runs it on port 8080 with the data directory `./data` mounted
read-only at `/data/`; the pipelines' upload (`pipeline/upload.sh`) fills that directory.

```sh
git clone https://github.com/mpierzyna/otprof-ui.git && cd otprof-ui
docker compose up -d --build                         # first start
git pull --ff-only && docker compose up -d --build   # update: deploys texts, config and app
git checkout <commit> && docker compose up -d --build   # rollback
```

Local changes to the setup (ports, networks) go into `docker-compose.override.yml` (git-ignored), e.g. to reach the
container through a reverse proxy network instead of a published port. TLS is not part of the image: put the container
behind a reverse proxy.

To test the image locally with the pipelines' data: link or copy `pipeline/data/webui` to `./data`, then run
`docker compose up --build` and open http://localhost:8080.

### Without Docker

`cd web && npm ci && npm run build`, copy `web/dist/` to the web root, put the data in `<web root>/data/` and use
`nginx.conf` as the server block (adjust `root` and `listen`). It sets what the app needs: the MIME types (`.nc`,
`.md`, `.mjs`), the app's routes, compression, caching and the content security policy.

### Paths

The app has paths of its own (`/forecast/..`, `/climatology/..`, `/licenses`), which the web server answers with
`index.html` (`nginx.conf`), so it is served from the root of its host. For a subdirectory: build with
`OTPROF_BASE=/otprof/` and adjust the routes in `nginx.conf`. Link previews (Slack, WhatsApp, ...) need the image's
absolute URL: build with `OTPROF_URL=https://<host>` when the app is served from another host.

## Releases

The web app and the pipelines share one version, kept in sync by [bump-my-version](https://github.com/callowayproject/bump-my-version)
(`.bumpversion.toml`): `package.json`, `package-lock.json`, `pyproject.toml`, `uv.lock` and `CITATION.cff`. From
a clean working tree:

```sh
uvx bump-my-version bump patch   # or minor, major: commits and tags v<version>
```

## How to cite

If you use this software, please cite the accompanying article (see [`CITATION.cff`](./CITATION.cff)):

> M. Pierzyna, S. Basu, R. Saathof (2026): OTProf: estimating high-resolution profiles of optical turbulence ($C_n^2$) from reanalysis using deep learning. Preprint, arXiv. [doi:10.48550/arXiv.2604.09346](https://doi.org/10.48550/arXiv.2604.09346)

## AI statement

The web app and the data pipelines in this repository were conceptualized and designed by the authors and implemented
with Claude Opus 5.5 (Anthropic, model ID `claude-opus-5-5`), used through Claude Code. The authors defined the
scientific content, the features, the user interface and its layout, and directed and reviewed the implementation.
Claude wrote most of the code, documentation, and project configuration. The authors have carefully reviewed and
tested all AI-assisted contributions.

## License

Unless otherwise noted, the content of this repository is licensed under **GNU General Public License v3.0 or later**
(see [`COPYING`](./COPYING)). The repository follows the [REUSE](https://reuse.software) specification: every file
states its license, in its header or in [`REUSE.toml`](./REUSE.toml); check with `reuse lint`.

The data shown on the website are licensed separately, under CC BY-SA 4.0 (see the Licenses page of the website).

### Third-party code

The icons of the web app ([`web/src/icons.ts`](web/src/icons.ts)) are [Material Icons](https://github.com/google/material-design-icons)
by Google, licensed under the Apache License 2.0 (see [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt)); some of
their paths are written in a shorter form. The GitHub mark before the links to the OTProf repositories
([`web/src/github-mark.svg`](web/src/github-mark.svg)) is from GitHub's [Octicons](https://github.com/primer/octicons),
licensed under the MIT License (see [`LICENSES/MIT.txt`](LICENSES/MIT.txt)).

The built web app also contains open-source packages from npm (MapLibre GL JS, d3, the Inter font), each under its
own license: the build lists them with their license texts (`third-party-licenses.json`, written by Vite), and the
Licenses page of the website shows that list. The basemap is generated at build time from
[Natural Earth](https://www.naturalearthdata.com) (public domain) via [world-atlas](https://github.com/topojson/world-atlas)
(ISC); the Licenses page credits it under its third-party assets.

## Copyright notice

Technische Universiteit Delft hereby disclaims all copyright interest in the program "OTProf UI" written by the
Author(s). Henri Werij, Faculty of Aerospace Engineering, Technische Universiteit Delft.
