import tkinter as tk
from tkinter import ttk
from PIL import ImageTk,Image


class ElementMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.config(tearoff = False)

        element_menu = tk.Menu(self, tearoff=False)
        element_menu.add_command(label="Remove", underline=1, command=lambda: parent.destroy())

class ContextMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.config(tearoff = False)

        add_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Add", menu=add_menu)
        add_menu.add_command(label="Resistor", command=lambda: parent.CreateResistor())

        #file_menu = tk.Menu(self, tearoff=False)
        #self.add_cascade(label="File",underline=0, menu=file_menu)
        #file_menu.add_command(label="Exit", underline=1, command=self.quit)


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File",underline=0, menu=file_menu)
        file_menu.add_command(label="Exit", underline=1, command=self.quit)

        edit_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Edit",menu=edit_menu)
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")

        option_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Edit",menu=option_menu)
        option_menu.add_command(label="Find")
        option_menu.add_command(label="Find Next")


    def quit(self):
        app.destroy()


class Element(tk.Label):
    def __init__(self, parent, posX, posY, rot):
        tk.Label.__init__(self, parent, bd=0, highlightthickness=0, relief='ridge')

        self.rotation = rot

        self.place(x=posX, y=posY)

        self.elementmenu = ElementMenu(self)

        self.bind("<Button-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<Button-3>", self.pop_up)

    def drag_start(self, event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y

    def drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.startX + event.x
        y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=x, y=y)

    def pop_up(self, event):
        print("hello")
        self.elementmenu.post(event.x_root, event.y_root)
        

class Resistor(Element):
    def __init__(self, parent, posX, posY, rot = 1):
        super().__init__(parent, posX, posY, rot)

        self.img=Image.open("./elements/resistor.png")
        self.element_img = ImageTk.PhotoImage(self.img)
        self.config(image=self.element_img)

class WorkSpace(tk.Canvas):
    def __init__(self, parent):
        tk.Canvas.__init__(self, parent)

        self.click_x, self.click_y = 0, 0
        
        #Creating work area
        self.config(bg="gray", bd=0, highlightthickness=0, relief='ridge')
        self.place(x=10, y=30)

        #Creating context menu
        self.contextmenu = ContextMenu(self)

        self.bind("<Button-3>", self.pop_up)
        

    def pop_up(self, event):
        self.click_x = event.x
        self.click_y = event.y
        self.contextmenu.post(event.x_root, event.y_root)

    def CreateResistor(self):
        resistor = Resistor(self, self.click_x, self.click_y)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # Adding a title to the window
        self.wm_title("Test Application")

        # Setting default state of the window to fullscreen
        self.wm_state('zoomed')

        # Adding menu to the window
        menubar = MenuBar(self)
        self.config(menu=menubar)

        #self.toolbar = Toolbar(self)
        #self.navbar = Navbar(self)
        self.main = Main(self)
        self.statusbar = StatusBar(self)

        #self.toolbar.pack(side="top", fill="x")
        #self.navbar.pack(side="left", fill="y")
        self.main.pack(side="top", fill="both", expand=True)
        self.statusbar.pack(side="bottom", fill="x")


class StatusBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the Status bar")
        label.pack(padx=10, pady=10)


class Main(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # creating a frame and assigning it to container
        container = tk.Frame(self, height=400, width=600)
        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames themselves later but let's add the components to the dictionary.
        for F in (A, B, C):
            frame = F(container, self)

            # the Application class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.show_frame(A)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()


class A(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        workspace = WorkSpace(self)
        workspace.pack(side="right", fill="both", expand=True)

        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = tk.Button(
            self,
            text="Go to the Side Page",
            command=lambda: controller.show_frame(B),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

class B(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the main area B")
        label.pack(padx=10, pady=10)

        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = tk.Button(
            self,
            text="Go to the Side Page",
            command=lambda: controller.show_frame(C),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

class C(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the main area C")
        label.pack(padx=10, pady=10)

        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = tk.Button(
            self,
            text="Go to the Side Page",
            command=lambda: controller.show_frame(A),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)



if __name__ == "__main__":
    app = Application()
    app.mainloop()
