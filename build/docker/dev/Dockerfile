FROM jcrattzama/datacube-base:odc1.8.3
# FROM sphinxdoc/sphinx:3.0.1

ARG ROOT_DIR
WORKDIR ${ROOT_DIR}

COPY build/requirements.txt build/requirements.txt
RUN pip3 install -r build/requirements.txt

# ARG UID
# RUN useradd -u ${UID} sphinx
# RUN chown -R sphinx .

# USER sphinx
