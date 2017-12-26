import psycopg2
import logging


class DatabaseException(Exception):
    """Class for managing database exceptions.

    """

    pass


class DatabaseUpload:
    """Class for managing connections to "proyecto2redes" database, as well as data manipulation.

    """

    def __init__(self):
        """Constructor for initializing connection, cursor and logging config.

        Logs file location will be the same as this file.

        """

        self.conn = None
        self.cur = None

        hdlr = logging.FileHandler('Proyecto2.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)

        self.log = logging.getLogger('proyecto2_redes')
        self.log.addHandler(hdlr)
        self.log.addHandler(consoleHandler)
        self.log.setLevel(logging.INFO)

    def connect(self):
        """Method in charge of connecting to the database "market_data".

        Raises:
            DatabaseException: If something impedes to connect to the database.

        """

        try:
            self.conn = psycopg2.connect("dbname=proyecto2redes user=redes host=localhost password=redes1234")
            # print "Connected to database"
        except Exception as e:
            self.log.exception("Failed to connect")
            raise DatabaseException("Failed to connect\n" + str(e))

    def disconnect(self):
        """Method in charge of disconnecting from database.

        Raises:
            DatabaseException: If something impedes to disconnect from database.

        """

        try:
            self.conn.close()
            # print "Disconnected from database"
        except Exception as e:
            self.log.exception("Unable to disconnect from database")
            raise DatabaseException("Unable to disconnect from database\n" + str(e))

    def set_pokemon(self, pokemon_name, image_path):
        """Method in charge of inserting valid new rows into Pokemon table.

        Args:
            pokemon_name (str): name of pokemon.
            image_path (str): path to pokemon image.

        Raises:
            DatabaseException: If something impedes to insert new data, such as repeated entries.

        """

        self.cur = self.conn.cursor()
        try:
            self.log.info('Pokemon: Inserting pokemon: {0}'.format(pokemon_name))
            self.cur.execute("""INSERT INTO Pokemon
                                (nombre, imagen)
                                VALUES ('{name}', '{path}')"""
                             .format(name=pokemon_name,
                                     path=image_path
                                     )
                             )
            self.log.info('Pokemon: Committing transaction')
            self.conn.commit()
            self.cur.close()

        except Exception as e:
            self.conn.rollback()
            self.log.error('Pokemon: Rolling back transaction')
            self.log.exception("Pokemon: Couldn't insert successfully")
            raise DatabaseException()

    def set_user(self, user_name, password):
        """Method in charge of inserting valid new rows into Usuario table.

        Args:
            user_name (str): name of user.
            password (str): user password.

        Raises:
            DatabaseException: If something impedes to insert new data, such as repeated entries.

        """

        self.cur = self.conn.cursor()
        try:
            self.log.info('Usuario: Inserting user: {0}'.format(user_name))
            self.cur.execute("""INSERT INTO Usuario
                                (nombre, password)
                                VALUES ('{name}', '{passwd}')"""
                             .format(name=user_name,
                                     passwd=password
                                     )
                             )
            self.log.info('Usuario: Committing transaction')
            self.conn.commit()
            self.cur.close()

        except Exception as e:
            self.conn.rollback()
            self.log.error('Usuario: Rolling back transaction')
            self.log.exception("Usuario: Couldn't insert successfully")
            raise DatabaseException()

    def get_nIdUsuario(self, username):
        """Method for retrieving the id of a given username.

        Args:
            username (str): name of user.

        Returns:
            int: integer representing the desired ID.

        """

        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT nIdusuario
                            FROM Usuario
                            WHERE nombre = '{0}'""".format(username))
            res = self.cur.fetchone()
            self.cur.close()
            if res is not None:
                return int(res[0])
            else:
                raise DatabaseException("Username not found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve Username: " + str(e))

    def get_nIdPokemon(self, pokemon):
        """Method for retrieving the id of a given pokemon.

        Args:
            pokemon (str): pokemon name.

        Returns:
            int: integer representing the desired ID.

        """

        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT nIdpokemon
                            FROM Pokemon
                            WHERE nombre = '{0}'""".format(pokemon))
            res = self.cur.fetchone()
            self.cur.close()
            if res is not None:
                return int(res[0])
            else:
                raise DatabaseException("Pokemon not found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve Pokemon: " + str(e))

    def capture_pokemon(self, username, pokemon):
        """Method in charge of inserting valid new rows into Capture table.

        Args:
            username (str): name of user.
            pokemon (str): pokemon name.

        Raises:
            DatabaseException: If something impedes to insert new data, such as repeated entries.

        """

        self.cur = self.conn.cursor()
        try:
            self.log.info('Capture: capturing {0} by {1}'.format(pokemon, username))
            self.cur.execute("""INSERT INTO Captura
                                (nIdpokemon, nIdusuario)
                                VALUES ({pok}, {user})"""
                             .format(pok=self.get_nIdPokemon(pokemon),
                                     user=self.get_nIdUsuario(username)
                                     )
                             )
            self.log.info('Capture: Committing transaction')
            self.conn.commit()
            self.cur.close()

        except Exception as e:
            self.conn.rollback()
            self.log.error('Capture: Rolling back transaction')
            self.log.exception("Capture: Couldn't insert successfully")
            raise DatabaseException()

    def get_captured(self, username):
        """Method for getting captured pokemon for a given user.

        Args:
            username (str): name of user.

        Returns:
            list: list of captured pokemon id's.
        """

        niduser = self.get_nIdUsuario(username)
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT nIdpokemon
                                    FROM Captura
                                    WHERE nidusuario = '{0}'""".format(niduser))
            res = self.cur.fetchall()
            self.cur.close()
            if res is not None:
                return [x[0] for x in res]
            else:
                raise DatabaseException("No captured pokemon found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve Pokemon: " + str(e))

    def get_image_from_name(self, pokemon):
        """Method for getting a pokemon's image path.

        Args:
            pokemon (str): name of pokemon.

        Returns:
            str: path to pokemon's image file.
        """

        nidpokemon = self.get_nIdPokemon(pokemon)
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT imagen
                                FROM Pokemon
                                WHERE nidpokemon = '{0}'""".format(nidpokemon))
            res = self.cur.fetchone()
            self.cur.close()
            if res is not None:
                return int(res[0])
            else:
                raise DatabaseException("No image found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve image path: " + str(e))

    def get_image_from_id(self, nidpokemon):
        """Method for getting a pokemon's image path.

        Args:
            nidpokemon (int): id of pokemon.

        Returns:
            str: path to pokemon's image file.
        """

        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT imagen
                                FROM Pokemon
                                WHERE nidpokemon = '{0}'""".format(str(nidpokemon)))
            res = self.cur.fetchone()
            self.cur.close()
            if res is not None:
                return res[0]
            else:
                raise DatabaseException("No image found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve image path: " + str(e))

    def get_pokemon_from_id(self, nidpokemon):
        """Method for getting a pokemon's name.

        Args:
            nidpokemon (int): id of pokemon.

        Returns:
            str: pokemon's name.
        """

        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT nombre
                                FROM Pokemon
                                WHERE nidpokemon = '{0}'""".format(str(nidpokemon)))
            res = self.cur.fetchone()
            self.cur.close()
            if res is not None:
                return res[0]
            else:
                raise DatabaseException("No pokemon found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve pokemon's name: " + str(e))

    def get_password(self, username):
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("""SELECT password
                                FROM Usuario
                                WHERE nombre = '{0}'""".format(username))
            res = self.cur.fetchone()
            self.cur.close()
            if res is not None:
                return res[0]
            else:
                raise DatabaseException("User not found.")

        except Exception as e:
            self.conn.rollback()
            print("Couldn't retrieve password: " + str(e))
