from tkinter import *
from PIL import ImageTk,Image 

##logic
def create_label(element_type, posX, posY):
    match element_type:
        case "resistor":
            img = ImageTk.PhotoImage(Image.open("./elements/resistor.png"))
        case _:
            return "undefined element"
    
    element = Label(canvas, image=img, bd=0, highlightthickness=0, relief='ridge')
    element.image = img
    element.place(x=posX, y=posY)
    element.bind("<Button-1>", drag_start)
    element.bind("<B1-Motion>", drag_motion)

def create_canvas(w, h):
    canvas.master = window
    canvas.config(bg="gray", width=w, height=h, bd=0, highlightthickness=0, relief='ridge')
    canvas.place(x=10, y=30)

    canvas.bind("<Button-3>", pop_up)
    
def drag_start(event):
    widget = event.widget
    widget.startX = event.x
    widget.startY = event.y

def drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget.startX + event.x
    y = widget.winfo_y() - widget.startY + event.y
    widget.place(x=x, y=y)

def pop_up(event):
    context_menu.tk_popup(event.x_root, event.y_root)

##Initialization
# creating window
window = Tk()

# setting attribute
window.state('zoomed')
window.title("Drag-drop GUI")

##events/everything before mainloop
# creating menu bar
main_menu = Menu(window)
window.config(menu=main_menu)

file_menu= Menu(main_menu, tearoff=False)
main_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New...")
file_menu.add_separator()
file_menu.add_command(label="Exit",command=window.quit)

edit_menu = Menu(main_menu, tearoff=False)
main_menu.add_cascade(label="Edit",menu=edit_menu)
edit_menu.add_command(label="Cut")
edit_menu.add_command(label="Copy")
 
option_menu = Menu(main_menu, tearoff=False)
main_menu.add_cascade(label="Edit",menu=option_menu)
option_menu.add_command(label="Find")
option_menu.add_command(label="Find Next")

# creating the canvas to display the elements on
canvas = Canvas(window)
create_canvas(1000, 500)
canvas.pack()

# creating context menu
context_menu = Menu(canvas, tearoff=False)

element_menu = Menu(context_menu, tearoff=False)
context_menu.add_cascade(label="Add", menu=element_menu)
element_menu.add_command(label="Resistor", command=lambda: create_label("resistor", (window.winfo_pointerx() - canvas.winfo_rootx() - context_menu.winfo_width() - 100), (window.winfo_pointery() - canvas.winfo_rooty() - context_menu.winfo_height())))

# creating text labels to display on window screen
create_label("resistor", 0, 0)
create_label("resistor", 100, 100)

window.mainloop()

