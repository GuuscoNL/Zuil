from tkinter import *
from tkinter import messagebox
from datetime import datetime
from functools import partial
import random
import psycopg2.extras
import pyowm

# ---------- Global Vars ----------
connection_string = "host='localhost' dbname='zuil' user='postgres' password='Guus2005!'"
conn = psycopg2.connect(connection_string)
STATIONS = ["Hilversum", "Utrecht", "Almere"]
schermIsOpen = False

# ---------- Fonts ----------
font_title = ("Courier", 15)
font_bericht = ("Courier", 10)


# ---------- Functions ----------

def Reiziger(entry_naam, entry_bericht, label_info):
    # --- Krijg de input ---
    naam = entry_naam.get() 
    bericht = entry_bericht.get("1.0",'end-1c')
    if naam == "": naam = "Anoniem"

    if len(bericht) >= 140: # check of het niet meer dan 140 chars zijn
        label_info["text"] = "Uw bericht mag maximaal 140 characters zijn"
        return
    elif len(bericht) == 0:
        label_info["text"] = "U kunt geen lege bericht sturen"
        return
    
    datumtijd = datetime.now()
    
    station = random.choice(STATIONS)
    
    # --- Zet het in de database ---
    cursor = conn.cursor() 
    query = """ INSERT INTO bericht(bericht, datumtijd, naamreiziger, station)
                VALUES
                    (%s, %s, %s, %s);
            """ 
    data = (bericht, datumtijd, naam, station)
    cursor.execute(query, data)
    conn.commit() 
    reiziger_change_to_reiziger_einde() # Ga naar de volgende page

def krijg_alle_berichten():
    # Haal alle berichten uit de database
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """ SELECT 	R.id,
                        R.naamreiziger,
                        R.station,
                        R.datumtijd,
                        R.bericht,
                        L.goedgekeurd
                FROM beoordeling AS L
	                RIGHT JOIN bericht AS R ON L.berichtid = R.id
                ORDER BY datumtijd DESC;"""
    cursor.execute(query)
    return cursor.fetchall()

def maak_bericht_compact(text, max_char, start_woord=""):
    # Zet een "\n" na n chars, zodat meer dan één lijn wordt gebruikt
    woorden = text.split(" ")
    woorden.insert(0, start_woord)
    sublines = [""]
    index = 0
    
    for woord in woorden:
        if len(sublines[index]) + len(woord) >= max_char:
            index += 1
            sublines.append(woord + " ")
        else:
            sublines[index] += woord + " "
    
    bericht_text = ""
    
    for subline in sublines:
        bericht_text += subline + "\n"
    
    return bericht_text[:-1]

def krijg_faciliteiten(station):
    # Haal alle beschikbare faciliteiten op uit de database
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """ SELECT * FROM station_service WHERE station_city = %s;"""
    data = (station,)
    cursor.execute(query, data)
    return cursor.fetchall()

def mod_login(entry_naam, entry_email, label_info):
    naam = entry_naam.get()
    
    email = entry_email.get()
    
    # Kijk of de moderator bestaat
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """ SELECT id FROM moderator
                WHERE naam = %s AND email = %s"""
    data = (naam, email)
    cursor.execute(query, data)
    mod = None
    for record in cursor.fetchall():
        mod = record

    if mod is None:
        label_info["text"] = "Mod account bestaat niet, probeer opnieuw"
    else:
        global cur_mod # Maak global zodat het later makkelijk kan worden gebruikt
        cur_mod = mod
        modInlog_change_to_mod() # Ga naar volgende pagina
        
def listbox_berichten_selected(label_naam, label_station, label_datum, label_bericht, label_goedkeuring, frame_keuringButtons, event):
    # Wanneer de gebruiker een bericht selecteer update frame_bericht met de juiste gegevens
    for index in listbox_berichten.curselection(): # check wat is geselecteerd
        bericht = berichten_lijst[index]
        label_naam["text"] = f"Naam: {bericht['naamreiziger']}"
        label_station["text"] = f"Station: {bericht['station']}"
        label_datum["text"] = f"Datum: {bericht['datumtijd'].strftime('%Y-%m-%d %H:%M:%S')}"
        label_bericht["text"] = maak_bericht_compact(bericht['bericht'], 35, "Bericht:")
        
        if bericht['goedgekeurd']:
            goedkeuring = "Goedgekeurd"
            frame_keuringButtons.forget()
        elif bericht['goedgekeurd'] == False:
            goedkeuring = "Niet goedgekeurd"
            frame_keuringButtons.forget()
        else:
            goedkeuring = "Nog niet beoordeeld"
            frame_keuringButtons.pack(pady=5,anchor="w",
                       side="left")
        
        label_goedkeuring["text"] = f"Beoordeling: {goedkeuring}"

def keur_bericht(keuring, label_goedkeuring):
    for index in listbox_berichten.curselection():# check wat is geselecteerd
        bericht = berichten_lijst[index]
        # --- Zet de keuring in de database ---
        cursor = conn.cursor()
        query = """ INSERT INTO beoordeling(goedgekeurd, datumtijd, berichtid, moderatorid)
                        VALUES
                            (%s, %s, %s, %s);"""
        data = (keuring, datetime.now(), bericht['id'], cur_mod['id'])
        cursor.execute(query, data)
        conn.commit()
        
        # --- Laat zien dat het is gekeurd ---
        if keuring:
            goedkeuring = "Goedgekeurd"
        else:
            goedkeuring = "Niet goedgekeurd"
        label_goedkeuring["text"] = f"Beoordeling: {goedkeuring}"
        frame_keuringButtons.forget()
        
        update_berichten()
        
def update_berichten():
    # update de berichten in de listbox_berichten
    listbox_berichten.delete(0, "end") # Leeg de listbox
    berichten = krijg_alle_berichten()
    global berichten_lijst
    berichten_lijst = []
    for i in range(len(berichten)):
        bericht = berichten[i]
        listbox_berichten.insert(i, f"Bericht van: {bericht['naamreiziger']}")
        
        if bericht['goedgekeurd'] == True: # Als het goedgekeurd is highlight het groen, anders rood
            listbox_berichten.itemconfig(i, background="#63ff63")
        elif bericht['goedgekeurd'] == False:
            listbox_berichten.itemconfig(i, background= "#ff7a7a")
        
        # Zet het bericht in deze lijst, zodat het alter gebruikt kan worden door andere functions
        berichten_lijst.append(bericht) 


# ---------- GUI ----------

def menu_change_to_reiziger():
    page_reiziger.pack(fill="both", expand=1)
    
    page_menu.forget()
    root.title("Reiziger")

def menu_change_to_stations():
    page_stations.pack(fill="both", expand=1)
    
    page_menu.forget()
    root.title("Stations")

def reiziger_change_to_menu(entry_name, entry_bericht):
    page_menu.pack(fill="both", expand=1)
    
    # Delete alles wat in de entries staat
    entry_name.delete(0, "end")
    entry_bericht.delete(1.0, "end")
    
    page_reiziger.forget()
    root.title("Menu")

def reiziger_change_to_reiziger_einde():
    page_reiziger_einde.pack(fill="both", expand=1)
    
    page_reiziger.forget()
    
def stations_change_to_menu():
    page_menu.pack(fill="both", expand=1)
    
    page_stations.forget()
    root.title("Menu")

def top_exit(top): 
    # Wanneer de Zuilscherm word gesloten zet schermIsOpen op false, 
    # zodat er nog een scherm kan worden geopend
    global schermIsOpen
    schermIsOpen = False
    top.destroy()
    
def menu_change_to_modInlog():
    page_modInlog.pack(fill="both", expand=1)
    
    page_menu.forget()
    root.title("Moderator login")

def modInlog_change_to_menu():
    page_menu.pack(fill="both", expand=1)
    
     # Delete alles wat in de entries staat
    entry_mod_naam.delete(0, "end")
    entry_mod_email.delete(0, "end")
    
    page_modInlog.forget()
    root.title("Menu")
    
def modInlog_change_to_mod():
    page_mod.pack(fill="both", expand=1)
    
    page_modInlog.forget()
    root.title("Moderator")
    
def mod_change_to_menu():
    page_menu.pack(fill="both", expand=1)
    
    # Delete alles wat in de entries staat
    entry_mod_naam.delete(0, "end")
    entry_mod_email.delete(0, "end")
    
    page_mod.forget()
    root.title("Menu")

# Initialise app
winWidth = 400
winHeight = 300

root = Tk()
root.title("Menu")
root.geometry(f"{winWidth}x{winHeight}")
root.resizable(False, False)
root.iconbitmap("Zuil/images/NS-logo.ico")


def load_menu():
    # Menu om uit de drie opties te kiezen: Reiziger, Moderator of het Stationsscherm
    
    global page_menu 
    page_menu = Frame(root,
                    width=winWidth/2,
                    height=winHeight/2)
    page_menu.pack(fill="both", expand=1)
        
    label_title = Label(master=page_menu, 
                text="Welke modus?")
    label_title.pack(pady=10)

    button_reiziger = Button(master=page_menu, 
                            text="Reiziger",
                            cursor="hand2",
                            command=menu_change_to_reiziger)
    button_reiziger.pack(pady=5)

    button_moderator = Button(master=page_menu, 
                            text="Moderator",
                            cursor="hand2",
                            command=menu_change_to_modInlog)
    button_moderator.pack(pady=5)

    button_scherm = Button(master=page_menu, 
                        text="Stations scherm",
                        cursor="hand2",
                        command=menu_change_to_stations)
    button_scherm.pack(pady=5)

def load_reiziger():
    # Op deze pagina kan de gebruiker een bericht maken die dan in de database wordt gezet.
    
    global page_reiziger 
    page_reiziger = Frame(root)
    page_reiziger.pack(fill="both", expand=1)

    label_title = Label(master=page_reiziger, 
                        text="Welkom!\nU kunt hier een bericht maken dat op het stationsscherm word laten zien",)
    label_title.pack(pady=5)

    frame_naam = Frame(page_reiziger)
    frame_naam.pack(anchor="n", side="top")

    label_naam = Label(frame_naam, text="Naam: ")
    label_naam.pack(side="left")

    entry_naam = Entry(frame_naam)
    entry_naam.pack(pady=5, side="left")

    frame_bericht = Frame(page_reiziger)
    frame_bericht.pack(anchor="n", side="top")

    label_bericht = Label(frame_bericht, text="bericht: ")
    label_bericht.pack(side="left")
    
    label_info = Label(page_reiziger, text="Laat naam leeg om anoniem te blijven")

    entry_bericht = Text(frame_bericht, width=30, height=5)
    entry_bericht.pack(pady=5, side="left")
    button_submit = Button(page_reiziger, 
                        text="Versturen",
                        cursor="hand2",
                        command=partial(Reiziger, entry_naam, entry_bericht, label_info))
    button_submit.pack(pady=5)

    label_info.pack()

    sub_frame_backbutton = Frame(page_reiziger)
    sub_frame_backbutton.pack(anchor="s", side="left")

    button_back = Button(master=sub_frame_backbutton, 
                        text="back",
                        cursor="hand2",
                        command=partial(reiziger_change_to_menu, entry_naam, entry_bericht))
    button_back.pack(anchor="s", side="left")
    
    page_reiziger.forget()

def load_reiziger_einde():
    # Deze pagina krijgt de gebruiker te zien wanneer het bericht is verstuurd
    
    global page_reiziger_einde
    page_reiziger_einde = Frame(root)
    page_reiziger_einde.pack(fill="both", expand=1)

    label_title = Label(master=page_reiziger_einde, 
                text="Bedankt voor het inzenden, nog een fijne dag!")
    label_title.pack(pady=5)
    
    page_reiziger_einde.forget()
    
def load_stations():
    # Op deze pagina kan de gebruiker kiezen van welk station de stationsscherm is.
    
    global page_stations
    page_stations = Frame(root)
    page_stations.pack(fill="both", expand=1)

    label_title = Label(master=page_stations,
                text="Welk station?")
    label_title.pack(pady=5)
    
    button_hilversum = Button(master=page_stations, 
                            text="Hilversum",
                            cursor="hand2",
                            command=partial(open_stationsscherm, "Hilversum"))
    button_hilversum.pack(pady=5)

    button_utrecht = Button(master=page_stations, 
                            text="Utrecht",
                            cursor="hand2",
                            command=partial(open_stationsscherm, "Utrecht"))
    button_utrecht.pack(pady=5)

    button_almere = Button(master=page_stations, 
                        text="Almere",
                        cursor="hand2",
                            command=partial(open_stationsscherm, "Almere"))
    button_almere.pack(pady=5)
    
    sub_frame_backbutton = Frame(page_stations)
    sub_frame_backbutton.pack(anchor="s", side="left")

    button_back = Button(master=sub_frame_backbutton, 
                        text="back",
                        cursor="hand2",
                        command=stations_change_to_menu)
    button_back.pack(anchor="s", side="left")
    
    page_stations.forget()

def open_stationsscherm(station):
    # Het stationsscherm dat in het station staat
    
    global schermIsOpen
    if schermIsOpen: 
        messagebox.showinfo("Error", "Er is al een stationsscherm open")
        return
    
    global top
    top = Toplevel(bg="#ffcc17")
    top.geometry("500x400")
    top.iconbitmap("Zuil/images/NS-logo.ico")
    top.resizable(False, False)
    
    label_title = Label(master=top, 
                        text=f"Welkom bij station {station}", 
                        bg="#ffcc17", 
                        font=font_title)
    label_title.pack(pady=10)
    
    # ---------- Berichten ----------
    
    frame_bericht = Frame(master=top, bg="#ffcc17")
    frame_bericht.pack(fill="both", expand=1)

    berichten = krijg_alle_berichten()
    
    index = 0
    for bericht in berichten:
        if index >= 5: break # Laat alleen de eerste 5 berichten zien
        if bericht["goedgekeurd"] == False or bericht["goedgekeurd"] is None: continue # Laat alleen berichten zien die zijn goedgekeurd
        if bericht["station"] != station: continue # Laat alleen berichten zien die bij dit station horen
        bericht_text = bericht["bericht"]
        
        bericht_text = maak_bericht_compact(bericht_text, 35)
        
        sub_frame_bericht = LabelFrame(master=frame_bericht, 
                                       bg="#ffcc17", 
                                       text=f"{bericht['naamreiziger']} zei: ")
        sub_frame_bericht.pack(pady=3)
        
        label_bericht = Label(master=sub_frame_bericht, 
                            text=bericht_text, 
                            font=font_bericht, 
                            bg="#ffcc17")
        label_bericht.pack()
        index += 1
    
    # ---------- Iconen ----------
    faciliteiten = krijg_faciliteiten(station)
    
    frame_iconen = Frame(master=top, bg="#ffcc17")
    frame_iconen.pack(anchor="s", side="left", padx=2, pady=3)
    
    if faciliteiten[0]["ov_bike"]:
        icon = PhotoImage(file="Zuil\images\img_ovfiets.png")
        icon = icon.subsample(2)
        label_title = Label(master=frame_iconen, image=icon)
        label_title.photo = icon
        label_title.pack(side="left", padx=2)
        
    if faciliteiten[0]["elevator"]:
        icon = PhotoImage(file="Zuil\images\img_lift.png")
        icon = icon.subsample(2)
        label_title = Label(master=frame_iconen, image=icon)
        label_title.photo = icon
        label_title.pack(side="left", padx=2)
        
    if faciliteiten[0]["toilet"]:
        icon = PhotoImage(file="Zuil\images\img_toilet.png")
        icon = icon.subsample(2)
        label_title = Label(master=frame_iconen, image=icon)
        label_title.photo = icon
        label_title.pack(side="left", padx=2)
        
    if faciliteiten[0]["park_and_ride"]:
        icon = PhotoImage(file="Zuil\images\img_pr.png")
        icon = icon.subsample(2)
        label_title = Label(master=frame_iconen, image=icon)
        label_title.photo = icon
        label_title.pack(side="left", padx=2)

    # ---------- Weer ----------
    
    owm = pyowm.OWM("6c9174d05f353b6f3fba0d4c53cb4728")
    
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(station)
    w = observation.weather
    
    temp = w.temperature('celsius')
    
    frame_weer = LabelFrame(master=top, bg="#ffcc17", text="Weer")
    frame_weer.pack(anchor="s", side="right", padx=2, pady=2)
    
    text_weer = f"""Temp: {temp["temp"]:7} C
Gevoel: {temp["feels_like"]:5} C
Max: {temp["temp_max"]:8} C
Min: {temp["temp_min"]:9} C"""
    
    label_weer = Label(master=frame_weer, text=text_weer, bg="#ffcc17")
    label_weer.pack()
    
    
    top.protocol("WM_DELETE_WINDOW", partial(top_exit, top)) # Wanneer de window wordt gesloten voer top_exit() uit

    schermIsOpen = True

def load_modInlog():
    # Op deze pagina de gebruiker kan inloggen als een moderator
    
    global page_modInlog
    page_modInlog = Frame(root)
    page_modInlog.pack(fill="both", expand=1)

    label_title = Label(master=page_modInlog, 
                text="Log in met je naam en email",)
    label_title.pack(pady=5)

    sub_frame_naam = Frame(page_modInlog)
    sub_frame_naam.pack(anchor="n", side="top")

    label_naam = Label(sub_frame_naam, text="Naam: ")
    label_naam.pack(side="left")

    global entry_mod_naam # global, zodat het later makkelijk gebruikt kan worden
    entry_mod_naam = Entry(sub_frame_naam, width=15)
    entry_mod_naam.pack(pady=5, side="left")

    sub_frame_bericht = Frame(page_modInlog)
    sub_frame_bericht.pack(anchor="n", side="top")

    label_bericht = Label(sub_frame_bericht, text="email: ")
    label_bericht.pack(side="left")

    global entry_mod_email # global, zodat het later makkelijk gebruikt kan worden
    entry_mod_email = Entry(sub_frame_bericht, width=27)
    entry_mod_email.pack(pady=5, side="left")
    
    label_info = Label(page_modInlog, text="")
    
    button_logIn = Button(page_modInlog, 
                        text="Log in",
                        cursor="hand2",
                        command=partial(mod_login, entry_mod_naam, entry_mod_email, label_info))
    button_logIn.pack(pady=5)
    
    label_info.pack()
    
    sub_frame_backbutton = Frame(page_modInlog)
    sub_frame_backbutton.pack(anchor="s", side="left")

    button_back = Button(master=sub_frame_backbutton, 
                        text="back",
                        cursor="hand2",
                        command=modInlog_change_to_menu)
    button_back.pack(anchor="s", side="left")
    
    page_modInlog.forget()

def load_mod():
    # Hier kan de moderator alle berichten bekijken en beoordelen
    
    global page_mod
    page_mod = Frame(root)
    page_mod.pack(fill="both", expand=1)
    
    label_title = Label(master=page_mod, 
                  text="Berichten")
    label_title.pack()
    
    frame_listbox = Frame(master=page_mod)
    frame_listbox.pack(anchor="w", side="left")
    
    scrollbar = Scrollbar(frame_listbox, orient=VERTICAL)
    
    global listbox_berichten # global, zodat het later makkelijk gebruikt kan worden
    listbox_berichten = Listbox(master=frame_listbox, 
                                height = 10, 
                                width = 30,
                                yscrollcommand=scrollbar.set)

    listbox_berichten.pack(anchor="w", side="left")
    
    scrollbar.config(command=listbox_berichten.yview)
    scrollbar.pack(side="left", fill=Y)
    
    frame_bericht = LabelFrame(master=page_mod,
                               text="Bericht")
    frame_bericht.pack(anchor="w",
                       side="left")
    
    label_naam = Label(master=frame_bericht,
                       text="Naam:")
    label_naam.pack(anchor="w")
    
    label_station = Label(master=frame_bericht,
                          text="Station:")
    label_station.pack(anchor="w")
    
    label_datum = Label(master=frame_bericht,
                       text="Datum:")
    label_datum.pack(anchor="w")
    
    label_bericht = Label(master=frame_bericht,
                          text="Bericht:")
    label_bericht.pack(anchor="w")
    
    label_goedkeuring = Label(master=frame_bericht,
                          text="Goedkeuring: ")
    label_goedkeuring.pack(anchor="w")
    
    global frame_keuringButtons # global, zodat het later makkelijk gebruikt kan worden
    frame_keuringButtons = Frame(master=frame_bericht)
    frame_keuringButtons.pack(pady=5,anchor="w",
                       side="left")
    
    button_keurgoed = Button(master=frame_keuringButtons,
                             text="Keur goed",
                             command=partial(keur_bericht, True, label_goedkeuring))
    button_keurgoed.pack(padx=5,
                         anchor="w",
                         side="left")
    
    button_keurAf = Button(master=frame_keuringButtons,
                             text="Keur niet goed",
                             command=partial(keur_bericht, False, label_goedkeuring))
    button_keurAf.pack(padx=5,
                       anchor="w",
                       side="left")
    
    frame_keuringButtons.forget()
    
    listbox_berichten.bind("<<ListboxSelect>>", partial(listbox_berichten_selected, 
                                                        label_naam, label_station, 
                                                        label_datum, label_bericht, 
                                                        label_goedkeuring, 
                                                        frame_keuringButtons))
    
    update_berichten()
    
    sub_frame_backbutton = Frame(page_mod)
    sub_frame_backbutton.place(x=3, y=winHeight-27)

    button_back = Button(master=sub_frame_backbutton, 
                        text="back",
                        cursor="hand2",
                        command=mod_change_to_menu)
    button_back.pack(anchor="s", side="left")
    
    
    page_mod.forget()


# Laad alle frames
load_menu()
load_reiziger()
load_reiziger_einde()
load_stations()
load_modInlog()
load_mod()

    
root.mainloop()