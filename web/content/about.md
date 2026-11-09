### How it is made

This website shows live forecasts and a climatology of optical turbulence profiles ($C_n^2$) and column-integrated
parameters (Fried parameter $r_0$ and scintillation index $\sigma_I^2$) over the Netherlands, estimated by the deep
learning model OTProf. The OTProf system is composed of the following three packages:

1. [**otprof-wrf**](https://github.com/mpierzyna/otprof-wrf): Code and config files to generate $C_n^2$ training data
   by post-processing output from the [Weather Research and Forecasting (WRF) model](https://github.com/wrf-model/wrf)
   with the variance-based $C_n^2$ parameterization of [He and Basu (2015)](https://doi.org/10.1117/12.2188227).
2. [**otprof**](https://github.com/mpierzyna/otprof): Code for training and inference of the OTProf deep learning model.
3. [**otprof-ui**](https://github.com/mpierzyna/otprof-ui): Code of the web UI to show OTProf-based $C_n^2$ forecasts
   and climatology, i.e. this website, and of the pipelines that compute them from GFS and ERA5.

The method and its performance are described in
[📄 Pierzyna, Basu, Saathof (2026, preprint)](https://arxiv.org/abs/2604.09346).

### Licenses and terms of use
The OTProf data products (forecasts and climatology) are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), which
excludes any warranty. See [Licenses](/licenses) for the full details of how you may use them, and for the third-party
data and software they build on.
