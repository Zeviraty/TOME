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

check:
	@echo "Running checks..."
	python -m py_compile $(find src -name '*.py') || { echo 'Syntax errors found.'; exit 1; }
	test -f requirements.txt || { echo 'Missing requirements.txt'; exit 1; }
	test -d src || { echo 'Missing src/ directory'; exit 1; }
	@echo "All checks passed!"

dist:
	tar -czf TOME.tar.gz --exclude=.git --exclude=*.pyc --exclude=__pycache__ .

distcheck:
	@echo "Creating source distribution package..."
	# Create a tarball (source package)
	make dist

	# Extract the distribution into a temporary directory
	mkdir -p tmp-distcheck
	tar -xzf your_project_name.tar.gz -C tmp-distcheck

	# Change into the directory and run ./configure (or similar setup)
	cd tmp-distcheck/your_project_name && ./configure && make

	# Optionally, run tests here (if you have any)
	cd tmp-distcheck/your_project_name && make check

	# Clean up the temporary directory
	rm -rf tmp-distcheck

	@echo "distcheck completed successfully!"
