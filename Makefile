PYTHON = uv run python
MAIN = -m src
ARGS =

.PHONY: unzip_maze install run debug clean lint lint-strict test package

unzip_maze:
	unzip -o mazegenerator-00001.zip -d lib

install:
	uv sync

run:
	$(PYTHON) $(MAIN) $(ARGS)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist release

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

test:
	uv run pytest

package:
	uv run pyinstaller --clean -y pac-man.spec
	rm -rf release && mkdir -p release/pac-man
	cp dist/pac-man config.json packaging/run.sh packaging/INSTRUCTIONS.txt release/pac-man/
	cd release && tar -czf pac-man-linux.tar.gz pac-man
