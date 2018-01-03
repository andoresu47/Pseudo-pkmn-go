DIRS := src/controller src/db_stuff src/view src
OBJS := $(foreach dir,$(DIRS),$(wildcard $(dir)/*.py))
CAMBIO := $(foreach x,$(OBJS), $(subst .py, ,$(subst /,.,$(OBJS))))

run-server:
	python -m src.controller.server

run-client:
	python -m src.view.interface

install-requirements:
	pip install -r requirements.txt

install-server:
	sudo -u postgres psql postgres -f ./src/db_stuff/schema.sql
	python -m src.db_stuff.initialize_db

generate-doc:
	$(foreach x,$(CAMBIO), pydoc -w $(x);)
	mv *.html doc