PYTHON := $(shell (command -v python3 >/dev/null 2>&1 && echo python3) || \
                 (command -v python >/dev/null 2>&1 && echo python) || \
                 (echo ""))

ifeq ($(PYTHON),)
$(error No Python interpreter found (python3 or python))
endif

.PHONY: install run clean genreqs

install:
	mv .gitignore .gitignore.copy
	rm -rf .gitignore
	mv .gitignore.copy .gitignore
	python3 -m pip install -r requirements.txt --break-system-packages
	touch run
	touch clean
	touch dbcli
	echo 'python src/db/cli.py $$@' > dbcli
	echo make run > run.sh
	echo make clean > clean
	chmod +x ./dbcli ./run.sh ./clean
	mkdir logs -p
	python src/db/cli.py full-init

run:
	$(PYTHON) src/main.py

clean:
	rm -rf logs/*.log __pycache__

genreqs:
	pipreqs ./src --force
	mv ./src/requirements.txt ./requirements.txt

check:
	@echo "Running checks..."
	@python -m py_compile $$(find src -name '*.py') || { echo 'Syntax errors found.'; exit 1; }
	@test -f requirements.txt || { echo 'Missing requirements.txt'; exit 1; }
	@test -d src || { echo 'Missing src/ directory'; exit 1; }
	@echo "All checks passed!"

dist:
	rm -f TOME.tar.gz
	mkdir -p dist-temp
	find . -type f ! -name '*.pyc' ! -path './__pycache__/*' ! -path './.git/*' -exec cp --parents {} dist-temp/ \;
	tar -czf TOME.tar.gz -C dist-temp .
	rm -rf dist-temp

distcheck:
	@echo "Creating source distribution package..."
	make dist || { echo "Error: Failed to create the distribution package"; exit 1; }

	mkdir -p tmp-distcheck
	tar -xzf TOME.tar.gz -C tmp-distcheck

	cd tmp-distcheck/ && ./configure && make
	cd tmp-distcheck/ && make check

	rm -rf tmp-distcheck

	@echo "distcheck completed successfully!"

