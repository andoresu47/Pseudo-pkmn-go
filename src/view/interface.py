from Tkinter import *
from random import randint

from PIL import ImageTk, Image

import src.controller.controller_functions as cf


class Application(Frame):
    """
    Class to handle the GUI of the application.
    """

    def __init__(self, master=None):
        """
        Class constructor.
        """

        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def capture_pokemon(self):
        """
        Method to handle the behaviour of the capture pokemon button upon clicking.
        """

        rand_pokemon = randint(1, 151)
        path = cf.get_image(rand_pokemon)
        pok_name = cf.get_pokemon_name(rand_pokemon)

        img = ImageTk.PhotoImage(Image.open(path))

        self.message.config(text="{0} captured!".format(pok_name))
        self.panel.config(image=img)
        self.panel.image = img

    def createWidgets(self):
        """
        Method to instantiate and initialize every component in the application view.
        """

        path = "C:\\Users\\Andres\\Documents\\UNAM\\Ciencias de la Computacion\\7mo semestre\\Redes de " \
               "computadoras\\Proyecto 2\\images\\qtn.png"

        # Message to display
        self.message = Label(text="A wild Pokemon appeared!")
        self.message.pack()

        # Question mark image to indicate a wild pokemon appeared
        self.image = ImageTk.PhotoImage(Image.open(path))
        self.panel = Label(image=self.image)
        self.panel.pack(side="bottom", fill="both", expand="yes")

        # Quit button
        self.QUIT = Button(self)
        self.QUIT["text"] = "Quit"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "left"})

        # Capture pokemon button
        self.capture_button = Button(self)
        self.capture_button["text"] = "Capture",
        self.capture_button["command"] = self.capture_pokemon
        self.capture_button.pack({"side": "left"})

root = Tk()
root.title("Pokemon Go!")
app = Application(master=root)
app.mainloop()
root.destroy()
