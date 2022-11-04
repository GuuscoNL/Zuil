from tkinter import *
from datetime import datetime
from functools import partial
import random
import psycopg2.extras

# ---------- Functions ----------
connection_string = "host='localhost' dbname='zuil' user='postgres' password='Guus2005!'"
conn = psycopg2.connect(connection_string)
STATIONS = ["Hilversum", "Bussum-Zuid", "Naarden-Bussum"]


def Reiziger(entry_naam, entry_bericht, label_info):
    naam = entry_naam.get()
    bericht = entry_bericht.get("1.0",'end-1c')
    if naam == "": naam = "Anoniem"

    if len(bericht) >= 140:
        label_info["text"] = "Uw bericht mag maximaal 140 characters zijn"
        return
    elif len(bericht) == 0:
        label_info["text"] = "U kunt geen lege bericht sturen"
        return
    
    datumtijd = datetime.now()
    
    station = random.choice(STATIONS)
    
    cursor = conn.cursor()
    query = """ INSERT INTO bericht(bericht, datumtijd, naamreiziger, station)
                VALUES
                    (%s, %s, %s, %s);
            """ 
    data = (bericht, datumtijd, naam, station)
    cursor.execute(query, data)
    conn.commit()
    reiziger_change_to_reiziger_einde()


def Moderator():
    naam = input("Naam: ")
    
    email = input("Email: ")
    
    # Kijk of de moderator al bestaat
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """ SELECT id FROM moderator
                WHERE naam = %s AND email = %s"""
    data = (naam, email)
    cursor.execute(query, data)
    mod = None
    for record in cursor.fetchall():
        mod = record
    
    if mod is None:
        print("Mod account bestaat niet probeer opnieuw")
        Moderator()
    
    # Haal het bericht op bericht
    query = """ SELECT 	R.id,
                        R.naamreiziger,
                        R.station,
                        R.datumtijd,
                        R.bericht
                FROM beoordeling AS L
	                RIGHT JOIN bericht AS R ON L.berichtid = R.id
                WHERE
                    L.id IS NULL;"""
    
    cursor.execute(query)
    berichten = cursor.fetchall()

    if berichten == []:
        print("Er zijn geen berichten die beoordeeld moet worden")
        return

    for i in range(len(berichten)):
        bericht = berichten[i]
        print(f"Bericht nummer {i}:")
        print(f"    Naam: {bericht['naamreiziger']}")
        print(f"    Station: {bericht['station']}")
        print(f"    Datum: {bericht['datumtijd'].strftime('%Y-%m-%d')}")
        print(f"    Tijd: {bericht['datumtijd'].strftime('%H:%M:%S')}")
        print(f"    Bericht: {bericht['bericht']}\n")

    keuze = int(input("Welk bericht wilt u beoordelen?\nNummer: "))

    bericht = berichten[keuze]
    print(f"    Naam: {bericht['naamreiziger']}")
    print(f"    Station: {bericht['station']}")
    print(f"    Datum: {bericht['datumtijd'].strftime('%Y-%m-%d')}")
    print(f"    Tijd: {bericht['datumtijd'].strftime('%H:%M:%S')}")
    print(f"    Bericht: {bericht['bericht']}\n")
    
    goedkeuring = input("Keurt u dit bericht goed? (y/n) ")
    goedgekeurd = None
    if goedkeuring == "y":
        goedgekeurd = True
        print("\nBericht is goedgekeurd!")
    elif goedkeuring == "n":
        goedgekeurd = False
        print("\nBericht is niet goedgekeurd!")

    cursor = conn.cursor()
    query = """ INSERT INTO beoordeling(goedgekeurd, datumtijd, berichtid, moderatorid)
                    VALUES
                        (%s, %s, %s, %s);"""
    data = (goedgekeurd, datetime.now(), bericht['id'], mod['id'])
    cursor.execute(query, data)
    conn.commit()





# ---------- GUI ----------

def menu_change_to_reiziger():
    frame_reiziger.pack(fill="both", expand=1)
    frame_menu.forget()
    root.title("Reiziger")

def reiziger_change_to_menu():
    frame_menu.pack(fill="both", expand=1)
    
    frame_reiziger.forget()
    root.title("Menu")

def reiziger_change_to_reiziger_einde():
    frame_reiziger_einde.pack(fill="both", expand=1)
    
    frame_reiziger.forget()

# Initialise app
winWidth = 400
winHeight = 300

root = Tk()
root.title("Menu")
#root.eval("tk::PlaceWindow . center")
root.geometry(f"{winWidth}x{winHeight}")
root.resizable(False, False)

# Menu Frame
def load_menu():
    global frame_menu 
    frame_menu = Frame(root,
                    width=winWidth/2,
                    height=winHeight/2)
    frame_menu.pack(fill="both", expand=1)
        
    label = Label(master=frame_menu, 
                text="Welke modus?")
    label.pack(pady=10)

    button_reiziger = Button(master=frame_menu, 
                            text="Reiziger",
                            cursor="hand2",
                            command=menu_change_to_reiziger)
    button_reiziger.pack(pady=5)

    button_moderator = Button(master=frame_menu, 
                            text="Moderator",
                            cursor="hand2")
    button_moderator.pack(pady=5)

    button_scherm = Button(master=frame_menu, 
                        text="Stations scherm",
                        cursor="hand2")
    button_scherm.pack(pady=5)

def load_reiziger():
    global frame_reiziger 
    frame_reiziger = Frame(root)
    frame_reiziger.pack(fill="both", expand=1)

    label = Label(master=frame_reiziger, 
                text="Welkom!\nU kunt hier een bericht maken dat op het stationsscherm word laten zien",)
    label.pack(pady=5)

    sub_frame_naam = Frame(frame_reiziger)
    sub_frame_naam.pack(anchor="n", side="top")

    label_naam = Label(sub_frame_naam, text="Naam: ")
    label_naam.pack(side="left")

    entry_naam = Entry(sub_frame_naam)
    entry_naam.pack(pady=5, side="left")

    sub_frame_bericht = Frame(frame_reiziger)
    sub_frame_bericht.pack(anchor="n", side="top")

    label_bericht = Label(sub_frame_bericht, text="bericht: ")
    label_bericht.pack(side="left")
    
    label_info = Label(frame_reiziger, text="Laat naam leeg om anoniem te blijven")

    entry_bericht = Text(sub_frame_bericht, width=30, height=5)
    entry_bericht.pack(pady=5, side="left")
    button_submit = Button(frame_reiziger, 
                        text="Versturen",
                        cursor="hand2",
                        command=partial(Reiziger, entry_naam, entry_bericht, label_info))
    button_submit.pack(pady=5)

    
    label_info.pack()

    sub_frame_backbutton = Frame(frame_reiziger)
    sub_frame_backbutton.pack(anchor="s", side="left")

    button_back = Button(master=sub_frame_backbutton, 
                        text="back",
                        cursor="hand2",
                        command=reiziger_change_to_menu)
    button_back.pack(anchor="s", side="left")
    
    frame_reiziger.forget()

def load_reiziger_einde():
    global frame_reiziger_einde
    frame_reiziger_einde = Frame(root)
    frame_reiziger_einde.pack(fill="both", expand=1)

    label = Label(master=frame_reiziger_einde, 
                text="Bedankt voor het inzenden, nog een fijne dag!")
    label.pack(pady=5)
    
    frame_reiziger_einde.forget()


# Laad alle frames
load_menu()
load_reiziger()
load_reiziger_einde()

    
root.mainloop()