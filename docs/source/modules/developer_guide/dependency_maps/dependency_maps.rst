Dependency Maps
===============

Below is a map of CEOS ODC environments and their dependency chains.

* Each cell is a Docker repository (which can have many images).
* The names have this format: 
  **<image-name>[:version] 
  (repo-path: (<hyperlink-to-repo-or-Dockerfile-in-repo>))**
* The image version (**[:version]**) is optional, as denoted by the square brackets (**[]**).
* If the **repo-path** is to a repo instead of a Dockerfile in a repo, check the **build** directory in the repo for the Dockerfile.
* Note that **image** and **image:latest** (or even **image:odc<odc_version>**) may
  or may not be identical (diagram is a simplification).

.. list-table:: CEOS ODC Dependency Map
   :widths: 20 20 20 20
   :header-rows: 0

   * - 
     - ubuntu:20.04
     - 
     - 
   * - 
     - \|
     - 
     - 
   * - 
     - | ubuntu-base 
       | (repo-path: 
       | `datacube-base/ubuntu-base <https://github.com/jcrattz/datacube-base/blob/master/ubuntu-base/Dockerfile>`_)
     - 
     - 
   * - 
     - \|
     - 
     - 
   * - 
     - | datacube-base
       | (repo-path: `datacube-base <https://github.com/jcrattz/datacube-base/blob/master/Dockerfile>`_)
     - 
     - 
   * - v\-
     - \|
     - \-v
     - 
   * - | data_cube_notebooks
       | (repo-path: `data_cube_notebooks <https://github.com/ceos-seo/data_cube_notebooks>`_)
     - | data_cube_ui
       | (repo-path: `data_cube_ui <https://github.com/ceos-seo/data_cube_ui>`_)
     - | odc_manual_indexer
       | (repo-path: `odc_manual_indexer <https://github.com/ceos-seo/odc_manual_indexer>`_)
     - \-v
   * - \|
     - \-v \-\>
     - \-v
     - \|
   * - | odc_drone_paper_notebooks
       | (repo-path: `odc_drone_paper_notebooks <https://github.com/jcrattz/odc_drone_paper_notebooks>`_)
     - | odc_training_notebooks
       | (repo-path: `odc_training_notebooks <https://github.com/jcrattz/odc_training_notebooks>`_)
     - | odc_va_cube_notebooks
       | (repo-path: `odc_va_cube_notebooks <https://github.com/jcrattz/odc_va_cube_notebooks>`_)
     - | odc_manual_indexer_init
       | (repo-path: `odc_db_init <https://github.com/jcrattz/odc_db_init>`_)
   * - \|\-\>
     - \|
     - \<\-\|
     - \|
   * - 
     - | odc_platform
       | (repo-path: `odc_platform <https://github.com/jcrattz/odc_platform>`_)
     - \<\-
     - \<\-\|

