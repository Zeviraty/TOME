PYTHON := $(shell (command -v python3 >/dev/null 2>&1 && echo python3) || \
                 (command -v python >/dev/null 2>&1 && echo python) || \
                 (echo ""))

NAME := tome
DOCKER ?= 0

ifeq ($(PYTHON),)
$(error No Python interpreter found (python3 or python))
endif

.PHONY: install run clean updatelibs check dist distcheck

install:
	$(MAKE) updatelibs
	@touch clean
	@touch dbcli
	@echo '$(PYTHON) src/tome/db/cli.py $$@' > dbcli
	@echo make run > run.sh
	@echo make clean > clean
	@chmod +x ./dbcli ./run.sh ./clean
	@mkdir logs -p
	@pip install -e . --break-system-packages
	@$(PYTHON) src/tome/db/cli.py full-init --force

run:
	$(PYTHON) src/tome

updatelibs:
	@$(PYTHON) -m pip install -r requirements.txt --break-system-packages
ifeq ($(DOCKER),0)
        curl -s https://raw.githubusercontent.com/zeviraty/zte/main/main.py -o tools/map-editor/zte.py
endif

clean:
	rm -rf logs/*.log

check:
	@echo "Running checks..."
	@test -d src || { echo 'Missing src/ directory'; exit 1; }
	@$(PYTHON) -m py_compile $$(find src -name '*.py') || { echo 'Syntax errors found.'; exit 1; }
	@./test || { echo 'Tests failed,'; exit 1; }
	@test -f requirements.txt || { echo 'Missing requirements.txt'; exit 1; }
	@echo "All checks passed!"

dist:
	rm -f TOME.tar.gz
	mkdir -p dist-temp
	find . -type f ! -name '*.pyc' ! -path './__pycache__/*' ! -path './.git/*' -exec cp --parents {} dist-temp/ \;
	tar -czf TOME.tar.gz -C dist-temp .
	rm -rf dist-temp

distcheck:
	@echo "Creating source distribution package..."
	@$(MAKE) dist || { echo "Error: Failed to create the distribution package"; exit 1; }

	@mkdir -p tmp-distcheck
	@tar -xzf TOME.tar.gz -C tmp-distcheck

	@cd tmp-distcheck/ && ./configure && make
	@cd tmp-distcheck/ && make check

	@rm -rf tmp-distcheck

	@echo "distcheck completed successfully!"
	@rm -rf TOME.tar.gz

mapjq:
	@$(foreach file, $(wildcard config/maps/*), cat $(file) | jq '.' > tmp.txt && mv tmp.txt $(file);)
