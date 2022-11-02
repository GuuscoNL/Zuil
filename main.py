from tkinter import *

def change_to_reiziger():
    frame_reiziger.pack(fill="both", expand=1)
    frame_menu.forget()
    root.title("Reiziger")
def change_to_menu():
    frame_menu.pack(fill="both", expand=1)
    frame_reiziger.forget()
    root.title("Menu")

# Initialise app
winWidth = 400
winHeight = 300

root = Tk()
root.title("Menu")
#root.eval("tk::PlaceWindow . center")
root.geometry(f"{winWidth}x{winHeight}")
root.resizable(False, False)

# Menu Frame
frame_menu = Frame(root,
                   width=winWidth/2,
                   height=winHeight/2)
frame_menu.pack(fill="both", expand=1)

#frame_menu.pack_propagate(False)
    
label = Label(master=frame_menu, 
            text="Welke modus?")
label.pack(pady=10)

button_reiziger = Button(master=frame_menu, 
                        text="Reiziger",
                        cursor="hand2",
                        command=change_to_reiziger)
button_reiziger.pack(pady=5)

button_moderator = Button(master=frame_menu, 
                        text="Moderator",
                        cursor="hand2")
button_moderator.pack(pady=5)

button_scherm = Button(master=frame_menu, 
                    text="Stations scherm",
                    cursor="hand2")
button_scherm.pack(pady=5)


frame_reiziger = Frame(root)
frame_reiziger.pack(fill="both", expand=1)

label = Label(master=frame_reiziger, 
            text="Reiziger")
label.pack()

button_back = Button(master=frame_reiziger, 
                    text="back",
                    cursor="hand2",
                    command=change_to_menu)
button_back.pack(anchor="sw")

frame_reiziger.forget()


root.mainloop()