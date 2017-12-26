# -*- coding: UTF-8 -*-
from time import sleep
import socket


class Cliente:

    def __init__(self, nombre, password, direccion, puerto=9999):
        self.nombre = nombre
        self.password = password
        self.direccion = direccion
        self.puerto = puerto
        # genera el socket de la conexión y lo conecta
        self.socket_connection = socket.socket()
        self.socket_connection.connect((direccion, puerto))

    # representa el edo C0 y su transición a S1
    def inicia_sesion_c0(self):
        """
        Inicia la sesión para identificarse con el servidor con su nombre y passwd
        [codigo][longNom][nombre][pass]
        :return 1 si la conexion fue aceptada, 0 si no
        """
        # genera el paquete a enviar
        paquete = bytearray()
        paquete.append(11)  # código
        paquete.append(len(self.nombre))  # longitud nombre
        # lo envía a través del socket
        self.socket_connection.send(paquete + self.nombre + self.password)
        # recibe la respuesta (un byte)
        b = bytearray()
        b.append(self.socket_connection.recv(1))
        return int(b[0])

    # representa el edo C2 y su transición a S10
    def pokedex_c2(self):
        """
        Se ejecuta cuando el usuario quiere ver su pokedex
        :return: la lista de ids de los pokemons que tiene
        """
        paquete = bytearray()
        paquete.append(12)
        self.socket_connection.send(paquete)
        # maneja los datos recibidos
        pokedex = []
        b = bytearray()
        b.append(self.socket_connection.recv(1))
        if int(b[0]) == 24:  # Si el codigo es correcto
            b.append(self.socket_connection.recv(1))
            for i in range(0, int(b[1])):
                c = bytearray()
                c.append(self.socket_connection.recv(1))
                pokedex.append(int(c[0]))
            return pokedex
        else:
            return "error, codgo incorrect"

    # representa el edo C2 y su transición a S3
    def solicita_poke_c2(self):
        """
        Implementa la trnasicion del estado s0 al s1
        Envia el código 10 para solicitar un pokemon.
        :return: El poke-ID [0,255] a atrapar
        """
        paquete = bytearray()
        paquete.append(10)
        self.socket_connection.send(paquete)  # envía el paquete
        # recibe la respuesta
        b = bytearray()
        b.append(self.socket_connection.recv(1))
        if int(b[0]) == 20:  # lee que el código sea el correcto
            # recibe el pokemon ID (un byte)
            b.append(self.socket_connection.recv(1))
            return int(b[1])
        else:
            return "error, codigo incorrecto"

    # representa el edo C4 y E7 y su transición a S5 o E11
    def capturar_poke_c4(self, decision):
        """
        Indica si quiere o no capturar el pokemon recibido, volver a pedir otro, o cerrar la sesión
        envía los códigos 30 para sí, 31 para no con 10 o 32 para intentar otro o cerrar la conexión respectivamente.
        :param decision: 0 si captura, 1 si no captura y termina la sesion, 2 si vuelve a intentar otro poke
        :return 21, 22 o 23 si se eligió 0 más el resto del respectivo paquete, id del nuevo poc si se escoge 2. -1 e.o.c.
        """
        bts = bytearray()
        if decision == 0:
            # Sí quiere capturar el poke
            bts.append(30)
            self.socket_connection.send(bts)  # Envía 30
            return self.manejo_resultados_captura()

        elif decision == 1:
            # No quiere capturar el poke y termina sesion
            bts.append(31)
            self.socket_connection.send(bts)  # Envía 31
            return self.fin_sesion()   # Envía 32

        elif decision == 2:
            # Reintenta con otro poke
            bts.append(31)
            self.socket_connection.send(bts)  # Envía 31
            return self.solicita_poke_c2()  # Envía 10

        else:
            return "Error, decisión entre [0,2]"

    # representa el edo C6 y E7 y su transición a S5, E11 o S3
    def reintentar_captura_c6(self, decision):
        """
        Se usa cuando el código recibido fue 21
        :param decision: si, no_Ycierre, no_Yreintento
        :return: resultado del intento, -1, nvo pokemon
        """
        bts = bytearray()
        if decision == "si":
            # manda un sí
            bts.append(30)
            self.socket_connection.send(bts)
            # recibe la respuesta
            return self.manejo_resultados_captura()
        elif decision == "no_Ycierre":
            # manda un no y cierra
            bts.append(31)
            self.socket_connection.send(bts)
            return self.fin_sesion()  # manda 32
        elif decision == "no_Yreintento":
            # manda un no y solicita otro
            bts.append(31)
            self.socket_connection.send(bts)
            return self.solicita_poke_c2()  # manda 10
        else:
            return "error, decisión incorrecta"

    # representa el edo C8 y su transición a S3 o E11
    def poke_recibido_c8(self, mas_pokes):
        """
        Se ejecuta cuando se recibió al pokemon y se quiere cerrar la sesion o capturar otro
        :param mas_pokes: True si se quiere capturar otro, false si no
        :return:
        """
        if mas_pokes:
            return self.solicita_poke_c2()  # manda 10
        else:
            return self.fin_sesion()  # manda 32

    # privado
    def manejo_resultados_captura(self):
        """
        Maneja los intentos de captura
        :return: si no es atrapó el id del pok y num de intentos restantes.
        si se atrapó, Id-poke y la imagen.
        "intentos_agotados" si se terminaron los intentos.
        """
        # recibe si se capturó o no el poke
        b = bytearray()
        b.append(self.socket_connection.recv(1))
        result = int(b[0])
        if result == 21:  # No se atrapó y quedan k intentos
            # regresa id del pok y num intentos restantes
            b.append(self.socket_connection.recv(1))
            b.append(self.socket_connection.recv(1))
            return 21, int(b[1]), int(b[2])
        elif result == 22:  # Se atrapó
            return 22, self.obten_imagen()
        elif result == 23:  # intentos agotados
            return 23, "intentos_agotados"

    # privado
    def obten_imagen(self):
        """
        Se ejecuta en el momento en que sea necesario obtener el paquete con la imagen
        :return: una lista con el ID (int) del poke y su imagen como una secuencia de bytes
        """
        # obtiene el poke-ID
        b = bytearray()
        b.append(self.socket_connection.recv(1))
        idpok = int(b[0])
        # obtiene el número de bytes a leer
        b = bytearray()
        b.append(self.socket_connection.recv(1))
        b.append(self.socket_connection.recv(1))
        b.append(self.socket_connection.recv(1))
        b.append(self.socket_connection.recv(1))
        tam = 0
        for i in range(0, 4, 1):
            tam += (b[i] << (8 * (3 - i)))

        img_bytes = self.socket_connection.recv(tam)

        return idpok, img_bytes, tam

    # privado
    def fin_sesion(self):
        """
        Se ejecuta a final para terminar toda la sesión y cerrar las conexiones
        :return:
        """
        end_code = bytearray()
        end_code.append(32)
        self.socket_connection.send(end_code)
        self.socket_connection.close()
        return -1

if __name__ == '__main__':
    # CONECTA AL SERVER
    cl = Cliente("MRJuanito", "Banana", socket.gethostname())
    # INCIA SESION y REVISA SI PUDO LOGGEARSE
    if cl.inicia_sesion_c0() == 0:
        print("error al iniciar sesión")
        exit(1)
    else:
        print("EXITO al iniciar sesion")

    #SOLICITA EL POKEDEX
    print ("MIS POKEmONS SON:\n")
    print (cl.pokedex_c2())

    #Solicita un poke para capturar y aceptamos:
    pokeID = cl.solicita_poke_c2()
    print("Capturaremos el poke "+ str(pokeID))
    res = cl.capturar_poke_c4(0)  # el 0 es para sí

    # print (res[0])
    if res[0] == 21:  # Si no se capturó
        print("Pokemon no atrapado\n Reintentando...")
        x = cl.reintentar_captura_c6("si")
        if x[0] == 21:  # si no se capturó
            print("Pokemon no atrapado\n Eligiendo otro...")
            # id nvo poke:
            idnvopok = cl.reintentar_captura_c6("no_Yreintento")
            print("Recibimos al nuevo pokemon " + str(idnvopok))
            cl.capturar_poke_c4(1) #No captura y cierra sesión
            print("No lo queremos capturar\n Finalizando sesion")
            
        else:  # si se capturó
            print("¡ POKEMON ATRAPADO!\n Terminamos la sesion")
            cl.poke_recibido_c8(False)
    elif res[0] == 22: #sí lo capturó
        # SE ARMA LA IMAGEN, ESTA EN RES[1] Y EL TAMAÑO EN RES[2]
        print("¡ POKEMON ATRAPADO!\n Finalizando la conexion")
        cl.poke_recibido_c8(False)


    elif res[0] == 23:  # se terminaron los reintentos
        print("Intentos agotados, ¡vamos por otro poke!")
        print("No queremos capturar al pokemon " + str(cl.solicita_poke_c2()))
        print(
            "Tampoco queremos capturar al poke " + str(cl.capturar_poke_c4(2)))  # 2 es para intentar otro poke
        print("Finalizamos sesión")

    exit(0)