
.PHONY: init test lint source clean

init:
	pip install -r requirements.txt

test:
	PYTHONPATH=. pytest -v

source:
	python3 setup.py sdist

lint:
	black .
	flake8 --ignore E203,E501

clean:
	python3 setup.py clean
	rm -rf build/ MANIFEST dist build dvdosc.egg-info deb_dist .pytest_cache
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete