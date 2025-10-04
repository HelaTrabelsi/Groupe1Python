import random

class Account:
    """
    Modèle d'un compte bancaire simple avec plafond et transfert.
    """
    def __init__(self, holder_name, balance=2000, limit=1000):
        self.holder_name = holder_name 
        
        self.account_number = random.randint(1000000000, 9999999999) 
        
        self.balance = float(balance)
        self.limit = float(limit) 
    def withdraw(self, amount):
        """Retire de l'argent du compte, vérifiant le solde et la limite."""
        amount = float(amount)
        if amount <= 0:
            print("Erreur : Le montant à retirer doit être positif.")
            return False

        if amount > self.limit:
            print(f"Retrait refusé : Le montant ({amount} €) dépasse la limite autorisée de {self.limit} € pour {self.holder_name}.")
            return False
        
        if amount > self.balance:
            print(f"Retrait refusé : Solde insuffisant pour retirer {amount} € pour {self.holder_name}. Solde actuel: {self.balance} €.")
            return False
        
        self.balance -= amount
        print(f"[RETRAIT] {self.holder_name} a retiré {amount} €. Nouveau solde : {self.balance} €.")
        return True
    
    def deposit(self, amount):
        """Dépose de l'argent sur le compte."""
        amount = float(amount)
        if amount > 0:
            self.balance += amount
            print(f"[DÉPÔT] {self.holder_name} a ajouté {amount} €. Nouveau solde : {self.balance} €.")
            return True
        print("Erreur : Le montant à déposer doit être positif.")
        return False

    def dump(self):
        """
        Affiche les informations finales du compte au format requis: 
        Nom, Numéro de compte, Solde arrondi à l'entier.
        """
        print(f"{self.holder_name}, {self.account_number}, {int(self.balance)}")

    def transfer(self, amount, target_account):
        """Transfère de l'argent vers un autre compte."""
        amount = float(amount)
        print(f"\n--- Tentative de Transfert : {self.holder_name} -> {target_account.holder_name} ({amount} €) ---")
        
        if self.withdraw(amount):
            target_account.deposit(amount)
            print(f"Transfert de {amount} € effectué de {self.holder_name} à {target_account.holder_name}.")
            return True
        else:
            print(f"Transfert échoué de {self.holder_name}.")
            return False

    def set_limit(self, new_limit):
        """Modifie la limite de retrait (plafond)."""
        new_limit = float(new_limit)
        if new_limit > 0:
            self.limit = new_limit
            print(f"Le plafond de retrait de {self.holder_name} est mis à jour : {new_limit} €.")
            return True
        print("Erreur : La nouvelle limite doit être positive.")
        return False


if __name__ == "__main__":
    print("Démo comptes Ross et Rachel")

    ross_account = Account(holder_name="Ross")
    rachel_account = Account(holder_name="Rachel")

    print(f"Ross Account: #{ross_account.account_number} (Initial: {ross_account.balance} €, Limite: {ross_account.limit} €)")
    print(f"Rachel Account: #{rachel_account.account_number} (Initial: {rachel_account.balance} €, Limite: {rachel_account.limit} €)\n")
    
    ross_account.withdraw(650) 

    rachel_account.deposit(1500) 
    rachel_account.withdraw(50) 
    
    rachel_account.transfer(350, ross_account)
    
 
    print("\n--- RÉSULTATS FINAUX (dump()) ---")

    ross_account.dump()
    rachel_account.dump()
