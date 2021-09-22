# Copyright 2016 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. All Rights Reserved.
#
# Portion of this code is Copyright Geoscience Australia, Licensed under the
# Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License
# at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# The CEOS 2 platform is licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import gdal
import numpy as np
import xarray as xr
import os
import math
import datetime
import uuid
import rasterio
import functools
import operator
import warnings
import dask
from joblib import load

def get_range(platform, collection, level):
    """
    Obtain the "valid" value range for a given combination of platform, 
    collection, level, and data variable (does vary by data variable for some products).

    Parameters
    ----------
    platform: str
        A string denoting the platform to be used. Can be 
        "LANDSAT_5", "LANDSAT_7", or "LANDSAT_8".
    collection: string
        The Landsat collection of the data. 
        Can be any of ['c1', 'c2'] for Collection 1 or 2, respectively.
    level: string
        The processing level of the Landsat data. 
        Currently only 'l2' (Level 2) is supported.

    Returns
    -------
    range: dict or list or None
        A dict of 2-tuples (lists) denoting the range for each data variable with a recorded range.
        `None` otherwise.
    """
    range_dict = None
    if (platform, collection, level) in \
        [('LANDSAT_5', 'c1', 'l2'), ('LANDSAT_7', 'c1', 'l2'),
            ('LANDSAT_8', 'c1', 'l2')]:
        range_dict = {'red': [0, 10000], 'green': [0, 10000], 'blue': [0, 10000],
                      'nir': [0, 10000], 'swir1': [0, 10000], 'swir2': [0, 10000]}
    elif (platform, collection, level) in \
        [('LANDSAT_5', 'c2', 'l2'), ('LANDSAT_7', 'c2', 'l2'),
            ('LANDSAT_8', 'c2', 'l2')]:
        range_dict = {'red': [1, 65455], 'green': [1, 65455], 'blue': [1, 65455],
                      'nir': [1, 65455], 'swir1': [1, 65455], 'swir2': [1, 65455]}
    return range_dict


def convert_range(dataset, from_platform, from_collection, from_level,
                  to_platform, to_collection, to_level):
    """
    Converts an xarray.Dataset range from its product range 
    to that of another product.

    Parameters
    ----------
    dataset: xarray.Dataset
        The dataset to convert to another range.
    from_platform, from_collection, from_level: string
        The dataset's product's platform, collection, and level.
        For example, ('LANDSAT_8', 'c2', 'l2').
    to_platform, to_collection, to_level: string
        The platform, collection, and level to convert the 
        dataset's range to.
        For example, ('LANDSAT_7', 'c1', 'l2').
    
    Returns
    -------
    output_dataset: xr.Dataset
    """
    def convert_data_var(data_arr, data_var_name):
        """
        Convert an xarray of values from the 'from' dataset (`dataset`) to the 'to' dataset's values.
        
        Parameters
        ----------
        data_arr: xarray.DataArray
            The data to convert.
        data_var_name: np.ndarray
            The name for this data variable in `dataset` to convert to the 'to' dataset (platform, collection, level) range.
        
        Returns
        -------
        output_data_arr: xr.DataArray
        """
        # Load the model for the data variable.
        model_path = model_paths[data_var_name]
        model = load(model_path)
        
        # Reformat the input for the model and run it.
        nan_mask = np.isnan(data_arr)        
        X = dataset[[data_var_name]].stack(row=('latitude', 'longitude', ...)).to_array().transpose('row', 'variable')
        nan_mask_x = np.isnan(X).squeeze()
        X = X.where(~nan_mask_x, drop=True)
        y_pred = model.predict(X)
        
        # Reformat the output from the model to match the format of `data_arr`.
        output_data_arr = xr.full_like(data_arr, np.nan, dtype=np.float32)#data_arr.copy(deep=True)
        output_data_arr_stacked = output_data_arr.stack(row=('latitude', 'longitude', ...))
        output_data_arr_stacked.values[~nan_mask.stack(row=('latitude', 'longitude', ...)).values] = y_pred
        output_data_arr = output_data_arr_stacked.unstack(('row')).transpose(..., 'latitude', 'longitude')
        return output_data_arr
    
    if isinstance(dataset, xr.DataArray):
        dataset = dataset.to_dataset()
    # 1. Determine the data variables to convert.
    #    (If any data variables to convert do not have models, throw an error.)
    filepath = os.path.dirname(os.path.abspath(__file__))
    model_paths = {data_var: f'{filepath}/models/{from_platform}_{from_collection}_{from_level}_to_{to_platform}_{to_collection}_{to_level}_{data_var}.joblib' for data_var in list(dataset.data_vars)}
    data_vars_no_model = []
    for data_var in dataset.data_vars:
        model_path = model_paths[data_var]
        if not os.path.exists(model_path):
            data_vars_no_model.append(data_var)
    if len(data_vars_no_model) > 0:
        raise ValueError(f"The data variables {data_vars_no_model} in `dataset` do not have a model for this conversion.")
    # 2. For each data variable, apply the conversion model.
    output_dataset = dataset.copy()
    for data_var in output_dataset.data_vars:
        if isinstance(dataset[data_var].data, np.ndarray):
            output_dataset[data_var] = convert_data_var(dataset[data_var], data_var)
        elif isinstance(dataset[data_var].data, dask.array.core.Array):
            # If using Dask, collapse to 1 chunk to avoid a potential error.
            output_dataset[data_var] = dataset[data_var].chunk(-1).map_blocks(convert_data_var, (data_var,), template=dataset[data_var])
    return output_dataset

def reverse_array_dict(dictionary):
    """
    Returns a reversed version a dictionary of keys to list-like objects. Each value in each list-like
    becomes a key in the returned dictionary mapping to its key in the provided dictionary.
    """
    return_dict = {}
    for label, values in dictionary.items():
        for value in values:
            return_dict[value] = label
    return return_dict

def list_prod(lst):
    """Takes the product of elements in a list."""
    return functools.reduce(operator.mul, lst)

def check_for_float(array):
    """
    Check if a NumPy array-like contains floats.

    Parameters
    ----------
    array : numpy.ndarray or convertible
        The array to check.
    """
    try:
        return array.dtype.kind == 'f'
    except AttributeError:
        # in case it's not a numpy array it will probably have no dtype.
        return np.asarray(array).dtype.kind in numerical_dtype_kinds

def create_cfmask_clean_mask(cfmask):
    """
    Create a clean mask for clear land/water pixels,
    i.e. mask out shadow, snow, cloud, and no data
    
    Parameters
    ----------
    cfmask: xarray.DataArray
        cf_mask from the ledaps products
    
    Returns
    -------
    clean_mask: np.ndarray 
        boolean numpy array - clear land/water mask
    """

    #########################
    # cfmask values:        #
    #   0 - clear           #
    #   1 - water           #
    #   2 - cloud shadow    #
    #   3 - snow            #
    #   4 - cloud           #
    #   255 - fill          #
    #########################

    clean_mask = (cfmask == 0) | (cfmask == 1)
    return clean_mask.values

def create_default_clean_mask(dataset_in):
    """
    Creates a data mask that masks nothing.
    
    Parameters
    ----------
    dataset_in: xarray.Dataset
        dataset retrieved from the Data Cube.
    
    Raises
    ------
    ValueError
        if dataset_in is an empty xarray.Dataset.
    """
    data = None
    if isinstance(dataset_in, xr.Dataset):
        data_vars = list(dataset_in.data_vars)
        if len(data_vars) != 0:
            data = dataset_in[data_vars[0]].data
    elif isinstance(dataset_in, xr.DataArray):
        data = dataset_in.data
    clean_mask = None
    if isinstance(data, dask.array.core.Array):
        clean_mask = dask.array.ones_like(data, dtype='uint8')
    else:
        if data is None:
            clean_mask = np.ones(dataset_in.shape, dtype=np.bool)
        else:
            clean_mask = np.ones_like(data, dtype=np.bool)
    return clean_mask.astype(np.bool)

def get_spatial_ref(crs):
    """
    Get the spatial reference of a given crs.
    
    Parameters
    ----------
    crs: datacube.model.CRS
        Example: CRS('EPSG:4326')
    
    Returns
    -------
    ref: str 
        spatial reference of given crs
    """
    import osr

    crs_str = str(crs)
    epsg_code = int(crs_str.split(':')[1])
    ref = osr.SpatialReference()
    ref.ImportFromEPSG(epsg_code)
    return str(ref)

def perform_timeseries_analysis(dataset_in, band_name, intermediate_product=None, no_data=-9999, operation="mean"):
    """
    Parameters
    ----------
    dataset_in: xarray.Dataset
        dataset with one variable to perform timeseries on
    band_name: str
        name of the band to create stats for.
    intermediate_product: xarray.Dataset
        result of this function for previous data, to be combined here
    
    Returns
    -------
    dataset_out: xarray.Dataset
        dataset containing variables: 
        normalized_data, total_data, total_clean
    """

    assert operation in ['mean', 'max', 'min'], "Please enter a valid operation."

    data = dataset_in[band_name]
    data = data.where(data != no_data)

    processed_data_sum = data.sum('time')

    clean_data = data.notnull()

    clean_data_sum = clean_data.astype('bool').sum('time')

    dataset_out = None
    if intermediate_product is None:
        processed_data_normalized = processed_data_sum / clean_data_sum
        dataset_out = xr.Dataset(
            {
                'normalized_data': processed_data_normalized,
                'min': data.min(dim='time'),
                'max': data.max(dim='time'),
                'total_data': processed_data_sum,
                'total_clean': clean_data_sum
            },
            coords={'latitude': dataset_in.latitude,
                    'longitude': dataset_in.longitude})
    else:
        dataset_out = intermediate_product
        dataset_out['total_data'] += processed_data_sum
        dataset_out['total_clean'] += clean_data_sum
        dataset_out['normalized_data'] = dataset_out['total_data'] / dataset_out['total_clean']
        dataset_out['min'] = xr.concat([dataset_out['min'], data.min(dim='time')], dim='time').min(dim='time')
        dataset_out['max'] = xr.concat([dataset_out['max'], data.max(dim='time')], dim='time').max(dim='time')

    dataset_out.where(dataset_out != np.nan, 0)

    return dataset_out


def clear_attrs(dataset):
    """Clear out all attributes on an xarray dataset to write to disk."""
    from collections import OrderedDict

    dataset.attrs = OrderedDict()
    for band in dataset.data_vars:
        dataset[band].attrs = OrderedDict()


def create_bit_mask(data_array, valid_bits, no_data=-9999):
    """
    Create a boolean bit mask from a list of valid bits.

    Parameters
    ----------
    data_array: xarray.DataArray
        DataArray to extract bit information for.
    valid_bits: np.ndarray
        ints representing what bits should be considered valid.
    no_data: int
        no_data value for the data array.

    Returns
    -------
    out: np.ndarray
        NumPy array boolean mask signifying valid data.
    """
    assert isinstance(valid_bits, list) and isinstance(valid_bits[0], int), "Valid bits must be a list of integer bits"
    #do bitwise and on valid mask - all zeros means no intersection e.g. invalid else return a truthy value?
    valid_mask = sum([1 << valid_bit for valid_bit in valid_bits])
    clean_mask = (data_array & valid_mask).astype('bool')
    return clean_mask.values


def add_timestamp_data_to_xr(dataset):
    """
    Add timestamp data to an xarray dataset using the time dimension.

    Adds both a timestamp and a human readable date int to a dataset - int32 format required.
    modifies the dataset in place.
    """
    dims_data_var = list(dataset.data_vars)[0]

    timestamp_data = np.full(dataset[dims_data_var].values.shape, 0, dtype="int32")
    date_data = np.full(dataset[dims_data_var].values.shape, 0, dtype="int32")

    for index, acq_date in enumerate(dataset.time.values.astype('M8[ms]').tolist()):
        timestamp_data[index::] = acq_date.timestamp()
        date_data[index::] = int(acq_date.strftime("%Y%m%d"))
    dataset['timestamp'] = xr.DataArray(
        timestamp_data,
        dims=('time', 'latitude', 'longitude'),
        coords={'latitude': dataset.latitude,
                'longitude': dataset.longitude,
                'time': dataset.time})
    dataset['date'] = xr.DataArray(
        date_data,
        dims=('time', 'latitude', 'longitude'),
        coords={'latitude': dataset.latitude,
                'longitude': dataset.longitude,
                'time': dataset.time})


def write_geotiff_from_xr(tif_path, data, bands=None, no_data=-9999, crs="EPSG:4326",
                          x_coord='longitude', y_coord='latitude'):
    """
    NOTE: Instead of this function, please use `import_export.export_xarray_to_geotiff()`.

    Export a GeoTIFF from an `xarray.Dataset`.

    Parameters
    ----------
    tif_path: string
        The path to write the GeoTIFF file to. You should include the file extension.
    data: xarray.Dataset or xarray.DataArray
    bands: list of string
        The bands to write - in the order they should be written.
        Ignored if `data` is an `xarray.DataArray`.
    no_data: int
        The nodata value.
    crs: string
        The CRS of the output.
    x_coord, y_coord: string
        The string names of the x and y dimensions.
    """
    if isinstance(data, xr.DataArray):
        height, width = data.sizes[y_coord], data.sizes[x_coord]
        count, dtype = 1, data.dtype
    else:
        if bands is None:
            bands = list(data.data_vars.keys())
        else:
            assrt_msg_begin = "The `data` parameter is an `xarray.Dataset`. "
            assert isinstance(bands, list), assrt_msg_begin + "Bands must be a list of strings."
            assert len(bands) > 0 and isinstance(bands[0], str), assrt_msg_begin + "You must supply at least one band."
        height, width = data.dims[y_coord], data.dims[x_coord]
        count, dtype = len(bands), data[bands[0]].dtype
    with rasterio.open(
            tif_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=count,
            dtype=dtype,
            crs=crs,
            transform=_get_transform_from_xr(data, x_coord=x_coord, y_coord=y_coord),
            nodata=no_data) as dst:
        if isinstance(data, xr.DataArray):
            dst.write(data.values, 1)
        else:
            for index, band in enumerate(bands):
                dst.write(data[band].values, index + 1)
    dst.close()


def write_png_from_xr(png_path, dataset, bands, png_filled_path=None, fill_color='red', scale=None, low_res=False,
                      no_data=-9999, crs="EPSG:4326"):
    """
    Write a rgb png from an xarray dataset.
    Note that using `low_res==True` currently causes the file(s)
    for `png_path` and `png_filled_path` to not be created.

    Parameters
    ----------
    png_path: str
        path for the png to be written to.
    dataset: xarray.Dataset
        dataset to use for the png creation.
    bands: list
        a list of three strings representing the bands and their order
    png_filled_path: str
        optional png with no_data values filled
    fill_color:
        color to use as the no_data fill
    scale: tuple
        desired scale - tuple like (0, 4000) for the upper and lower bounds

    """
    assert isinstance(bands, list), "Bands must a list of strings"
    assert len(bands) == 3 and isinstance(bands[0], str), "You must supply three string bands for a PNG."

    tif_path = os.path.join(os.path.dirname(png_path), str(uuid.uuid4()) + ".tif")
    write_geotiff_from_xr(tif_path, dataset, bands, no_data=no_data, crs=crs)
    
    scale_string = ""
    if scale is not None and len(scale) == 2:
        scale_string = "-scale {} {} 0 255".format(scale[0], scale[1])
    elif scale is not None and len(scale) == 3:
        for index, scale_member in enumerate(scale):
            scale_string += " -scale_{} {} {} 0 255".format(index + 1, scale_member[0], scale_member[1])
    outsize_string = "-outsize 25% 25%" if low_res else ""
    cmd = "gdal_translate -ot Byte " + outsize_string + " " + scale_string + " -of PNG -b 1 -b 2 -b 3 " + tif_path + ' ' + png_path

    os.system(cmd)

    if png_filled_path is not None and fill_color is not None:
        cmd = "convert -transparent \"#000000\" " + png_path + " " + png_path
        os.system(cmd)
        cmd = "convert " + png_path + " -background " + \
            fill_color + " -alpha remove " + png_filled_path
        os.system(cmd)

    os.remove(tif_path)


def write_single_band_png_from_xr(png_path, dataset, band, color_scale=None, fill_color=None, interpolate=True,
                                  no_data=-9999, crs="EPSG:4326"):
    """
    Write a pseudocolor png from an xarray dataset.

    Parameters
    ----------
    png_path: str
        path for the png to be written to.
    dataset: xarray.Dataset
        dataset to use for the png creation.
    band: str
        The band to write to a png
    png_filled_path: str
        optional png with no_data values filled
    fill_color: 
        color to use as the no_data fill
    color_scale: str
        path to a color scale compatible with gdal.
    """
    assert os.path.exists(color_scale), "Color scale must be a path to a text file containing a gdal compatible scale."
    assert isinstance(band, str), "Band must be a string."

    tif_path = os.path.join(os.path.dirname(png_path), str(uuid.uuid4()) + ".png")
    write_geotiff_from_xr(tif_path, dataset, [band], no_data=no_data, crs=crs)

    cmd = "gdaldem color-relief -of PNG -b 1 " + tif_path + " " + \
        color_scale + " " + png_path
    os.system(cmd)

    if fill_color is not None:
        cmd = "convert -transparent \"#FFFFFF\" " + \
            png_path + " " + png_path
        os.system(cmd)
        if fill_color is not None and fill_color != "transparent":
            cmd = "convert " + png_path + " -background " + \
                fill_color + " -alpha remove " + png_path
            os.system(cmd)

    os.remove(tif_path)

def _get_transform_from_xr(data, x_coord='longitude', y_coord='latitude'):
    """Create a geotransform from an xarray.Dataset or xarray.DataArray.
    """

    from rasterio.transform import from_bounds
    geotransform = from_bounds(data[x_coord][0], data[y_coord][-1],
                               data[x_coord][-1], data[y_coord][0],
                               len(data[x_coord]), len(data[y_coord]))
    return geotransform


# Break the list l into n sized chunks.
def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def ignore_warnings(func, *args, **kwargs):
    """Runs a function while ignoring warnings"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ret = func(*args, **kwargs)
    return ret