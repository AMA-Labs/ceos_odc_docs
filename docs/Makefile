# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j "auto"
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Generate RST files from the utils code.
apidocs:
	rm -rf ./source/modules/developer_guide/generate
	sphinx-apidoc -o ./source/modules/developer_guide/generate data_cube_utilities/

livehtml:
	sphinx-autobuild -b html -c source --host 0.0.0.0 --port $${SPHINX_AUTOBUILD_PORT} --ignore "*_tmp_*" --ignore "*_old_*" --ignore "build/*" --ignore "source/modules/developer_guide/generate/*" $(SPHINXOPTS) source $(BUILDDIR)/html

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# %:: Makefile
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf build/
	rm -rf source/modules/developer_guide/generate/

# Required when Python source code changes (docstrings).
fullrebuild: clean apidocs html
