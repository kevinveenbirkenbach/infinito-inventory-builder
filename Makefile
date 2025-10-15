# Makefile for Infinito Inventory Builder
# Usage:
#   make init    -> copies env.example to .env if missing
#   make up      -> starts the app via docker compose
#   make build   -> builds all images
#   make down    -> stops and removes containers
#   make ps/logs -> show container status or logs

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Load environment variables if .env exists
ifneq (,$(wildcard .env))
include .env
export
endif

help:
	@echo "Available targets:"
	@echo "  init   - create .env from env.example if missing"
	@echo "  up     - start the app (builds if needed)"
	@echo "  build  - build Docker images"
	@echo "  down   - stop and remove containers"
	@echo "  ps     - show running containers"
	@echo "  logs   - follow container logs"

init:
	@test -f .env || (cp env.example .env && echo "✅ Created .env from env.example")
	@test -f .env && echo "✔️  .env is ready"

up: init
	docker compose up --build

build: init
	docker compose build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f
