run-server:
	python -m src.controller.server

run-client:
	python -m src.view.interface

install-requirements:
	pip install -r requirements.txt

install-server:
	sudo -u postgres psql postgres -f ./src/db_stuff/schema.sql
	python -m src.db_stuff.initialize_db
