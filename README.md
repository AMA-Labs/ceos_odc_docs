# CEOS ODC Documentation

The Committee on Earth Observation Satellites (CEOS) Open Data Cube (ODC) documentation is a ReadTheDocs website containing documentation about CEOS products related to the ODC and general useful information about using the ODC. 

## Contents

* [Managing the Development Environment](#dev)
* [Editing the Documentation](#editing)
* [Deploying the Documentation Publicly to Read the Docs](#deploy)

## <a id="dev"></a> Managing the Development Environment

To start the development environment, run `make dev-up`.

To check the status of the development environment, run `make dev-ps` - this also shows the port of the development website (should be `8123`, address is `localhost:<port>`).

To restart the development environment, run `make dev-restart`.

To open a terminal to the development environment, run `make dev-ssh`.

## <a id="editing"></a> Editing the Documentation

This repository uses Sphinx to build HTML documentation from markdown documents - specifically reStructuredText (RST) and Standard Markdown (mainly reStructuredText).

The Sphinx website has a good primer on RST [here](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html).

The HTML pages are built on start and for changed markdown files automatically within a few seconds after saving a file - including refreshing any browser tabs viewing the changed HTML files.

To build the HTML pages from the markdown files manually, first connect to the development container: `make dev-ssh`. 

When in the shell on the container, run these commands to perform the corresponding actions:

| command            | result                                                                               |
|--------------------|--------------------------------------------------------------------------------------|
| `make html`        | Build the HTML pages from the markdown                                               |
| `make apidocs`     | Build the API documentation (CEOS ODC Utilities)                                     |
| `make fullrebuild` | Remove old build products and rebuild the HTML - including for the API documentation |
+--------------------+--------------------------------------------------------------------------------------+

## <a id="deploy"></a> Deploying the Documentation Publicly to Read the Docs

Follow these steps to deploy the documentation to readthedocs.org:

1. Sign up on the [Read the Docs website](https://readthedocs.org/).
2. Once you have signed in, on your [dashboard](https://readthedocs.org/dashboard/) create a new project with the `Import a Project` button.
3. Select this repository and specify the project details, such as its name and default branch.
4. To trigger a build and deployment of the documentation in the repository, click the `Build version` button on the project page.
