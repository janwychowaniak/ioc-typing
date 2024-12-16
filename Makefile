.PHONY: test lint format build clean clean-all dev check

test:
	tox

check: format lint

lint:
	tox -e lint

format:
	tox -e format

build:
	tox -e build

clean:
	tox -e clean

clean-all:
	tox -e clean-all

dev:
	tox -e dev 