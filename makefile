.PHONY: install run clean

install:
	python -m venv .
	pip install -r requirements.txt --break-system-packages
	echo python src/db.py \$@ > dbcli
	echo python src/main.py > run
	echo rm -rf logs/*.log __pycache__ > clean
	chmod +x ./dbcli ./run ./clean
