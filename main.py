from datetime import datetime
import random
import csv
import psycopg2

connection_string = "host='localhost' dbname='zuil' user='postgres' password='Guus2005!'"
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
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        query = """ INSERT INTO bericht(bericht, datumtijd, naamreiziger, station)
                    VALUES
                        (%s, %s, %s, %s);
                """ 
        data = (bericht, datumtijd, naam, station)
        cursor.execute(query, data)
        conn.commit()
        conn.close()

def Moderator():
    naam = input("Naam: ")
    
    email = input("Email: ")
    
    berichten = []
    with open("Zuil\\berichten.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            berichten.append(row)
    
    for i in range(len(berichten)):
        bericht = berichten[i]
        print(f"Bericht nummer {i}:")
        print(f"    Naam: {bericht[0]}")
        print(f"    Locatie: {bericht[4]}")
        print(f"    Datum: {bericht[2]}")
        print(f"    Tijd: {bericht[3]}")
        print(f"    Bericht: {bericht[1]}\n")

    keuze = int(input("Welk bericht wilt u beoordelen?\nNummer: "))

    bericht = berichten[keuze]
    print(f"\nBericht nummer {keuze}:")
    print(f"    Naam: {bericht[0]}")
    print(f"    Locatie: {bericht[4]}")
    print(f"    Datum: {bericht[2]}")
    print(f"    Tijd: {bericht[3]}")
    print(f"    Bericht: {bericht[1]}\n")
    goedkeuring = input("Keurt u dit bericht goed? (y/n) ")
    
    if goedkeuring == "y":
        print("\nBericht is goedgekeurd!")
    elif goedkeuring == "n":
        print("\nBericht is niet goedgekeurd!")
    #TODO: Goedkeuring opslaan ergens
    #TODO: Bericht met goedkeuring in database zetten
    
main()