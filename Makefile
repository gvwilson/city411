all: commands

## commands: show available commands (*)
commands:
	@grep -h -E '^##' ${MAKEFILE_LIST} \
	| sed -e 's/## //g' \
	| column -t -s ':'


## build: build package
build:
	python -m build

## check: check code issues
check:
	ruff check .

## clean: clean up
clean:
	rm -rf ./dist
	find . -path './.venv' -prune -o -type f -name '.DS_Store' -exec rm {} +
	find . -path './.venv' -prune -o -type d -name '.cache' -exec rm {} +
	find . -path './.venv' -prune -o -type f -name '.coverage' -exec rm {} +
	find . -path './.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -path './.venv' -prune -o -type d -name '.ruff_cache' -exec rm -rf {} +
	find . -path './.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} +
	find . -path './.venv' -prune -o -type f -name '*~' -exec rm {

## fix: fix code issues
fix:
	@ruff check --fix .

## format: format code
format:
	@ruff format .

## publish: publish using ~/.pypirc credentials
publish:
	twine upload --verbose dist/*

## test: run tests
test:
	@pytest tests
