"""
Gestion simple de comptes bancaires
---------------------------------------------------------
Fonctionnalités :
- Dépôt / Retrait (avec plafond de retrait)
- Transfert entre comptes
- Historique des opérations
- Créer / supprimer des comptes (utilisateurs)
- Modification du plafond de retrait

"""

# --- Imports ---
import tkinter as tk                         # Tkinter : base de l'interface graphique
from tkinter import ttk, messagebox          # ttk (widgets modernes) + boîtes de dialogue
from datetime import datetime                # Pour dater les opérations de l’historique
import random                                # Pour générer des numéros de compte aléatoires

# --- Constantes par défaut ---
DEFAULT_BALANCE: float = 2000.0              # Solde initial par défaut
DEFAULT_LIMIT: float = 1000.0                # Plafond par défaut pour les retraits

# =======================
#   Modèle : Account
# =======================

class Account:
    def __init__(self, holder_name: str, balance: float = DEFAULT_BALANCE, limit: float = DEFAULT_LIMIT) -> None:
        # Identité du titulaire
        self.holder_name: str = holder_name
        # Numéro de compte aléatoire à 10 chiffres
        self.account_number: int = random.randint(1000000000, 9999999999)
        # Solde du compte
        self.balance: float = float(balance)
        # Plafond de retrait autorisé par opération
        self.limit: float = float(limit)
        # Liste d’opérations
        self.liste_historique: List[dict] = []

    def withdraw(self, amount: float) -> bool:
        """Retirer de l'argent : vérifie que le montant est > 0, <= limite et <= solde."""
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Erreur", "Le montant doit être positif.")
            return False
        if amount > self.limit:
            messagebox.showwarning("Limite dépassée", f"Le montant dépasse la limite de {self.limit:.2f} €.")
            return False
        if amount > self.balance:
            messagebox.showwarning("Solde insuffisant", f"Solde insuffisant ({self.balance:.2f} €).")
            return False
        # Décrémenter le solde puis tracer l’opération
        self.balance -= amount
        self._historiser("retrait", amount)
        return True

    def deposit(self, amount: float) -> bool:
        """Déposer de l'argent : vérifie que le montant est > 0."""
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Erreur", "Le montant doit être positif.")
            return False
        # Augmenter le solde puis tracer l’opération
        self.balance += amount
        self._historiser("depot", amount)
        return True

    def transfer(self, amount: float, target_account: "Account") -> bool:
        """Transférer vers un autre compte : retire ici, dépose chez la cible, historise les deux côtés."""
        amount = float(amount)
        if self.withdraw(amount):
            target_account.deposit(amount)
            self._historiser("transfert_sortant", amount)
            target_account._historiser("transfert_entrant", amount)
            return True
        return False

    def set_limit(self, new_limit: float) -> bool:
        """Changer le plafond de retrait : doit être strictement positif."""
        new_limit = float(new_limit)
        if new_limit <= 0:
            messagebox.showerror("Erreur", "La limite doit être strictement positive.")
            return False
        self.limit = new_limit
        self._historiser("modif_plafond", new_limit)
        return True

    def _historiser(self, type_op: str, montant: float) -> None:
        """Ajouter une ligne dans l'historique (type, montant, date lisible, solde après)."""
        self.liste_historique.append({
            "type": type_op,
            "montant": float(montant),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "solde_apres": float(self.balance),
        })

    def __str__(self) -> str:
        """Représentation texte 'propre' d’un compte."""
        return (
            f"{self.holder_name} ({self.account_number})\n"
            f"Solde : {self.balance:.2f} €\n"
            f"Plafond de retrait : {self.limit:.2f} €"
        )

# =======================
#   Bank App
# =======================
class BankApp(tk.Tk):
    def __init__(self) -> None:
        # Appelle le constructeur de tk.Tk pour créer la fenêtre principale
        super().__init__()
        # Titre et taille de la fenêtre
        self.title("Gestion de Comptes Bancaires")
        self.geometry("680x400")
        # Dictionnaire des comptes (clé = nom du titulaire, valeur = objet Account)
        self.accounts: Dict[str, Account] = {
            "Ross": Account("Ross"),
            "Rachel": Account("Rachel"),
        }
        # Construit tout l’UI puis sélectionne automatiquement un compte au démarrage
        self._build_ui()
        self._select_first_account()

    def _build_ui(self) -> None:
        """Crée la mise en page : colonne gauche (liste & actions), colonne droite (infos & opérations)."""
        # Conteneur principal
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        # --- Colonne gauche : liste de comptes + boutons Ajouter/Supprimer ---
        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 10))

        ttk.Label(left, text="Comptes :").pack(anchor="w")

        # StringVar liée à la Listbox : quand on change acc_var, la liste se met à jour
        self.acc_var = tk.StringVar(value=list(self.accounts.keys()))

        # Listbox montrant les noms des comptes
        self.listbox = tk.Listbox(left, listvariable=self.acc_var, height=10, exportselection=False, width=22)
        self.listbox.pack(fill="y")

        # À chaque changement de sélection dans la liste, on rafraîchit le panneau d’infos
        self.listbox.bind("<<ListboxSelect>>", lambda _e: self._refresh_info_panel())

        # Cadre pour les boutons liés aux comptes
        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(8, 0))

        # Bouton : Ajouter un compte (ouvre une fenêtre avec formulaire)
        ttk.Button(actions, text="➕ Ajouter compte", command=self._on_add_account).grid(row=0, column=0, sticky="we", padx=(0, 6))
        # Bouton : Supprimer le compte sélectionné (avec confirmation)
        ttk.Button(actions, text="🗑️ Supprimer compte", command=self._on_delete_account).grid(row=0, column=1, sticky="we")

        # --- Colonne droite : panneau d’infos + opérations ---
        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        # Rendre la colonne droite extensible (prend l’espace restant)
        container.columnconfigure(1, weight=1)

        ttk.Label(right, text="Infos du compte :").grid(row=0, column=0, columnspan=2, sticky="w")

        # Zone de texte en lecture seule pour afficher les infos du compte
        self.info_text = tk.Text(right, width=50, height=7, state="disabled")
        self.info_text.grid(row=1, column=0, columnspan=2, sticky="we")

        # Champ de saisie pour taper un montant (dépôt/retrait/transfert)
        ttk.Label(right, text="Montant (€) :").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.amount_entry = ttk.Entry(right)
        self.amount_entry.grid(row=2, column=1, sticky="we", pady=(10, 0))
        right.columnconfigure(1, weight=1)  # la colonne du champ montant s’étire

        # Boutons d’opérations sur le compte sélectionné
        ttk.Button(right, text="➕ Dépôt",       command=self._on_deposit).grid(  row=3, column=0, sticky="we", pady=5)
        ttk.Button(right, text="➖ Retrait",     command=self._on_withdraw).grid( row=3, column=1, sticky="we", pady=5)
        ttk.Button(right, text="🔁 Transférer",  command=self._on_transfer).grid( row=4, column=0, sticky="we", pady=5)
        ttk.Button(right, text="📜 Historique",  command=self._on_show_history).grid(row=4, column=1, sticky="we", pady=5)
        ttk.Button(right, text="⚙️ Modifier le plafond", command=self._on_set_limit).grid(row=5, column=0, sticky="we", pady=5)

        # Barre de statut en bas (messages utilisateur)
        self.status = ttk.Label(self, relief=tk.SUNKEN, anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _select_first_account(self) -> None:
        """Sélectionne le premier compte de la liste au démarrage (si la liste n’est pas vide) puis met à jour l’affichage."""
        if self.listbox.size() > 0:              # size() = nombre d’éléments dans la Listbox
            self.listbox.selection_set(0)         # sélectionne l’élément d’index 0 (premier)
        self._refresh_info_panel()                # met à jour le panneau d’infos à droite

    def _selected_account(self) -> Account:
        """Retourne l’objet Account correspondant à la sélection actuelle dans la Listbox."""
        sel = self.listbox.curselection()         # tuple d’indices sélectionnés (ex: (0,))
        name = self.listbox.get(sel[0])           # récupère le nom affiché à l’index sélectionné
        return self.accounts.get(name)            # retourne l’objet Account stocké dans le dict

    def _refresh_accounts_list(self, select_name: str = None) -> None:
        """Recharge la Listbox à partir du dictionnaire self.accounts (sans gérer ici la sélection)."""
        names = list(self.accounts.keys())        # liste des noms (clés du dict)
        self.acc_var.set(names)                   # met à jour la Listbox via la StringVar liée
        self._refresh_info_panel()                # met à jour le panneau d’infos (au cas où)

    def _refresh_info_panel(self) -> None:
        """Efface et réécrit le panneau d’infos en fonction du compte sélectionné."""
        acc = self._selected_account()            # objet Account actuellement sélectionné
        self.info_text.config(state="normal")     # déverrouille la zone de texte pour écrire dedans
        self.info_text.delete("1.0", tk.END)      # efface tout le texte
        if acc:
            self.info_text.insert(tk.END, str(acc))                      # affiche la représentation __str__ du compte
            self.status.config(text=f"Compte sélectionné : {acc.holder_name}")  # met à jour la barre d’état
        self.info_text.config(state="disabled")   # repasse en lecture seule (empêche l’édition manuelle)

    # =======================
    #  Actions
    # =======================
    def _on_add_account(self) -> None:
        """Ouvre une fenêtre pour saisir un nouveau compte (nom + solde) puis le crée."""

        def create_account() -> None:
            # Récupération et validations des champs du formulaire
            name = entry_name.get()
            if not name:
                messagebox.showerror("Erreur", "Le nom du titulaire est obligatoire.")
                return
            try:
                balance = float(entry_balance.get())
            except ValueError:
                messagebox.showerror("Erreur", "Solde initial invalide.")
                return

            # Création et enregistrement du compte dans le dictionnaire
            self.accounts[name] = Account(name, balance, DEFAULT_LIMIT)

            # Rafraîchir la liste
            self._refresh_accounts_list(select_name=name)

            # Message utilisateur dans la barre de statut (montants formatés 2 décimales)
            self.status.config(text=f"✅ Compte '{name}' créé (solde {balance:.2f} €, plafond {DEFAULT_LIMIT:.2f} €).")

            # Fermer la fenêtre d’ajout
            add_win.destroy()

        # --- Petite fenêtre (Toplevel) pour créer un compte ---
        add_win = tk.Toplevel(self)
        add_win.title("➕ Ajouter un compte")
        add_win.geometry("340x210")
        add_win.resizable(False, False)

        ttk.Label(add_win, text="Nom du titulaire :").pack(pady=(12, 4))
        entry_name = ttk.Entry(add_win)           # champ pour le nom
        entry_name.pack(pady=4, fill="x", padx=16)
        entry_name.focus_set()                    # focus direct sur le champ

        ttk.Label(add_win, text="Solde initial (€) :").pack(pady=(10, 4))
        entry_balance = ttk.Entry(add_win)        # champ pour le solde initial
        entry_balance.insert(0, f"{DEFAULT_BALANCE:.0f}")  # valeur par défaut affichée (2000)
        entry_balance.pack(pady=4, fill="x", padx=16)

        # Boutons Valider / Annuler
        buttons = ttk.Frame(add_win)
        buttons.pack(pady=14)
        ttk.Button(buttons, text="✅ Valider / Créer", command=create_account).grid(row=0, column=0, padx=6, ipadx=6, ipady=3)
        ttk.Button(buttons, text="❌ Annuler", command=add_win.destroy).grid(row=0, column=1, padx=6, ipadx=6, ipady=3)

    def _on_delete_account(self) -> None:
        """Supprime le compte actuellement sélectionné après confirmation."""
        acc = self._selected_account()
        if not acc:
            messagebox.showwarning("Attention", "Aucun compte sélectionné.")
            return
        # Confirmation utilisateur
        if not messagebox.askyesno("Confirmation", f"Supprimer le compte '{acc.holder_name}' ?"):
            return
        # Suppression dans le dictionnaire puis rafraîchissement
        del self.accounts[acc.holder_name]
        self._refresh_accounts_list()
        self.status.config(text=f"🗑️ Compte '{acc.holder_name}' supprimé.")

    def _on_deposit(self) -> None:
        """Lit le montant, effectue un dépôt sur le compte sélectionné, met à jour la vue et vide le champ."""
        acc = self._selected_account()
        try:
            amt = float(self.amount_entry.get())  # conversion du texte saisi en float
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        if acc.deposit(amt):
            self.status.config(text=f"💰 {amt:.2f} € déposés sur {acc.holder_name}.")
            self._refresh_info_panel()            # réaffiche solde/plafond mis à jour
        self.amount_entry.delete(0, tk.END)       # vide le champ de saisie

    def _on_withdraw(self) -> None:
        """Lit le montant, effectue un retrait depuis le compte sélectionné, met à jour la vue et vide le champ."""
        acc = self._selected_account()
        try:
            amt = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        if acc.withdraw(amt):
            self.status.config(text=f"💸 {amt:.2f} € retirés de {acc.holder_name}.")
            self._refresh_info_panel()
        self.amount_entry.delete(0, tk.END)

    def _on_transfer(self) -> None:
        """Ouvre une fenêtre pour transférer un montant vers un autre compte."""
        source = self._selected_account()         # compte émetteur (sélectionné)

        def do_transfer() -> None:
            # Lecture du montant
            try:
                amt = float(entry_amount.get())
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide.")
                return
            # Vérifier qu’une cible est sélectionnée
            sel = target_list.curselection()
            if not sel:
                messagebox.showwarning("Erreur", "Choisissez un compte destinataire.")
                return
            # Récupérer le nom et l’objet Account du destinataire
            target_name = targets[sel[0]]
            target_acc = self.accounts[target_name]
            # Exécuter le transfert + rafraîchissement + fermeture
            if source.transfer(amt, target_acc):
                self.status.config(text=f"🔁 {amt:.2f} € transférés de {source.holder_name} à {target_acc.holder_name}.")
                self._refresh_info_panel()
                transfer_win.destroy()

        # --- Fenêtre de transfert ---
        transfer_win = tk.Toplevel(self)
        transfer_win.title("Transfert")
        transfer_win.geometry("280x190")
        transfer_win.resizable(False, False)

        ttk.Label(transfer_win, text="Montant (€) :").pack(pady=(10, 4))
        entry_amount = ttk.Entry(transfer_win)     # champ montant
        entry_amount.pack(pady=4, fill="x", padx=12)

        ttk.Label(transfer_win, text="Vers le compte :").pack(pady=(10, 4))
        # Liste des noms cibles (tous les comptes sauf la source)
        targets = [name for name in self.accounts if name != source.holder_name]
        target_var = tk.StringVar(value=targets)
        target_list = tk.Listbox(transfer_win, listvariable=target_var, height=min(6, len(targets)), exportselection=False)
        target_list.pack(padx=12, fill="x")

        ttk.Button(transfer_win, text="Transférer", command=do_transfer).pack(pady=12)

    def _on_show_history(self) -> None:
        """Affiche l’historique du compte sélectionné dans une nouvelle fenêtre."""
        acc = self._selected_account()

        # Fenêtre d’historique
        hist_win = tk.Toplevel(self)
        hist_win.title(f"Historique — {acc.holder_name}")
        hist_win.geometry("460x260")
        hist_win.resizable(True, True)

        # Listbox pour lister chaque opération
        hist_list = tk.Listbox(hist_win)
        hist_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Si aucun historique, message dédié
        if not acc.liste_historique:
            hist_list.insert(tk.END, "Aucune opération enregistrée.")
            return

        # Sinon, on affiche chaque ligne formatée
        for op in acc.liste_historique:
            hist_list.insert(
                tk.END,
                f"{op['date']} | {op['type']} | {op['montant']:.2f} € | Solde: {op['solde_apres']:.2f} €"
            )

    def _on_set_limit(self) -> None:
        """Ouvre une fenêtre pour modifier le plafond du compte sélectionné."""
        acc = self._selected_account()

        def apply_limit() -> None:
            # Lecture du nouveau plafond
            try:
                new_limit = float(entry_limit.get())
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide.")
                return
            # Si la mise à jour est valide, on actualise
            if acc.set_limit(new_limit):
                self.status.config(text=f"⚙️ Nouveau plafond de {acc.holder_name} : {new_limit:.2f} €")
                self._refresh_info_panel()
                limit_win.destroy()

        # --- Fenêtre de modification du plafond ---
        limit_win = tk.Toplevel(self)
        limit_win.title("Modifier le plafond")
        limit_win.geometry("260x140")
        limit_win.resizable(False, False)

        ttk.Label(limit_win, text="Nouvelle limite (€) :").pack(pady=(12, 6))
        entry_limit = ttk.Entry(limit_win)
        entry_limit.insert(0, f"{acc.limit:.0f}")  # prérempli avec la limite actuelle
        entry_limit.pack(pady=4, fill="x", padx=14)

        ttk.Button(limit_win, text="Appliquer", command=apply_limit).pack(pady=12)

# =======================
#   Point d’entrée
# =======================
if __name__ == "__main__":
    app = BankApp()    # instancie l’application (crée la fenêtre)
    app.mainloop()     # boucle d’événements Tkinter (écoute clics, clavier, etc.)
