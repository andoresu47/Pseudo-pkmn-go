# Pseudo-pkmn-go
Final project for the Computer Networks course at Facultad de Ciencias, UNAM, Mexico City. 

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Postgres 9.5.10
* Python 2.7
* pip 9.0.1

### Installing

Navigate to the repository directory and execute the following commands. 

Install required python packages:

```
pip install -r requirements.txt
```

Load database schema:

```
sudo -u postgres psql postgres -f ./src/db_stuff/schema.sql
```

Upload test data to database:

```
python -m src.db_stuff.initialize_db
```

## Running

Again, from the repository's main directory, execute the following.

Run server:

```
python -m src.controller.server
```

Run client (application):
```
python -m src.view.interface
```

### Notes

* You can run as many instances of client as you like.
* Client file `<interface.py>` accepts `<ip_address, port>` command line arguments.

## Makefile

Additionally, you can run the above commands via the included makefile.

Initialize server example:

```
make install-server
```

## Authors

* **Santiago Ley Flores**
* **Andrés López Martínez**
* **Ulises Manuel Cárdenas**
