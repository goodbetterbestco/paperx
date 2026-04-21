VENV_PYTHON ?= ./.venv-paperx/bin/python
CORPUS ?= stepview
CORPUS_DIR := corpus/$(CORPUS)
MAX_WORKERS ?= 20

.PHONY: help install run-corpus reset-corpus corpus-status run-project test-unit test-integration test-e2e test-smoke

help:
	@printf '%s\n' \
		'make install' \
		'make run-corpus CORPUS=stepview MAX_WORKERS=20' \
		'make reset-corpus CORPUS=stepview' \
		'make corpus-status CORPUS=stepview' \
		'make run-project PROJECT_DIR=./tmp/fixed_validation_slice MAX_WORKERS=2' \
		'make test-unit' \
		'make test-integration' \
		'make test-e2e' \
		'make test-smoke'

install:
	python3 -m venv .venv-paperx
	$(VENV_PYTHON) -m pip install -r requirements.txt

run-corpus:
	PIPELINE_CORPUS_NAME=$(CORPUS) $(VENV_PYTHON) -m pipeline.cli.run_corpus_rounds --max-workers $(MAX_WORKERS)

reset-corpus:
	$(VENV_PYTHON) -m pipeline.cli.reset_corpus_to_source $(CORPUS_DIR)

corpus-status:
	@test -f $(CORPUS_DIR)/_runs/status.json && sed -n '1,240p' $(CORPUS_DIR)/_runs/status.json || echo 'No status file found at $(CORPUS_DIR)/_runs/status.json'

run-project:
	@test -n "$(PROJECT_DIR)" || (echo 'PROJECT_DIR is required'; exit 2)
	$(VENV_PYTHON) -m pipeline.cli.run_project $(PROJECT_DIR) --max-workers $(MAX_WORKERS)

test-unit:
	$(VENV_PYTHON) -m unittest discover -s tests/unit -t . -p '*_test.py'

test-integration:
	$(VENV_PYTHON) -m unittest discover -s tests/integration -t . -p '*_test.py'

test-e2e:
	$(VENV_PYTHON) -m unittest discover -s tests/e2e -t . -p '*_test.py'

test-smoke:
	PAPERX_RUN_SMOKE=1 $(VENV_PYTHON) -m unittest discover -s tests/smoke -t . -p '*_test.py'
