import tkinter as tk
from tkinter import ttk
from PIL import ImageTk,Image
import json
from tkinter.filedialog import asksaveasfile, askopenfile


def writeToJSONFile(path, fileName, data):
    json.dump(data, path)
 

#Create metaclass to make class iterable
class MetaClass(type):
    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__"):
                yield attr


# Context menu for the elements
class ElementMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.config(tearoff = False)
        self.add_command(label="Rotate", underline=1, command=lambda: parent.rotate())
        self.add_command(label="Remove", underline=1, command=lambda: parent.destroy())


# Context menu for the workspace       
class ContextMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.config(tearoff = False)

        add_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Add", menu=add_menu)
        add_menu.add_command(label="Resistor", command=lambda: parent.CreateElement("Resistor"))
        add_menu.add_command(label="Diode", command=lambda: parent.CreateElement("Diode"))


# Menu bar for the application
class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File",underline=0, menu=file_menu)
        file_menu.add_command(label="Save", command=lambda: parent.Save())
        file_menu.add_command(label="Load", command=lambda: parent.Load())
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


# Base element class
class Element(tk.Label, metaclass=MetaClass):
    def __init__(self, parent, posX, posY, rot = 0, img = ""):
        tk.Label.__init__(self, parent, bd=0, highlightthickness=0, relief='ridge')

        self.parent = parent
        self.x, self.y = posX, posY
        self.rotation = rot
        self.img = ImageTk.PhotoImage(Image.open(img).rotate(-90 * self.rotation, expand=True))

        
        self.config(image=self.img)
        self.place(x=self.x, y=self.y)
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
        self.x = widget.winfo_x() - widget.startX + event.x
        self.y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=self.x, y=self.y)


    def pop_up(self, event):
        self.elementmenu.post(event.x_root, event.y_root)

    def rotate(self):
        self.rotation += 1
        if self.rotation == 4:
            self.rotation = 0
        if isinstance(self, Diode):
            diode = Diode(self.parent, self.x, self.y, self.rotation)
        elif isinstance(self, Resistor):
            resistor = Resistor(self.parent, self.x, self.y, self.rotation)
        self.destroy()

    def Save(self):
        data = {}
        data['type'] = self.__class__.__name__
        data['posX'] = self.x
        data['posY'] = self.y
        data['rot'] = self.rotation

        return data
        
# Resistor element derived from element class
class Resistor(Element, metaclass=MetaClass):
    def __init__(self, parent, posX, posY, rot = 0):
        super().__init__(parent, posX, posY, rot, "./elements/resistor.png")

        
# Diode element derived from element class
class Diode(Element, metaclass=MetaClass):
    def __init__(self, parent, posX, posY, rot = 0):
        super().__init__(parent, posX, posY, rot, "./elements/diode.png")


# The workspace for the application
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

    def CreateElement(self, elementType, posX = None, posY = None, rot = 0):
        if posX is None and posY is None:
            posX = self.click_x
            posY = self.click_y
            print("default value")
        else:
            ##self.year_released = year_released
            print("has value")

        match elementType:
                case "Resistor":
                    resistor = Resistor(self, posX, posY, rot)
                case "Diode":
                    diode = Diode(self, posX, posY, rot)
                case _:
                    print("Invalid element")


    def Save(self):
        data = []
        # Iterating through all children of the Canvas which are not ContextMenu
        for child in filter(lambda w:not isinstance(w,ContextMenu), self.winfo_children()):
            data.append(child.Save())
        return data

    def Load(self, data):
        for child in filter(lambda w:not isinstance(w,ContextMenu), self.winfo_children()):
            child.destroy()
        for element in data:
            ##print(element["type"])
            self.CreateElement(element["type"], element["posX"], element["posY"], element["rot"])

# The main application
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
        self.workspace = WorkSpace(self)
        #self.main = Main(self)
        self.statusbar = StatusBar(self)

        #self.toolbar.pack(side="top", fill="x")
        #self.navbar.pack(side="left", fill="y")
        self.workspace.pack(side="top", fill="both", expand=True)
        #self.main.pack(side="top", fill="both", expand=True)
        self.statusbar.pack(side="bottom", fill="x")

    def Save(self):
        print("Application - saved")
        data = self.workspace.Save()
        print(data)
        files = [('JSON File', '*.json')]
        fileName='IOTEDU'
        filepos = asksaveasfile(initialdir = "/output/", filetypes = files,defaultextension = json,initialfile='IOTEDU')
        if filepos : # user selected a file
            writeToJSONFile(filepos, fileName, data)
        else: # user cancel the file browser window
            print("No file chosen")

    def Load(self):
        print("Load")
        file = askopenfile(title='Select input file', filetypes=[("JSON files", ".json")])
        if file: # user selected a file
            data = json.loads(file.read())
            print(data)
            self.workspace.Load(data)
        else: # user cancel the file browser window
            print("No file chosen") 


# Statusbar for the application
class StatusBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the Status bar")
        label.pack(padx=10, pady=10)

##
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

##
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
##
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
##
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
