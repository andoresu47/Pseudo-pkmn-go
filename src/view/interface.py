import Tkinter as tk
import tkFont as tkfont
import tkMessageBox as tm
from random import randint
import os
from PIL import ImageTk, Image
import src.controller.controller_functions as cf
from src.controller.controller_functions import UserNotRegisteredException


class Application(tk.Tk):
    """
    Class to handle the GUI of the application.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, StartPage, OptionsPage, CapturePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Pokemon-Go!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Login", width=5,
                            command=lambda: controller.show_frame("LoginPage"))
        button2 = tk.Button(self, text="Quit", fg='red', width=5,
                            command=self.quit)
        # button1.place(relx=.4, rely=.5, width=40, anchor="c")
        # button2.place(relx=.6, rely=.5, anchor="c")
        button1.pack()
        button2.pack()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label_1 = tk.Label(self, text="Username")
        self.label_2 = tk.Label(self, text="Password")

        self.entry_1 = tk.Entry(self)
        self.entry_2 = tk.Entry(self, show="*")

        self.label_1.grid(row=0, sticky=tk.E)
        self.label_2.grid(row=1, sticky=tk.E)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)

        self.logbtn = tk.Button(self, text="Login", command=self._login_btn_clickked)
        self.logbtn.grid(columnspan=2)

        self.pack()

    def _login_btn_clickked(self):
        username = self.entry_1.get()
        password = self.entry_2.get()

        try:
            verif = cf.login(username, password)
            if verif:
                self.controller.show_frame("OptionsPage")
                tm.showinfo("Login info", "Welcome {0}".format(username))
            else:
                tm.showerror("Login error", "Incorrect username or password")

        except UserNotRegisteredException as e:
            tm.showerror("Login error", "Unregistered user.")


class OptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Options", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Capture", width=8,
                           command=lambda: controller.show_frame("CapturePage"))
        button.pack()

        self.logout_button = tk.Button(self, text="Logout", width=8, command=self.logout)
        self.logout_button.pack()

        quit_button = tk.Button(self, text="Quit", fg='red', width=8, command=self.quit)
        quit_button.pack(pady=(0, 10))

    def logout(self):
        self.controller.show_frame("LoginPage")
        tm.showinfo("Logout info", "Logged out")


class CapturePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        three_up = os.path.abspath(os.path.join(__file__, "../../.."))
        images_path = os.path.join(three_up, "images")

        path = os.path.join(images_path, "qtn.png")

        self.message = tk.Label(self, text="A wild Pokemon appeared!")
        self.message.pack(side="top")

        # Question mark image to indicate a wild pokemon appeared
        self.image = ImageTk.PhotoImage(Image.open(path))
        self.panel = tk.Label(self, image=self.image)
        self.panel.pack(side="top", fill="both", expand="yes", pady=5)

        self.capture_button = tk.Button(self, text="Capture", width=8, command=self.capture_pokemon)
        self.capture_button.pack(side="left")

        self.return_button = tk.Button(self, text="Go back", width=8,
                                       command=lambda: controller.show_frame("OptionsPage"))
        self.return_button.pack(side="left")

        self.QUIT = tk.Button(self, text="Quit", fg='red', width=8, command=self.quit)
        self.QUIT.pack(side="left")

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


if __name__ == "__main__":
    app = Application()
    app.mainloop()
