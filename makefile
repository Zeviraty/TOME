.PHONY: install run clean my_target

install:
	mv .gitignore .gitignore.copy
	python -m venv .
	rm -rf .gitignore
	mv .gitignore.copy .gitignore
	pip install -r requirements.txt --break-system-packages
	echo 'python src/db.py dbcli $$@' > dbcli
	echo make run > run
	echo make clean > clean
	chmod +x ./dbcli ./run ./clean
	mkdir logs -p

run:
	./dbcli backup
	python src/main.py

clean:
	rm -rf logs/*.log __pycache__
