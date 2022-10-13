from datetime import datetime
import random
import csv

def main():
    mode = eval(input("Station Zeil programma\n\nModes:\n1. Klant\n2. Moderator\nKeuze: "))
    if mode == 1:
        Reiziger()
    elif mode == 2:
        Moderator()
        
def Reiziger(naam = ""):
    berichtInfo = {}
    
    if naam == "":
        naam = input("Naam (Leeg betekent anoniem): ")
        if naam == "": naam = "Anoniem"
    berichtInfo["naam"] = naam
    
    bericht = input("Het bericht (Max 140 karakters): \n")
    if len(bericht) >= 140:
        print(f"Bericht is the lang: {len(bericht)} karakters lang, maar het mag maar 140 karakters lang zijn")
        Reiziger(naam)
    berichtInfo["bericht"] = bericht
    
    tijd = datetime.now()
    berichtInfo["datum"] = tijd.strftime("%d-%m-%Y")
    berichtInfo["tijd"] = tijd.strftime("%X")
    
    with open("Zuil\stations.txt") as file:
        stations = file.readlines()
        station = random.choice(stations)
        berichtInfo["station"] = station.strip()

    commit = input("Will je het bericht versturen?\nAntwoord (y/n): ")
    if commit == "y":
        with open("Zuil\\berichten.csv", "a", newline='') as file:
            writer = csv.DictWriter(file, berichtInfo.keys())
            writer.writerow(berichtInfo)

def Moderator():
    print("Moderator")

main()