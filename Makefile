SHELL := /bin/bash
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: install-poetry install-requirements ## Install project

install-poetry:
	@pip install --upgrade pip setuptools wheel
	@pip install poetry
	@poetry run pip install --upgrade pip setuptools wheel

install-requirements: ## Install project requirements
	@poetry install

clean:
	@rm -rf $$(dirname $$(dirname $$(poetry run which python)))

reinstall: clean install ## Reset project

update: ## Update dependencies
	@poetry update

backup: ## Run backup
	@poetry run backup_notion --output-dir='exports'

build: ## Build package
	@poetry build

publish: ## Publish package
	@poetry publish --build

format: ## Format
	@black .
