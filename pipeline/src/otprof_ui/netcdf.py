# SPDX-FileCopyrightText: 2026 Maximilian Pierzyna
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""NetCDF files of both pipelines: atomic writing, fixed time encoding, the licence and the credits of the data for
download."""

import numpy as np
import xarray as xr

LICENSE = "CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)"  # of the data for download

# Credits of the input data and references, in the files for download (global attributes `acknowledgement` and
# `references`) and, for the climatology, in its meta.json for the web app's CSV files. The same as on the web app's
# Licenses page (web/content/license.md).
ARTICLE = (
    "Pierzyna, M., Basu, S., Saathof, R. (2026): OTProf: estimating high-resolution profiles of optical turbulence (Cn2) "
    "from reanalysis using deep learning. arXiv, doi:10.48550/arXiv.2604.09346"
)
ERA5_REFERENCE = (
    "Hersbach, H. et al. (2023): ERA5 hourly data on pressure levels from 1940 to present. Copernicus Climate Change "
    "Service (C3S) Climate Data Store (CDS), doi:10.24381/cds.bd0915c6"
)
GFS_ACKNOWLEDGEMENT = (
    "Derived from NOAA Global Forecast System (GFS) data (https://registry.opendata.aws/noaa-gfs-bdp-pds/). The original "
    "NOAA data have been altered by OTProf: these are not original NOAA data, and NOAA does not endorse them."
)


def era5_acknowledgement(year: int) -> str:
    """The credit of the ERA5 data (CC BY 4.0) in a product made in `year`."""
    return (
        f"Contains modified Copernicus Climate Change Service data ({year}): ERA5 hourly data on pressure levels from "
        "1940 to present (Hersbach et al., 2023, doi:10.24381/cds.bd0915c6), licensed under CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). OTProf estimates optical turbulence from the ERA5 data; the "
        "estimates are aggregated into monthly statistics."
    )


# Fixed encoding for all datetimes; otherwise xarray infers units per file (e.g. "days since" for single-lead
# files), which is then inherited by downstream steps and cannot represent their 3-hourly times.
TIME_ENCODING = {"units": "hours since 1970-01-01", "dtype": "int64"}


def to_netcdf(ds: xr.Dataset, path, **kwargs):
    """`ds.to_netcdf` with all datetime variables encoded with `TIME_ENCODING` (and `encoding` given)."""
    encoding = {v: TIME_ENCODING for v in ds.variables if np.issubdtype(ds[v].dtype, np.datetime64)}
    return ds.to_netcdf(path, encoding=encoding | kwargs.pop("encoding", {}), **kwargs)


def to_netcdf_atomic(ds: xr.Dataset, path, **kwargs):
    """`to_netcdf` to `<path>.part`, renamed to `path` when complete: an interrupted write leaves no file at `path`."""
    part = path.with_name(path.name + ".part")
    to_netcdf(ds, part, **kwargs)
    part.replace(path)
