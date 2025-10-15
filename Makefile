# Makefile for Infinito Inventory Builder
# Usage:
#   make init       -> copies env.example to .env if missing
#   make install    -> init + pkgmgr install + link path from pkgmgr
#   make up         -> starts the app via docker compose
#   make build      -> builds all images
#   make down       -> stops and removes containers
#   make ps/logs    -> show container status or logs

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Load environment variables if .env exists
ifneq (,$(wildcard .env))
include .env
export
endif

help:
	@echo "Available targets:"
	@echo "  init       - create .env from env.example if missing"
	@echo "  pkgmgr-install - install 'infinito' via pkgmgr"
	@echo "  link-path  - set INFINITO_NEXUS_PATH from 'pkgmgr path infinito' in .env"
	@echo "  install    - init + pkgmgr-install + link-path"
	@echo "  up         - start the app (builds if needed)"
	@echo "  build      - build Docker images"
	@echo "  down       - stop and remove containers"
	@echo "  ps         - show running containers"
	@echo "  logs       - follow container logs"

init:
	@test -f .env || (cp env.example .env && echo "✅ Created .env from env.example")
	@test -f .env && echo "✔️  .env is ready"

link-path: init
	@command -v pkgmgr >/dev/null 2>&1 || { \
		echo "❌ 'pkgmgr' not found in PATH."; \
		exit 127; \
	}
	@path=$$(pkgmgr path infinito); \
	if [ -z "$$path" ]; then \
		echo "❌ Could not resolve path from 'pkgmgr path infinito'"; \
		exit 1; \
	fi; \
	if grep -q '^INFINITO_NEXUS_PATH=' .env; then \
		sed -i.bak 's|^INFINITO_NEXUS_PATH=.*|INFINITO_NEXUS_PATH='"$$path"'|' .env; \
	else \
		echo INFINITO_NEXUS_PATH="$$path" >> .env; \
	fi; \
	echo "✔️  INFINITO_NEXUS_PATH set to $$path"

install: init pkgmgr-install link-path

up: init build
	docker compose up

build: init
	docker compose build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f
