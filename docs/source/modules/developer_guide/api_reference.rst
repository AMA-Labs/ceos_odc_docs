API Reference
=============

.. currentmodule:: data_cube_utilities

.. highlight:: python

Data Info
---------

.. autosummary::
   :nosignatures:

   dc_load.is_dataset_empty
   dc_load.get_product_extents
   dc_load.get_overlapping_area
   dc_load.find_desired_acq_inds
   dc_utilities.get_range
   data_stats.find_gaps

Data Masking/Cleaning
---------------------

General
^^^^^^^

These masking utilities are for generic use with xarrays.

.. autosummary::
   :nosignatures:

   clean_mask.xarray_values_in
   clean_mask.create_circular_mask
   shapefile_mask.shapefile_mask

Dataset-specific
^^^^^^^^^^^^^^^^

Landsat
"""""""

These masking utilities serve to clean Landsat data.

We recommend using ``landsat_clean_mask_full`` for simplicity and ``landsat_qa_clean_mask`` if you need to be specific about what is masked (e.g. cloud shadow).

All of these functions except ``landsat_clean_mask_invalid`` require the QA data (often called ``pixel_qa`` as a measurement for Landsat products in ODC).

.. autosummary::
   :nosignatures:

   clean_mask.landsat_clean_mask_invalid
   clean_mask.landsat_qa_clean_mask
   clean_mask.landsat_clean_mask_full

Sentinel-2
""""""""""

These masking utilities serve to clean Sentinel-2 data.

.. autosummary::
   :nosignatures:

   clean_mask.sentinel2_fmask_clean_mask

Data Combining
--------------

.. autosummary::
   :nosignatures:

   dc_load.match_prods_res
   dc_load.match_dim_sizes
   dc_load.get_product_extents

Data Transformations
--------------------

Aggregation/Rescaling
^^^^^^^^^^^^^^^^^^^^^

These utilities allow binning, grouping, and 
rescaling features (such as resolution) beyond those 
offered by xarray, or having simplified interfaces, or both.

Note that ``xr_scale_res`` is a simpler interface to ``xr_interp``.

.. autosummary::
   :nosignatures:

   aggregate.xr_sel_time_by_bin
   dc_load.reduce_on_day
   aggregate.xr_scale_res
   aggregate.xr_interp

Kernel-Based Filters
^^^^^^^^^^^^^^^^^^^^

There are 2 kinds of kernel-based filters 
offered here: seletive and non-selective.

Selective filters apply to only some data 
points. These include:
[``raster_filter.lone_object_filter``]

Non-selective filters apply to all data 
points. These include:
[``stats_filter_3d_composite_2d``, ``stats_filter_2d``]

.. autosummary::
   :nosignatures:

   raster_filter.lone_object_filter
   raster_filter.stats_filter_3d_composite_2d
   raster_filter.stats_filter_2d

Conversion
^^^^^^^^^^

Sometimes data needs to be transformed to more closely
match another dataset (e.g. converting Landsat 8 Level 2 
Collection 2 data to approximate Landsat 8 Level 2 
Collection 1 data to accomodate algorithms that 
only support the latter).

.. autosummary::
   :nosignatures:

   dc_utilities.convert_range

Visualization
-------------

2D Data Display
^^^^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   plotter_utils.xarray_imshow
   dc_rgb.rgb

Plotting
^^^^^^^^

.. autosummary::
   :nosignatures:

   plotter_utils.xarray_time_series_plot
   plotter_utils.binary_class_change_plot
   plotter_utils.create_discrete_color_map
   plotter_utils.create_gradient_color_map
   plotter_utils.impute_missing_data_1D

Figure Sizing
^^^^^^^^^^^^^

``figure_ratio`` is often used to set the size of `matplotlib` figures and axes (created by ``matplotlib.pyplot.Figure()`` or ``matplotlib.pyplot.subplots()``).

.. autosummary::
   :nosignatures:

   plotter_utils.figure_ratio

Animation
^^^^^^^^^

``xr_animation`` is from Geoscience Australia's utilities `here <https://github.com/GeoscienceAustralia/dea-notebooks/blob/93ecf194963d7b0047486e2e439525573cfecc11/Tools/dea_tools/plotting.py>`_.

.. autosummary::
   :nosignatures:

   plotter_utils.xr_animation

Dask
----

.. autosummary::
   :nosignatures:

   dask.create_local_dask_cluster


Machine Learning
----------------

Clustering
^^^^^^^^^^

.. autosummary::
   :nosignatures:

   dc_clustering.kmeans_cluster_dataset
   dc_clustering.birch_cluster_dataset
   dc_clustering.get_frequency_counts

EO Topics
---------

Urbanization
^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   urbanization.NDBI
   urbanization.DBSI

Fires
^^^^^

.. autosummary::
   :nosignatures:

   vegetation.NBR

Vegetation
^^^^^^^^^^

.. autosummary::
   :nosignatures:

   vegetation.EVI
   vegetation.EVI2
   vegetation.NDVI
   vegetation.SAVI

Water
^^^^^

Water Detection
"""""""""""""""

.. autosummary::
   :nosignatures:

   dc_water_classifier.NDWI
   dc_water_classifier.wofs_classify

Water Quality
"""""""""""""

.. autosummary::
   :nosignatures:

   dc_water_quality.tsm

Coastlines
""""""""""

.. autosummary::
   :nosignatures:

   dc_coastal_change.compute_coastal_change

Landslides
^^^^^^^^^^

.. autosummary::
   :nosignatures:

   dc_slip.compute_slip

Land Classification
^^^^^^^^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   dc_fractional_coverage_classifier.frac_coverage_classify

Export
------

.. autosummary::
   :nosignatures:

   import_export.export_xarray_to_netcdf
   import_export.export_xarray_to_multiple_geotiffs
   import_export.export_xarray_to_geotiff

Mosaics
-------

.. autosummary::
   :nosignatures:

   dc_mosaic.create_min_max_var_mosaic
   dc_mosaic.create_mosaic
   dc_mosaic.create_mean_mosaic
   dc_mosaic.create_median_mosaic
   dc_mosaic.create_hdmedians_multiple_band_mosaic

