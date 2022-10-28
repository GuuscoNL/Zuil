from datetime import datetime
import random
import psycopg2.extras

connection_string = "host='localhost' dbname='zuil' user='postgres' password='Guus2005!'"
conn = psycopg2.connect(connection_string)
STATIONS = ["Hilversum", "Bussum-Zuid", "Naarden-Bussum"]

def main():
    mode = eval(input("Station Zeil programma\n\nModes:\n1. Klant\n2. Moderator\nKeuze: "))
    if mode == 1:
        Reiziger()
    elif mode == 2:
        Moderator()

def Reiziger(naam = ""):
    
    if naam == "":
        naam = input("Naam (Leeg betekent anoniem): ")
        if naam == "": naam = "Anoniem"
    
    bericht = input("Het bericht (Max 140 karakters): \n")
    if len(bericht) >= 140:
        print(f"Bericht is the lang: {len(bericht)} karakters lang, maar het mag maar 140 karakters lang zijn")
        Reiziger(naam)
    
    datumtijd = datetime.now()
    
    station = random.choice(STATIONS)

    commit = input("Wilt u het bericht versturen? (y/n)\n")
    
    if commit == "y":
        cursor = conn.cursor()
        query = """ INSERT INTO bericht(bericht, datumtijd, naamreiziger, station)
                    VALUES
                        (%s, %s, %s, %s);
                """ 
        data = (bericht, datumtijd, naam, station)
        cursor.execute(query, data)
        conn.commit()


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
    print()
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
    
main()