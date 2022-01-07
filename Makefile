init:
	pip install -r requirements.txt

test:
	PYTHONPATH=. pytest

.PHONY: init test
