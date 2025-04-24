.PHONY: install run clean genreqs

install:
	mv .gitignore .gitignore.copy
	python -m venv .
	rm -rf .gitignore
	mv .gitignore.copy .gitignore
	pip install -r requirements.txt --break-system-packages
	echo 'python src/db/cli.py $$@' > dbcli
	echo make run > run
	echo make clean > clean
	chmod +x ./dbcli ./run ./clean
	mkdir logs -p

run:
	python src/main.py

clean:
	rm -rf logs/*.log __pycache__

genreqs:
	pipreqs ./src --force
	mv ./src/requirements.txt ./requirements.txt
