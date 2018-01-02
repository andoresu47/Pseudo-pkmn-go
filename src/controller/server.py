import select
import sys
import socket
import Queue
import threading
import random
import os
from sets import Set
import src.controller.controller_functions as cf


# NOTAS
# MODIFICAR LO QUE DIGA 'FALTA'
# MODIFICAR CONSTANTES EN CLASE 'Server' SI ES NECESARIO
# LAS IMAGENES DEBEN ESTAR EN LA MISMA CARPETA QUE ESTE ARCHIVO

class Client_Handler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def setup(self, _conn, _address, _server):
        self.conn = _conn
        self.address = _address
        self.server = _server

        # estado
        self.estado = Server.ESTADOS["C0"]

        # Pokemon data
        self.pokid = 0
        self.captureRate = 0
        self.intentos = 0

        # Login data
        self.user = ""
        self.password = ""

    def select_pokemon(self, response):
        """
        Returns the pokemon id
        """

        # FALTA OBTENER LOS SIGUIENTES DATOS DE LA DB
        self.pokid = random.randint(1, 151)
        self.captureRate = 0.5
        self.intentos = 4
        # ES TODO
        return self.pokid

    def image_data(self):
        """
        Returns [imgSize][image]
        4 bytes for the image size and k for the image
        """

        fname = cf.get_image(self.pokid)
        pok_name = cf.get_pokemon_name(self.pokid)
        cf.capture(self.user, pok_name)

        # EJEMPLO DE OBTENER DE UN ARCHIVO
        img_size = 0
        img_data = ""

        with open(fname, 'rb') as fp:
            img_data = fp.read()

        img_size = len(img_data)

        # CONVERTIR NUMERO A 4 BYTES
        encoded_size = ""
        mask = 0xFF
        for i in range(3, -1, -1):
            bits = ((mask << (8 * i)) & img_size) >> (8 * i)
            encoded_size += chr(bits)

        print 'MANDAR IMAGEN DE %d BYTES' % img_size
        print 'SIZE IN HEX %s' % encoded_size.encode('hex')

        return encoded_size + img_data

    def login(self, _user, _password):
        """
        Function that manages the login given the user and password
        """

        self.user = _user
        self.password = _password

        exito = cf.login(self.user, self.password)

        return exito

    def query_pokedex(self):
        """
        Returns a string, the first byte is the number of captured pokemons
        Then follows as much bytes as pokemons the user has.
        """

        pokedex = cf.query_pokemon(self.user)
        num_pokemon = len(pokedex)

        response = "" + chr(num_pokemon)
        for pok in pokedex:
            response += chr(pok)
        return response

    def process_data(self, data):
        str_data = str(data)
        byts = list(str_data)
        codigo = ord(byts[0])
        print 'Codigo = %d' % codigo

        # por omision regresa error
        response = "" + chr(40)
        seguir = True

        if self.estado == Server.ESTADOS["C0"] and codigo == 11:
            # EL CLIENTE QUIERE INICIAR SESION
            self.estado = Server.ESTADOS["S1"]
            # Segundo byte es cuanto ocupa el nombre
            name_size = ord(byts[1])
            # CREDENCIALES
            user = str_data[2:name_size + 2]
            password = str_data[name_size + 2:]

            print "name_size = '%d'" % name_size
            print "Try to login with user '%s' and pass '%s'" % (user, password)

            if Client_Handler.login(self, user, password):
                # transicion
                # EXITO
                response = "" + chr(1)
                seguir = True
                self.estado = Server.ESTADOS["C2"]
            else:
                # transicion
                # RECHAZO
                response = "" + chr(0)
                seguir = True
                self.estado = Server.ESTADOS["E9"]

        elif (self.estado == Server.ESTADOS["C2"] or self.estado == Server.ESTADOS["C6"] or self.estado ==
            Server.ESTADOS["E7"] or self.estado == Server.ESTADOS["C9"] or self.estado == Server.ESTADOS[
            "C8"]) and codigo == 10:
            # EL CLIENTE PIDE UN POKEMON
            self.estado = Server.ESTADOS["S3"]

            # transicion
            response = "" + chr(20)
            response += chr(Client_Handler.select_pokemon(self, response))
            seguir = True
            self.estado = Server.ESTADOS["C4"]

        elif self.estado == Server.ESTADOS["C2"] and codigo == 12:
            # EL CLIENTE PIDE SU POKEDEX
            self.estado = Server.ESTADOS["S10"]

            # transicion
            response = "" + chr(24)
            response += Client_Handler.query_pokedex(self)
            seguir = True
            self.estado = Server.ESTADOS["C2"]

        elif codigo == 32 and (
                                self.estado == Server.ESTADOS["C2"] or self.estado == Server.ESTADOS[
                            "C8"] or self.estado ==
                        Server.ESTADOS["C9"] or self.estado == Server.ESTADOS["E7"]):
            # EL CLIENTE PIDE TERMINAR LA CONEXION
            print "Cerrando Conexion..."
            self.estado = Server.ESTADOS["E11"]
            response = ""
            seguir = False

        elif (self.estado == Server.ESTADOS["C4"] or self.estado == Server.ESTADOS["C6"]) and codigo == 31:
            # EL CLIENTE RECHAZA EL POKEMON
            self.estado = Server.ESTADOS["E7"]

            # transicion
            response = "" + chr(123)
            seguir = True
        # self.estado = Server.ESTADOS["E11"]

        elif (self.estado == Server.ESTADOS["C4"] or self.estado == Server.ESTADOS["C6"]) and codigo == 30:
            # EL CLIENTE INTENTA CAPTURAR EL POKEMON
            self.estado = Server.ESTADOS["S5"]

            p = random.uniform(0.0, 1.0)
            if p >= self.captureRate and self.intentos > 0:
                self.intentos -= 1

                # SE MANDA EL POKEMON

                # transicion
                response = "" + chr(22) + chr(self.pokid)
                response += Client_Handler.image_data(self)
                seguir = True
                self.estado = Server.ESTADOS["C8"]

            elif self.intentos > 1 and p < self.captureRate:
                self.intentos -= 1

                # SE DICE QUE NO SE ATRAPO

                # transicion
                response = "" + chr(21) + chr(self.pokid) + chr(self.intentos)
                seguir = True
                self.estado = Server.ESTADOS["C6"]

            else:
                self.intentos -= 1

                # SE DICE QUE SE AGOTARON EL NUMERO DE INTENTOS

                # transicion
                response = "" + chr(23)
                seguir = True
                self.estado = Server.ESTADOS["C9"]

        # ERROR
        if len(response) > 0 and response[0] == chr(40):
            self.estado = Server.ESTADOS["E11"]

        return (response, seguir)

    def run(self):
        inputs = [self.conn]
        outputs = []

        condicion = True
        s = self.conn

        try:
            while condicion:
                readable, writable, exceptional = select.select(inputs, [], [], Server.TIMEOUT)

                if s in readable:
                    # Receive data
                    data = s.recv(Server.BUFFER_SIZE)
                    # Do something with the data
                    if data:
                        print "Server received '%s' from '%s'" % (data.encode('hex'), s.getpeername())
                        # ACCIONES CON EL DATA
                        response, condicion = Client_Handler.process_data(self, data)

                        if condicion and response[0] != chr(123):
                            s.send(response)

                        if self.estado == Server.ESTADOS["E11"]:
                            condicion = False
                    else:
                        condicion = False
                else:
                    print "TIMEOUT"
                    condicion = False
        except socket.error, exc:
            print "Something happened: %s" % exc
        finally:
            self.server.sockets.remove(s)


class Server:
    TIMEOUT = 30
    QUEUE_SIZE = 50
    BUFFER_SIZE = 1024

    ESTADOS = {
        "C0": 0,
        "S1": 1,
        "C2": 2,
        "S3": 3,
        "C4": 4,
        "S5": 5,
        "C6": 6,
        "E7": 7,
        "C8": 8,
        "C9": 9,
        "S10": 10,
        "E11": 11
    }

    def __init__(self, HOST_IP, HOST_PORT=9999):
        """
		Constructor
		"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST_IP, HOST_PORT))

        self.inputs = [self.server_socket]
        self.outputs = []
        self.sockets = Set()

    def run(self):
        """
		Runs the server continuously to respond to client sockets
		"""
        self.server_socket.listen(Server.QUEUE_SIZE)

        try:
            while True:
                print self.sockets
                # Receive the sockets ready to receive and send data
                # With a Server.TIMEOUT timeout
                readable, writable, exceptional = select.select(self.inputs, [], [], Server.TIMEOUT)

                for socket in readable:
                    if socket == self.server_socket:
                        # When the server is ready to receive connections
                        conn, addr = socket.accept()

                        if conn not in self.sockets:
                            self.sockets.add(conn)
                            # Run a thread to process it
                            handler = Client_Handler()
                            handler.setup(conn, addr, self)
                            handler.start()
        finally:
            self.server_socket.close()
            os._exit(0)


if __name__ == "__main__":
    HOST = socket.gethostname()
    PORT = 9999
    server = Server(HOST, PORT)

    server.run()
