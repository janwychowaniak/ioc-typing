.PHONY: test lint format typecheck build clean clean-all dev check

test:
	tox

check: format lint typecheck

lint:
	tox -e lint

format:
	tox -e format

typecheck:
	tox -e typecheck

build:
	tox -e build

clean:
	tox -e clean

clean-all:
	tox -e clean-all

dev:
	tox -e dev 