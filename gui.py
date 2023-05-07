import tkinter as tk
from tkinter import ttk
from PIL import ImageTk,Image
import json
from tkinter.filedialog import asksaveasfile, askopenfile
import math
import random
import template_matching as tm


# Function for saving to file
def writeToJSONFile(path, fileName, data):
    json.dump(data, path)


# Context menu for the elements
class ElementMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.config(tearoff = False)
        self.add_command(label="Rotate", underline=1, command=lambda: parent.rotate())
        self.add_command(label="Connect", underline=1, command=lambda: parent.parent.connect(parent.x, parent.y, parent))
        self.add_command(label="Delete Connection", underline=1, command=lambda: parent.parent.deleteConnect(parent))
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
        file_menu.add_command(label="Load from file", command=lambda: parent.LoadFromFile())
        file_menu.add_command(label="Exit", underline=1, command=self.quit)

    def quit(self):
        app.destroy()


# Connections
class Connection():
    def __init__(self, parent, anchor1, anchor2):
        self.parent = parent
        self.anchor1, self.anchor2 = anchor1, anchor2

        self.lines = None
        self.update()

    def createConnection(self, anchors):
        lines = []
        x1, y1 = anchors[0]
        x2, y2 = anchors[1]
        if abs(x1 - x2) >= abs(y1 - y2):
            lines.append(self.parent.create_line(x1 - 1, y1 - 1, (x2 + x1) / 2 - 1, y1 - 1, width = 3))
            lines.append(self.parent.create_line((x2 + x1) / 2 - 1, y1 - 1, (x2 + x1) / 2 - 1, y2 - 1, width = 3))
            lines.append(self.parent.create_line((x2 + x1) / 2 - 1, y2 - 1, x2 - 1, y2 - 1, width = 3))
        else:
            lines.append(self.parent.create_line(x1 - 1, y1 - 1, x1 - 1, (y2 + y1) / 2 - 1, width = 3))
            lines.append(self.parent.create_line(x1 - 1, (y2 + y1) / 2 - 1, x2 - 1, (y2 + y1) / 2 - 1, width = 3))
            lines.append(self.parent.create_line(x2 - 1, (y2 + y1) / 2 - 1, x2 -1, y2 - 1, width = 3))
        return lines

    def update(self):
        if self.lines:
            for line in self.lines:
                self.parent.delete(line)
        anchors = self.checkAnchors(self.anchor1, self.anchor2)
        self.lines = self.createConnection(anchors)

    def delete(self):
        self.anchor1 = None
        self.anchor2 = None
        self.lines = None

    def checkAnchors(self, element1, element2):
        tmp = 999999
        anchorStart, anchorEnd = None, None
        for anchor1 in element1.anchorPoints:
            for anchor2 in element2.anchorPoints:
                if math.sqrt(math.pow(anchor2[0] - anchor1[0], 2) + math.pow(anchor2[1] - anchor1[1], 2)) < tmp:
                    tmp = math.sqrt(math.pow(anchor2[0] - anchor1[0], 2) + math.pow(anchor2[1] - anchor1[1], 2))
                    anchorStart = anchor1
                    anchorEnd = anchor2
        return anchorStart, anchorEnd

    def Save(self):
        data = {}
        data['type'] = self.__class__.__name__
        data['anchor1'] = self.anchor1.id
        data['anchor2'] = self.anchor2.id
        data['lines'] = self.lines

        return data


# Base element class
class Element(tk.Label):
    def __init__(self, parent, posX, posY, elementId = 0, rot = 0, img = ""):
        tk.Label.__init__(self, parent, bd=0, highlightthickness=0, relief='ridge')

        self.id = None
        if elementId == 0:
            self.id = random.randint(1,99999)
        else:
            self.id = elementId
        self.parent = parent
        self.x, self.y = posX, posY
        self.rotation = rot
        self.img = ImageTk.PhotoImage(Image.open(img).rotate(-90 * self.rotation, expand=True))
        self.anchorPoints = []
        
        self.config(image=self.img)
        self.place(x=self.x, y=self.y)
        self.elementmenu = ElementMenu(self)
        
        self.bind("<Button-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<ButtonRelease-1>", self.drag_end)
        self.bind("<Button-3>", self.pop_up)


    def drag_start(self, event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y
        widget.update()

    def drag_motion(self, event):
        widget = event.widget
        self.x = widget.winfo_x() - widget.startX + event.x
        self.y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=self.x, y=self.y)
        
    def drag_end(self, event):
        widget = event.widget
        widget.update()
        if widget.parent.connections:
            for connection in widget.parent.connections:
                connection.update()

    def pop_up(self, event):
        self.elementmenu.post(event.x_root, event.y_root)
        self.parent.click_x = event.x_root
        self.parent.click_y = event.y_root

    def rotate(self):
        element = None
        self.rotation += 1
        if self.rotation == 4:
            self.rotation = 0
        if isinstance(self, Diode):
            element = Diode(self.parent, self.x, self.y, self.id, self.rotation)
        elif isinstance(self, Resistor):
            element = Resistor(self.parent, self.x, self.y, self.id, self.rotation)
        if self.parent.connections:
            for connection in self.parent.connections:
                if connection.anchor1 == self:
                    connection.anchor1 = element
                if connection.anchor2 == self:
                    connection.anchor2 = element 
                connection.update()
        self.destroy()

    def Save(self):
        data = {}
        data['type'] = self.__class__.__name__
        data['posX'] = self.x
        data['posY'] = self.y
        data['id'] = self.id
        data['rot'] = self.rotation
        data['anchorPts'] = self.anchorPoints

        return data

        
# Resistor element derived from element class
class Resistor(Element):
    def __init__(self, parent, posX, posY, elementId = 0, rot = 0, img = ""):
        super().__init__(parent, posX, posY, elementId, rot, "./elements/resistor.png")
        self.update()

    def update(self):
        if self.rotation == 0 or self.rotation == 2:
            self.anchorPoints = [[self.x, (self.y + self.winfo_reqheight()/2)],[(self.x + self.winfo_reqwidth()), (self.y + self.winfo_reqheight()/2)]]
        elif self.rotation == 1 or self.rotation == 3:
            self.anchorPoints = [[(self.x + self.winfo_reqwidth()/2), self.y],[(self.x + self.winfo_reqwidth()/2), (self.y + self.winfo_reqheight())]]

        
# Diode element derived from element class
class Diode(Element):
    def __init__(self, parent, posX, posY, elementId = 0, rot = 0, img = ""):
        super().__init__(parent, posX, posY, elementId, rot, "./elements/diode.png")
        self.update()

    def update(self):
        if self.rotation == 0 or self.rotation == 2:
            self.anchorPoints = [[self.x, (self.y + self.winfo_reqheight()/2)],[(self.x + self.winfo_reqwidth()), (self.y + self.winfo_reqheight()/2)]]
        elif self.rotation == 1 or self.rotation == 3:
            self.anchorPoints = [[(self.x + self.winfo_reqwidth()/2), self.y],[(self.x + self.winfo_reqwidth()/2), (self.y + self.winfo_reqheight())]]


# The workspace for the application
class WorkSpace(tk.Canvas):
    def __init__(self, parent):
        tk.Canvas.__init__(self, parent)

        self.click_x, self.click_y = 0, 0
        self.connectStart = None
        self.connections = []
        
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

    def CreateElement(self, elementType, posX = None, posY = None,elementId = 0, rot = 0):
        if posX is None and posY is None:
            posX = self.click_x
            posY = self.click_y

        match elementType:
                case "Resistor":
                    resistor = Resistor(self, posX, posY, elementId, rot)
                case "Diode":
                    diode = Diode(self, posX, posY, elementId, rot)
                case _:
                    print("Invalid element")

    def connect(self, posX, posY, element):
        if self.connectStart == None:
            self.connectStart = element
        else:
            self.connections.append(Connection(self, self.connectStart, element))
            self.connectStart = None

    def deleteConnect(self, element):
        tmp = []
        for connection in self.connections:
            if connection.anchor1 == element:
                for line in connection.lines:
                    self.delete(line)
                connection.delete()
                tmp.append(connection)
            elif connection.anchor2 == element:
                for line in connection.lines:
                    self.delete(line)
                connection.delete()
                tmp.append(connection)
        for element in tmp:
            self.connections.remove(element)

    def Save(self):
        data = []
        # Iterating through all children of the Canvas which are not ContextMenu
        for child in filter(lambda w:not isinstance(w,ContextMenu), self.winfo_children()):
            data.append(child.Save())
        for connection in self.connections:
            data.append(connection.Save())
        return data

    def Load(self, data):
        for child in filter(lambda w:not isinstance(w,ContextMenu), self.winfo_children()):
            self.deleteConnect(child)
            child.destroy()
        self.connections.clear
        for element in data:
            if element["type"] != "Connection":
                self.CreateElement(element["type"], element["posX"], element["posY"],element["id"], element["rot"])
            else:
                self.connections.append(Connection(self, self.getElementById(element["anchor1"]), self.getElementById(element["anchor2"])))

    def getElementById(self, elementId):
        for child in filter(lambda w:not isinstance(w,ContextMenu), self.winfo_children()):
            if child.id == elementId:
                return child
        return None

# The main application
class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # Adding a title to the window
        self.wm_title("Circuit diagram editor")

        # Setting default state of the window to fullscreen
        self.wm_state('zoomed')

        # Adding menu to the window
        menubar = MenuBar(self)
        self.config(menu=menubar)

        self.workspace = WorkSpace(self)
        self.statusbar = StatusBar(self)

        self.workspace.pack(side="top", fill="both", expand=True)
        self.statusbar.pack(side="bottom", fill="x")

    def Save(self):
        data = self.workspace.Save()
        files = [('JSON File', '*.json')]
        fileName='circuit'
        filepos = asksaveasfile(initialdir = "/output/", filetypes = files,defaultextension = json,initialfile='circuit')
        if filepos : # user selected a file
            writeToJSONFile(filepos, fileName, data)
        else: # user cancel the file browser window
            print("No file chosen")

    def Load(self):
        file = askopenfile(title='Select input file', filetypes=[("JSON files", ".json")])
        if file: # user selected a file
            data = json.loads(file.read())
            self.workspace.Load(data)
        else: # user cancel the file browser window
            print("No file chosen") 

    def LoadFromFile(self):
        file = askopenfile(title='Select input file', filetypes=[("PNG files", ".png")])
        if file: # user selected a file
            path = file.name.split("/")
            data = tm.main(path[len(path)-1])
            self.workspace.Load(data)
        else: # user cancel the file browser window
            print("No file chosen")     

# Statusbar for the application
class StatusBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self)
        label.pack(padx=10, pady=10)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
