.PHONY: clean version

clean:
	rm -rf *.egg-info build dist .pytest_cache .mypy_cache .ruff_cache __pycache__ .coverage coverage.xml

version:
	@echo "Current version: $(shell poetry version -s)"

ship:
	#To ship a bump you would manually tag, e.g:
	#git tag v1.0.1
	#git push origin v1.0.1

sync:
	git fetch origin
	git merge origin/master   # still on dev
	git push origin dev

