.PHONY: format
format:
	autoflake --recursive --in-place --remove-all-unused-imports .
	isort .
	black .
	flake8

.PHONY: lint
lint:
	isort --check .
	black --check .
	flake8

.PHONY: publish
publish:
	@echo "Remember to update the Changelog's version and date in README.rst and stage the changes"
	@echo ""
	@read -p "Press Enter to continue...";
	@echo ""
	@echo "Afterwards, run the following commands:"
	@echo "poetry run bumpversion --allow-dirty minor"
	@echo "poetry build"
	@echo "poetry publish"
	@echo ""
	@read -p "Press Enter to continue...";
	@echo ""
	@echo "You probably want to update the repo now:"
	@echo "git push origin master"
	@echo "git push --tags"
