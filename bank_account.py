class Account:
    def __init__(self, name, account_number, balance=2000, plafond=1000):
        self.name = name
        self.account_number = account_number
        self.balance = balance
        self.plafond = plafond
    
    def withdraw(self, montant):
        if montant > self.balance :
            print(f"Solde insuffisant pour retirer {montant} €.")
        elif montant > self.plafond :
            print(f"Montant dépasse le plafond de {self.plafond} €.") 
        else : 
            self.balance -= montant
            print(f"Vous avez retirer {montant} €, il vous reste {self.balance} €")
    
    def deposit(self, montant):
        self.balance += montant
        print(f"Vous avez ajouter {montant} €, Vous avez maintenant {self.balance} €")

    def dump(self):
        print(f"{self.name}, {self.account_number}, {self.balance}")

    def transfere(self, montant, autre_compte):
        if montant > self.balance :
            print(f"Transfert impossible : solde insuffisant.")
        elif montant > self.plafond :
            print(f"Transfert impossible : montant dépasse le plafond de {self.plafond} €") 
        else : 
            self.balance -= montant
            autre_compte.deposit(montant)
            print(f"Transfert de {montant} € effectué de {self.name} à {autre_compte.name}.")

    def plafond_modifier(self, nouveau_plafond):
        self.plafond = nouveau_plafond
        print(f"Votre plafond il a modifier, votre retrait ne doit pas depasser {nouveau_plafond} €")
