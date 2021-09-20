CEOS ODC-GEE Technical Documentation
====================================

Operation Requirements
----------------------

The ODC-GEE integration package ([GitHub](https://github.com/ceos-seo/odc-gee)) has a few requirements to operate properly.

Operation Requirement 1: Supported Metadata Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**The ODC index database used by your environment must support the `eo3` metadata type.** This can be checked by running `datacube metadata list` in your ODC environment. If eo3 is not listed, then you will need to add it. The default eo3 type definition can be found [here](https://github.com/opendatacube/datacube-core/blob/datacube-1.8.3/datacube/index/default-metadata-types.yaml). To add it, save the eo3 definition in a `.yaml` file then run the following command: `datacube metadata add <your_eo3.yaml>`.

Operation Requirement 2: Earth Engine Credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the ODC-GEE integration package, you must be registered as an Earth Engine developer. If not, you may submit an [application to Google](https://signup.earthengine.google.com/).

You will need [GEE service account credentials](https://developers.google.com/earth-engine/guides/service_account) for your account - specifically the private key JSON file.
Put your version of this JSON file here: `odc_gee/config/credentials.json`.

(Optional) You can also create a JSON file defining the spatial areas associated with region names. An example is provided in `odc_gee/opt/config/odc-gee/regions.json`. Put your version of this JSON file here: `odc_gee/config/regions.json`.

Adding New GEE Datasets as ODC Products
---------------------------------------

To use a GEE dataset from the [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/), a new product must be created using the `new_product` command. Format: `new_product --asset <asset_id> <product_name.yaml>` where the `asset_id` is provided in the "Earth Engine Snippet" string on the dataset's page on the catalog and `<product_name.yaml>` is the path to the output YAML file containing the ODC product definition. For example, to index [Landsat 8 Level 2 Collection 2 Tier 1](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2?hl=en) data: `new_product --asset LANDSAT/LC08/C02/T1_L2 ls8_l2_c2_gee.yaml`. The full process is as follows:

1. Run the `new_product` command to create the product definition.
2. Reformat the product definition to match a standard format, such as [this one from the ODC Indexer](https://github.com/ceos-seo/odc_manual_indexer/blob/develop/prod_defs/Landsat/collection_2/ls8_l2_c2.yaml).
3. Change the `aliases` field for the measurements as desired. Do NOT change the `name` field of any measurement - creating the product will fail if the `name` fields are changed.
4. Run `datacube product add <path-to-product-definition-file>` to add the product.

Notably, you will need to add a `storage` section with `crs` and `resolution` entries to avoid having to specify the `output_crs` and `resolution` each time data is loaded from the product.

After adding the product, it is a **non-indexed GEE product** (or ["undefined product"](https://github.com/ceos-seo/odc-gee#undefined-product)). It must be loaded using the [ODC-GEE `datacube.Datacube` wrapper class](https://github.com/ceos-seo/odc-gee#datacube-wrapper).

Once you have confirmed that data is loading for the newly defined product, you are welcome to add a pull request to the [ODC Indexer](https://github.com/ceos-seo/odc_manual_indexer) repository to add the new product definition to the `prod_defs` directory. Prefix the product definition file with `_google`.

The data can be indexed using the `index_gee` command, making it an **indexed GEE product**, but **this is deprecated**. Format: `index_gee --asset <asset_id> --product <product_name> [--latitude (lat1, lat2) --longitude (lon1, lon2) --time (YYYY-MM-DD, YYYY-MM-DD) --region <region_name>]` (for information on the optional arguments and others not listed here, run `index_gee --help`). For example, to index [Landsat 8 Level 2 Collection 2 Tier 1](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2?hl=en) data for the United States: `index_gee --asset LANDSAT/LC08/C02/T1_L2 --product <product_name> --latitude (25.3168, 49.4885) --longitude (-125.2052, -66.6657)`. Data for these products can be loaded by the normal `datacube.Datacube` class.

Using GEE vs non-GEE Data
-------------------------

To load data from non-GEE products, use the `datacube.Datacube` class as always:

```python
from datacube import Datacube
dc = datacube.Datacube()
```

To load data from GEE products, use the `odc_gee.earthengine.Datacube` class:

```python
from odc_gee.earthengine import Datacube as GEE_Datacube
dc = GEE_Datacube()
```

To load data from indexed GEE products (remember **this is deprecated**), use the `datacube.Datacube` class.

GEE versus Alternative Datasources
----------------------------------

These are the benefits and penalties of loading data from Google Earth Engine through the ODC-GEE module instead of from other datasources such as S3.

Benefits:

1. Data does not need to be indexed before loading, which allows new datasets to be added and queried quickly, which allows faster prototyping. This also results in a much smaller ODC index database.
2. There is no cost to loading data from GEE.

Penalties:

1. Data has a very low throughput - just a few MiB per second.
2. (Advanced) Using `dask_chunks` in the `load()` call does not work as expected. Normally, loads specifying the `dask_chunks` parameters will not immediately load data - instead creating the plan to load data with Dask. Instead, the data immediately begins loading as if `dask_chunks` was not specified. This can be problematic for datasets that are larger than the amount of available memory. This problem does not occur when loading data using the normal `datacube.Datacube` class.
