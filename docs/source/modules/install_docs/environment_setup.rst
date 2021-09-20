Environment Setup Guide
=======================

This document is a guide for setting up an environment to run the ODC - notably by installing Make, Docker, and Docker Compose.

Installation
---------------

Operating System
^^^^^^^^^^^^^^^^

First, you will need to ensure you are in an Ubuntu 18.04 or 20.04 environment (20.04 recommended).

We encourage Windows 10 users to use [Windows Subsystem for Linux Version 2 (WSL2)](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

Make, Docker, Docker Compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now install Make in your Ubuntu environment:
`apt-get update && apt-get install make -y`

For Windows users, install [Docker for Windows (Docker Desktop)](https://docs.docker.com/docker-for-windows/).

For Ubuntu users (**not WSL Ubuntu**), ensure you are a sudoer (user that can run `sudo`). Run the `sudo-ubuntu-install-docker` target in the `Makefile` in the top-level directory of a repository (e.g. [data_cube_notebooks](https://github.com/ceos-seo/data_cube_notebooks)) to install Docker:

```bash
make sudo-ubuntu-install-docker
```

After running the above command, logout and login again.

If that `Makefile` target is not available or it does not install Docker properly (e.g. the test listed below fails or the repository's environment will not start in Docker), run these commands as a block and then logout and login again.

```bash
apt-get update && \
apt install -y docker.io curl && \
curl -L "https://github.com/docker/compose/releases/download/1.27.4 docker-compose-Linux-x86_64" -o /usr/local/bin/docker-compose && \
chmod +x /usr/local/bin/docker-compose && \
systemctl start docker && \
systemctl enable docker && \
# The following steps are for enabling use 
# of the `docker` command for the current user
# without using `sudo`
getent group docker || sudo groupadd docker && \
usermod -aG docker ${USER}
```

Testing
-------

Once Docker is installed, test it with 
the following command: `docker run hello-world`

You should see output beginning with `Hello from Docker!`.