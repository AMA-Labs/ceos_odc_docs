CEOS ODC Products Overviews
===========================

CEOS ODC UI
-----------
The CEOS ODC UI (`UI GitHub <https://github.com/ceos-seo/data_cube_ui>`_) is a Python Django webapp
that uses the ODC to conduct some predefined analysis, such
as cloud coverage estimation, water quality estimation, and coastal change detection.

The UI was designed to favor simplicity for casual users, but see the notebooks (mentioned below) before attempting to use the UI, since the UI is currently dated and harder to manage in comparison.

CEOS ODC Notebooks
------------------
The CEOS ODC Notebooks (`Notebooks GitHub <https://github.com/ceos-seo/data_cube_notebooks>`_) is a collection of Jupyter Notebooks in a `JupyterLabs <https://jupyter.org/>`_ environment uses the ODC to analyze satellite data.

Notebooks allow users to write code to conduct analyses. Some technologies such as widgets (`from the Panel library <https://panel.holoviz.org/>`_) allow notebooks to be more easily usable - even by causal users (non-programmers).

CEOS ODC Utilities
------------------
The CEOS ODC Utilities (`Utils GitHub <https://github.com/ceos-seo/data_cube_utilities>`_) are a collection of Python files that provide several tools that conduct water detection, suspended matter estimation (water particulate pollution), coastline classification and change detection, and plotting - among other things.

CEOS ODC Indexer
----------------
The CEOS ODC Indexer (`Indexer GitHub <https://github.com/ceos-seo/odc_manual_indexer>`_) provides convenient means of processing and indexing data for ODC environments.

CEOS ODC-GEE Integration Package
--------------------------------
The CEOS ODC-GEE integration package (`ODC-GEE GitHub <https://github.com/ceos-seo/odc-gee>`_) allows Google Earth Engine (GEE) data to be loaded into ODC environments.

This is particularly useful since GEE has many datasets and they can be "indexed" very quickly with ODC-GEE. Indexing a product only requires a product definition to be created (should be reformatted to look more like product definitions in the ODC Indexer) and added with ``datacube product add`` to allow an environment with ODC-GEE to be able to load data from it.

However, note that the throughput of the GEE API is quite slow, so loading data with ODC-GEE is also quite slow compared to loading data from data sources such as Amazon S3.
