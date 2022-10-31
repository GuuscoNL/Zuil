from tkinter import *

root = Tk()


label = Label(master=root, text="Welke modus?")
label.pack()

button_reiziger = Button(master=root, text="Reiziger")
button_reiziger.pack()

button_moderator = Button(master=root, text="Moderator")
button_moderator.pack()

button_scherm = Button(master=root, text="Stations scherm")
button_scherm.pack()




root.title("Zuil")
root.geometry("350x300")
root.mainloop()