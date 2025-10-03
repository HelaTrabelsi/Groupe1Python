from datetime import datetime
import random

class Account:
    def __init__(self, name, account_number=None, balance=2000, plafond=1000):
        self.name = name
        self.account_number = account_number or self._generate_account_number()
        self.balance = balance
        self.plafond = plafond
        self.liste_historique = []
    
    def _generate_account_number(self):
        """Génère un numéro de compte aléatoire à 10 chiffres"""
        return random.randint(1000000000, 9999999999)

    def withdraw(self, montant):
        if montant > self.balance :
            print(f"Solde insuffisant pour retirer {montant} €.")
        elif montant > self.plafond :
            print(f"Montant dépasse le plafond de {self.plafond} €.") 
        else : 
            self.balance -= montant
            self.historique("retrait", montant)
            print(f"Vous avez retiré {montant} €, il vous reste {self.balance} €")
    
    def deposit(self, montant):
        self.balance += montant
        self.historique("depot", montant)
        print(f"Vous avez ajouté {montant} €, Vous avez maintenant {self.balance} €")

    def dump(self):
        print(f"{self.name}, {self.account_number}, {self.balance} €")

    def transfere(self, montant, autre_compte):
        if montant > self.balance :
            print("Transfert impossible : solde insuffisant.")
        elif montant > self.plafond :
            print(f"Transfert impossible : montant dépasse le plafond de {self.plafond} €") 
        else : 
            self.balance -= montant
            autre_compte.deposit(montant)
            self.historique("transfert_sortant", montant)
            autre_compte.historique("transfert_entrant", montant)
            print(f"Transfert de {montant} € effectué de {self.name} à {autre_compte.name}.")

    def historique(self,type,montant):
        self.liste_historique.append({
            "type": type,
            "montant": montant,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "solde_apres": self.balance
        })
    
    def afficher_historique(self):
        print(f"Historique de {self.name} :")
        for op in self.liste_historique:
            print(f"{op['date']} - {op['type']} : {op['montant']} € - Solde après : {op['solde_apres']} €")

    def plafond_modifier(self, nouveau_plafond):
        self.plafond = nouveau_plafond
        print(f"Votre plafond a été modifié, votre retrait ne doit pas dépasser {nouveau_plafond} €")

    def solde(self):
        """Retourne le solde actuel du compte"""
        return self.balance

    def __str__(self):
        return f"Compte {self.name} ({self.account_number}) : {self.balance} €"
