.PHONY: clean version

clean:
	rm -rf *.egg-info build dist .pytest_cache __pycache__ .coverage

version:
	@echo "Current version: $(shell poetry version -s)"
