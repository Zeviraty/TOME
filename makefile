.PHONY: install run clean

install:
	python -m venv .
	pip install -r requirements.txt --break-system-packages

run:
	python src/main.py

clean:
	rm -rf logs/*.log __pycache__
