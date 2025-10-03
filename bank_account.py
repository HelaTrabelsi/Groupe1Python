import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random

# -------------------- Classe Account --------------------
class Account:
    """Classe représentant un compte bancaire"""
    def __init__(self, name, account_number=None, balance=2000, plafond=1000):
        """
        Initialise un compte avec :
        - name : nom du titulaire
        - account_number : numéro de compte (généré si None)
        - balance : solde initial
        - plafond : montant maximum par opération
        """
        self.name = name
        self.account_number = account_number or self._generate_account_number()
        self.balance = balance
        self.plafond = plafond
        self.liste_historique = [] 

    def _generate_account_number(self):
        """Génère un numéro de compte aléatoire à 10 chiffres."""
        return random.randint(1000000000, 9999999999)

    def withdraw(self, montant):
        """Retirer de l'argent si solde suffisant et montant <= plafond."""
        if montant > self.balance:
            print(f"Solde insuffisant pour retirer {montant} €.")
        elif montant > self.plafond:
            print(f"Montant dépasse le plafond de {self.plafond} €.")
        else:
            self.balance -= montant
            self.historique("retrait", montant)
            print(f"Vous avez retiré {montant} €, solde restant : {self.balance} €")

    def deposit(self, montant):
        """Ajouter de l'argent au compte."""
        self.balance += montant
        self.historique("depot", montant)
        print(f"Vous avez ajouté {montant} €, solde actuel : {self.balance} €")

    def transfere(self, montant, autre_compte):
        """
        Transférer de l'argent vers un autre compte.
        Vérifie solde et plafond.
        """
        if montant > self.balance:
            print("Transfert impossible : solde insuffisant.")
        elif montant > self.plafond:
            print(f"Transfert impossible : montant dépasse le plafond de {self.plafond} €")
        else:
            self.balance -= montant
            autre_compte.deposit(montant)
            self.historique("transfert_sortant", montant)
            autre_compte.historique("transfert_entrant", montant)
            print(f"Transfert de {montant} € effectué de {self.name} à {autre_compte.name}.")

    def historique(self, type_op, montant):
        """Enregistre une opération dans l'historique."""
        self.liste_historique.append({
            "type": type_op,
            "montant": montant,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "solde_apres": self.balance
        })

    def __str__(self):
        """Affiche les infos principales du compte."""
        return f"{self.name} ({self.account_number}) - Solde : {self.balance} € - Plafond : {self.plafond} €"


# -------------------- Interface graphique --------------------
class BankApp(tk.Tk):
    """Application bancaire avec interface graphique simple."""
    def __init__(self):
        super().__init__()
        self.title("Bank Account")  # Titre de la fenêtre
        self.geometry("500x300")      # Taille de la fenêtre

        # Comptes disponibles au lancement
        self.accounts = {
            "Ross": Account("Ross"),
            "Rachel": Account("Rachel")
        }

        self._build_ui()  # Construire l'interface

    def _build_ui(self):
        """Crée tous les widgets"""
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # --- Liste des comptes ---
        ttk.Label(frame, text="Comptes:").grid(row=0, column=0, sticky="w")
        self.acc_var = tk.StringVar(value=list(self.accounts.keys()))
        self.listbox = tk.Listbox(frame, listvariable=self.acc_var, height=5, exportselection=False)
        self.listbox.grid(row=1, column=0, sticky="ns")
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.on_show_info())
        self.listbox.selection_set(0)

        # --- Infos du compte sélectionné ---
        ttk.Label(frame, text="Infos du compte:").grid(row=0, column=1, sticky="w")
        self.info_text = tk.Text(frame, width=40, height=5, state="disabled")
        self.info_text.grid(row=1, column=1, sticky="n")

        # --- Montant à déposer/retraiter/transférer ---
        ttk.Label(frame, text="Montant (€):").grid(row=2, column=0, sticky="w", pady=(10,0))
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=2, column=1, sticky="we", pady=(10,0))

        # --- Boutons d'action ---
        ttk.Button(frame, text="➕ Déposer", command=self.on_deposit).grid(row=3, column=0, sticky="we", pady=5)
        ttk.Button(frame, text="➖ Retirer", command=self.on_withdraw).grid(row=3, column=1, sticky="we", pady=5)
        ttk.Button(frame, text="Transférer", command=self.on_transfer).grid(row=4, column=0, sticky="we", pady=5)
        ttk.Button(frame, text="Historique", command=self.on_show_history).grid(row=4, column=1, sticky="we", pady=5)

        # --- Status en bas de fenêtre ---
        self.status = ttk.Label(self, relief=tk.SUNKEN, anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Affiche automatiquement les infos du premier compte
        self.on_show_info()

    # -------------------- Fonctions utilitaires --------------------
    def selected_account(self):
        """Retourne le compte actuellement sélectionné dans la listbox."""
        sel = self.listbox.curselection()
        if not sel:
            return None
        name = self.listbox.get(sel[0])
        return self.accounts.get(name)

    def on_show_info(self):
        """Affiche les infos du compte sélectionné dans la zone de texte."""
        acc = self.selected_account()
        if acc:
            self.info_text.configure(state="normal")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert(tk.END, str(acc))
            self.status.config(text=f"Affichage : {acc.name}")

    def on_deposit(self):
        """Effectue un dépôt sur le compte sélectionné."""
        acc = self.selected_account()
        if acc:
            try:
                amount = float(self.amount_entry.get())
                acc.deposit(amount)
                self.on_show_info()
                self.status.config(text=f"{amount} € déposés sur {acc.name}")
                self.amount_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide")

    def on_withdraw(self):
        """Effectue un retrait sur le compte sélectionné."""
        acc = self.selected_account()
        if acc:
            try:
                amount = float(self.amount_entry.get())
                acc.withdraw(amount)
                self.on_show_info()
                self.status.config(text=f"{amount} € retirés de {acc.name}")
                self.amount_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide")

    def on_transfer(self):
        """Ouvre une petite fenêtre pour effectuer un transfert vers un autre compte."""
        acc = self.selected_account()


        transfer_win = tk.Toplevel(self)
        transfer_win.title("Transfert")
        transfer_win.geometry("250x150")

        ttk.Label(transfer_win, text="Montant à transférer:").pack(pady=5)
        entry_amount = ttk.Entry(transfer_win)
        entry_amount.pack(pady=5, fill="x", padx=10)

        ttk.Label(transfer_win, text="Vers le compte:").pack(pady=5)
        targets = [name for name in self.accounts if name != acc.name]
        target_var = tk.StringVar(value=targets)
        target_list = tk.Listbox(transfer_win, listvariable=target_var, height=len(targets), exportselection=False)
        target_list.pack(padx=10)

        def do_transfer():
            try:
                amount = float(entry_amount.get())
                sel = target_list.curselection()
                if not sel:
                    messagebox.showwarning("Erreur", "Sélectionnez un compte destinataire")
                    return
                target_acc = self.accounts[targets[sel[0]]]
                acc.transfere(amount, target_acc)
                self.on_show_info()
                self.status.config(text=f"{amount} € transférés de {acc.name} à {target_acc.name}")
                transfer_win.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide")

        ttk.Button(transfer_win, text="Transférer", command=do_transfer).pack(pady=10)

    def on_show_history(self):
        """Affiche l'historique des opérations du compte sélectionné."""
        acc = self.selected_account()
        hist_win = tk.Toplevel(self)
        hist_win.title(f"Historique - {acc.name}")
        hist_win.geometry("400x200")
        hist_list = tk.Listbox(hist_win)
        hist_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for op in acc.liste_historique:
            hist_list.insert(
                tk.END,
                f"{op['date']} | {op['type']} | {op['montant']} € | Solde: {op['solde_apres']} €"
            )


# -------------------- Lancer l'application --------------------
if __name__ == "__main__":
    app = BankApp()
    app.mainloop()
