
def main():
    mode = eval(input("Station Zeil programma\n\nModes:\n1. Klant\n2. Moderator\nKeuze: "))
    if mode == 1:
        klant()
    elif mode == 2:
        Moderator()
        
def klant():
    print("Reizeger")
    
def Moderator():
    print("Moderator")

main()