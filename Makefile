.PHONY: run test

run:
	pipenv run python main.py

test:
	pipenv run pytest
