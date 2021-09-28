SHELL:=/bin/bash
# Set the project name to the path - making underscore the path separator.
# Remove the leading slash and use lowercase since docker-compose will.
project_name=$(shell PWD_var=$$(pwd); PWD_no_lead_slash=$${PWD_var:1}; echo $${PWD_no_lead_slash//\//_} | awk '{print tolower($$0)}' | cat)
docker_compose_dev = docker-compose --project-directory build/docker/dev -f build/docker/dev/docker-compose.yml -p $(project_name)_dev

export UID:=$(shell id -u)

## Common ##

dev-build-no-cache:
	$(docker_compose_dev) build --no-cache

dev-build:
	$(docker_compose_dev) build

# Start the notebooks environment
dev-up:
	$(docker_compose_dev) up -d --build

# Start without rebuilding the Docker image
# (use when dependencies have not changed for faster starts).
dev-up-no-build:
	$(docker_compose_dev) up -d

# Stop the notebooks environment
dev-down:
	$(docker_compose_dev) down --remove-orphans

dev-restart: dev-down dev-up

dev-restart-no-build: dev-down dev-up-no-build

# List the running containers.
dev-ps:
	$(docker_compose_dev) ps

# Start an interactive shell
dev-ssh:
	$(docker_compose_dev) exec sphinx bash

# Delete everything
dev-clear:
	$(docker_compose_dev) stop
	$(docker_compose_dev) rm -fs

dev-push:
	docker push ${DEV_OUT_IMG}

dev-pull:
	docker pull ${DEV_OUT_IMG}

## End Common ##

## CI ##
test-ci-local:
	gitlab-runner exec shell build-no-cache
## End CI ##
