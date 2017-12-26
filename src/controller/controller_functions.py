import pandas as pd

from src.db_stuff.database_connection import DatabaseUpload, DatabaseException


def populate_pokemon():
    """
    Function to populate database with the 151 first-generation pokemon.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    images_path = "C:\\Users\\Andres\\Documents\\UNAM\\Ciencias de la Computacion\\7mo semestre\\Redes de " \
                  "computadoras\\Proyecto 2\\images\\"
    df = pd.read_csv("../images/name_pokedex.csv", sep=',', header=None, index_col=0)

    for row in df.itertuples():
        index, pokemon = row
        path = images_path + str(index) + ".png"
        db_connection.set_pokemon(pokemon.lower(), path)

    db_connection.disconnect()


def register_user(username, password):
    """
    Function to register users in database.

    Args:
        username (str): name of user.
        password (str): user password.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    try:
        db_connection.set_user(username, password)

    except DatabaseException as e:
        print "Could not register user."

    finally:
        db_connection.disconnect()


def capture(username, pokemon):
    """
    Function for a user to capture a pokemon.

    Args:
        username (str): name of user.
        pokemon (str): pokemon name.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    try:
        db_connection.capture_pokemon(username, pokemon.lower())

    except DatabaseException as e:
        print "Could not capture pokemon"

    finally:
        db_connection.disconnect()


def query_pokemon(username):
    """
    Function to query captured pokemon for a given user.

    Args:
        username (str): name of user.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    try:
        return db_connection.get_captured(username)

    except DatabaseException as e:
        print "Could not capture pokemon"

    finally:
        db_connection.disconnect()


def get_image(pokemon):
    """
    Function to get a pokemon's image file path.

    Args:
        pokemon: id or name of pokemon.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    try:
        if isinstance(pokemon, int):
            return db_connection.get_image_from_id(pokemon)
        else:
            return db_connection.get_image_from_name(pokemon)

    except DatabaseException as e:
        print "Could not get image."

    finally:
        db_connection.disconnect()


def get_pokemon_name(nidpokemon):
    """
        Function to get a pokemon's name given its id.

        Args:
            nidpokemon: id of pokemon.
        """

    db_connection = DatabaseUpload()
    db_connection.connect()

    try:
        return db_connection.get_pokemon_from_id(nidpokemon).title()

    except DatabaseException as e:
        print "Could not get pokemon."

    finally:
        db_connection.disconnect()


if __name__ == '__main__':
    # populate_pokemon()
    # populate_users("redes2", "pass2")
    # capture("redes2", "bulbasaur")
    # print query_pokemon("redes2")
    # print get_image(1)
    print get_pokemon_name(1)
