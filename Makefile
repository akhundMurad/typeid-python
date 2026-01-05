# ==============================================================================
# Project configuration
# ==============================================================================

PACKAGE      := typeid
TESTS        := tests
DIST_DIR     := dist
VENV_DIR     := .venv

UV           := uv run
PYTEST       := $(UV) pytest
RUFF         := $(UV) ruff
BLACK        := $(UV) black
MYPY         := $(UV) mypy

# ==============================================================================
# Phony targets
# ==============================================================================

.PHONY: help lint lint-fix test test-docs docs docs-build build-sdist clean

# ==============================================================================
# Help
# ==============================================================================

help:
	@echo "Available targets:"
	@echo ""
	@echo "  lint         Run all linters (ruff, black, mypy)"
	@echo "  lint-fix     Automatically fix linting issues"
	@echo "  test         Run test suite"
	@echo "  test-docs    Run documentation tests"
	@echo "  docs         Serve documentation locally"
	@echo "  docs-build   Build documentation"
	@echo "  build-sdist  Build source distribution"
	@echo "  clean        Remove build artifacts"
	@echo ""

# ==============================================================================
# Linting
# ==============================================================================

lint:
	$(RUFF) check $(PACKAGE)/ $(TESTS)/
	$(BLACK) --check --diff $(PACKAGE)/ $(TESTS)/
	$(MYPY) $(PACKAGE)/

lint-fix:
	$(RUFF) check --fix $(PACKAGE)/ $(TESTS)/
	$(BLACK) $(PACKAGE)/ $(TESTS)/

# ==============================================================================
# Testing
# ==============================================================================

test:
	$(PYTEST) -v $(TESTS)

test-docs:
	$(PYTEST) README.md docs/ --markdown-docs

# ==============================================================================
# Documentation
# ==============================================================================

docs:
	mkdocs serve

docs-build:
	mkdocs build

# ==============================================================================
# Build & cleanup
# ==============================================================================

build-sdist: clean
	@uv build --sdist -o $(DIST_DIR)
	@ls -la $(DIST_DIR)

clean:
	@rm -rf $(DIST_DIR) build *.egg-info $(VENV_DIR)
