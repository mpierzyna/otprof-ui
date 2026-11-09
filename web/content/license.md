## Licenses

The OTProf-based products are optical turbulence forecasts and an optical turbulence climatology delivered as NetCDF files, CSV files, and interactive plots.
These data products are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), which excludes any warranty.
The products are derived from two third-party datasets listed below, which permit redistribution of derivatives.

The source code of this website and its data pipelines, [OTProf UI](https://github.com/mpierzyna/otprof-ui), is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html) if not stated otherwise.

The source code of the deep learning model used to estimate optical turbulence from the input datasets, [OTProf](https://github.com/mpierzyna/otprof), is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html) if not stated otherwise.
The architecture of the OTProf model (SQF-H) is derived from the Kaggle notebook ["LEAP: Training 1"](https://www.kaggle.com/code/shlomoron/leap-training-1?scriptVersionId=188874411) by Ron Shlomo, licensed under the Apache License 2.0.
The weights of the pretrained models are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) and are available on [Hugging Face](https://huggingface.co/maxiimilian/otprof-sqfh).

The OTProf training data are generated using the [Weather Research and Forecasting (WRF) model v4.5.2](https://github.com/wrf-model/WRF).
The code and config files to run WRF for this purpose are licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html) and published on GitHub as [OTProf WRF](https://github.com/mpierzyna/otprof-wrf).
The WRF output (i.e., the training data) is available on Zenodo under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (DOI: [10.5281/zenodo.23733024](https://doi.org/10.5281/zenodo.23733024)).

Technische Universiteit Delft hereby disclaims all copyright interest in the programs "OTProf" and "OTProf UI" written by the Author(s). Henri Werij, Faculty of Aerospace Engineering, Technische Universiteit Delft.

© 2026, Maximilian Pierzyna (excluding third-party code and data listed below)

### Third-party input data

OTProf optical turbulence forecasts are derived from data provided by the [**NOAA Global Forecast System (GFS)**](https://registry.opendata.aws/noaa-gfs-bdp-pds/), taken from the AWS Registry of Open Data every 6 hours whenever a new GFS cycle becomes available.
The original NOAA data have been altered by OTProf: the forecasts are not original NOAA data, and NOAA does not endorse them.

The OTProf-based optical turbulence climatology is derived from **ERA5 pressure level data** (Hersbach et al., 2023: ERA5 hourly data on pressure levels from 1940 to present, DOI: [10.24381/cds.bd0915c6](https://doi.org/10.24381/cds.bd0915c6)), provided by the Copernicus Climate Change Service (C3S) Climate Data Store (CDS) under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence.
The climatology contains modified Copernicus Climate Change Service data (2026): OTProf estimates optical turbulence from the ERA5 data, and the estimates are aggregated into monthly statistics.

### Third-party assets

OTProf UI ships the following third-party assets:

- **Basemap**: [Natural Earth](https://www.naturalearthdata.com), public domain, via
  [world-atlas](https://github.com/topojson/world-atlas), Copyright 2013-2019 Michael Bostock, ISC license.
- **Icons**: [Material Icons](https://github.com/google/material-design-icons) by Google, licensed under the
  [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
- **Formulas**: typeset with [MathJax](https://www.mathjax.org) (Apache License 2.0) when the page is built.
