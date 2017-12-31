import pandas as pd
import os
from passlib.hash import pbkdf2_sha256
from src.db_stuff.database_connection import DatabaseUpload, DatabaseException


class UserNotRegisteredException(Exception):
    """Class for managing database exceptions.

    """

    pass


def populate_pokemon():
    """
    Function to populate database with the 151 first-generation pokemon.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    three_up = os.path.abspath(os.path.join(__file__, "../../.."))
    images_path = os.path.join(three_up, "images")

    df = pd.read_csv("../images/name_pokedex.csv", sep=',', header=None, index_col=0)

    for row in df.itertuples():
        index, pokemon = row
        path = images_path + str(index) + ".png"
        db_connection.set_pokemon(pokemon.lower(), path)

    db_connection.disconnect()


def set_password(raw_password):
    """
    Function to encrypt a password.

    Args:
        raw_password: plain text password.

    Returns:
        str: encrypted password.
    """

    return pbkdf2_sha256.hash(raw_password)


def register_user(username, password):
    """
    Function to register users in database.

    Args:
        username (str): name of user.
        password (str): user password.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    encrypted = set_password(password)

    try:
        db_connection.set_user(username, encrypted)

    except DatabaseException as e:
        print "Could not register user."

    finally:
        db_connection.disconnect()


def check_password(raw_password, enc_password):
    """
    Function to test the matching of a plain text password with
    an encrypted one.

    Args:
        raw_password (str): plain text password.
        enc_password (str): encrypted password.

    Returns:
        bool: True if they match, False otherwise.
    """

    return pbkdf2_sha256.verify(raw_password, enc_password)


def login(username, password):
    """
    Function to verify a user's credentials.

    Args:
        username (str): name of user.
        password (str): plain text user password

    Returns:
        bool: True if login was successful, False otherwise.
    """

    db_connection = DatabaseUpload()
    db_connection.connect()

    try:
        encrypted = db_connection.get_password(username)
        if check_password(password, encrypted):
            return True
        else:
            return False

    except DatabaseException as e:
        print "Could not login."
        raise UserNotRegisteredException()

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

    Returns:
        list: list of captured pokemon id's.
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

    Returns:
        str: path to a pokemon's image file.
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

    Returns:
        str: pokemon name.
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
    # register_user("redes6", "pass6")
    # capture("redes2", "bulbasaur")
    # print query_pokemon("redes2")
    # print get_image(1)
    # print get_pokemon_name(1)
    print login("redes6", "pass6")
