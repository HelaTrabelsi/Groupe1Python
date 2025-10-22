import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random
from typing import Dict, List

DEFAULT_BALANCE: float = 2000.0
DEFAULT_LIMIT: float = 1000.0

class Account:
    def __init__(self, holder_name: str, balance: float = DEFAULT_BALANCE, limit: float = DEFAULT_LIMIT) -> None:
        self.holder_name: str = holder_name
        self.account_number: int = random.randint(1000000000, 9999999999)
        self.balance: float = float(balance)
        self.limit: float = float(limit)
        self.liste_historique: List[dict] = []

    def withdraw(self, amount: float) -> bool:
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
        self.balance -= amount
        self._historiser("retrait", amount)
        return True

    def deposit(self, amount: float) -> bool:
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Erreur", "Le montant doit être positif.")
            return False
        self.balance += amount
        self._historiser("depot", amount)
        return True

    def transfer(self, amount: float, target_account: "Account") -> bool:
        amount = float(amount)
        if self.withdraw(amount):
            target_account.deposit(amount)
            self._historiser("transfert_sortant", amount)
            target_account._historiser("transfert_entrant", amount)
            return True
        return False

    def set_limit(self, new_limit: float) -> bool:
        new_limit = float(new_limit)
        if new_limit <= 0:
            messagebox.showerror("Erreur", "La limite doit être strictement positive.")
            return False
        self.limit = new_limit
        self._historiser("modif_plafond", new_limit)
        return True

    def _historiser(self, type_op: str, montant: float) -> None:
        self.liste_historique.append({
            "type": type_op,
            "montant": float(montant),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "solde_apres": float(self.balance),
        })

    def __str__(self) -> str:
        return (
            f"{self.holder_name} ({self.account_number})\n"
            f"Solde : {self.balance:.2f} €\n"
            f"Plafond de retrait : {self.limit:.2f} €"
        )

class BankApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gestion de Comptes Bancaires")
        self.geometry("680x400")
        self.accounts: Dict[str, Account] = {
            "Ross": Account("Ross"),
            "Rachel": Account("Rachel"),
        }
        self._build_ui()
        self._select_first_account()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        ttk.Label(left, text="Comptes :").pack(anchor="w")
        self.acc_var = tk.StringVar(value=list(self.accounts.keys()))
        self.listbox = tk.Listbox(left, listvariable=self.acc_var, height=10, exportselection=False, width=22)
        self.listbox.pack(fill="y")
        self.listbox.bind("<<ListboxSelect>>", lambda _e: self._refresh_info_panel())
        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="➕ Ajouter compte", command=self._on_add_account).grid(row=0, column=0, sticky="we", padx=(0, 6))
        ttk.Button(actions, text="🗑️ Supprimer compte", command=self._on_delete_account).grid(row=0, column=1, sticky="we")
        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(1, weight=1)
        ttk.Label(right, text="Infos du compte :").grid(row=0, column=0, columnspan=2, sticky="w")
        self.info_text = tk.Text(right, width=50, height=7, state="disabled")
        self.info_text.grid(row=1, column=0, columnspan=2, sticky="we")
        ttk.Label(right, text="Montant (€) :").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.amount_entry = ttk.Entry(right)
        self.amount_entry.grid(row=2, column=1, sticky="we", pady=(10, 0))
        right.columnconfigure(1, weight=1)
        ttk.Button(right, text="➕ Dépôt", command=self._on_deposit).grid(row=3, column=0, sticky="we", pady=5)
        ttk.Button(right, text="➖ Retrait", command=self._on_withdraw).grid(row=3, column=1, sticky="we", pady=5)
        ttk.Button(right, text="🔁 Transférer", command=self._on_transfer).grid(row=4, column=0, sticky="we", pady=5)
        ttk.Button(right, text="📜 Historique", command=self._on_show_history).grid(row=4, column=1, sticky="we", pady=5)
        ttk.Button(right, text="⚙️ Modifier le plafond", command=self._on_set_limit).grid(row=5, column=0, sticky="we", pady=5)
        self.status = ttk.Label(self, relief=tk.SUNKEN, anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _select_first_account(self) -> None:
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
        self._refresh_info_panel()

    def _selected_account(self) -> Account:
        sel = self.listbox.curselection()
        name = self.listbox.get(sel[0])
        return self.accounts.get(name)

    def _refresh_accounts_list(self, select_name: str = None) -> None:
        names = list(self.accounts.keys())
        self.acc_var.set(names)
        self._refresh_info_panel()

    def _refresh_info_panel(self) -> None:
        acc = self._selected_account()
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        if acc:
            self.info_text.insert(tk.END, str(acc))
            self.status.config(text=f"Compte sélectionné : {acc.holder_name}")

    def _on_add_account(self) -> None:
        def create_account() -> None:
            name = entry_name.get()
            if not name:
                messagebox.showerror("Erreur", "Le nom du titulaire est obligatoire.")
                return
            try:
                balance = float(entry_balance.get())
            except ValueError:
                messagebox.showerror("Erreur", "Solde initial invalide.")
                return
            self.accounts[name] = Account(name, balance, DEFAULT_LIMIT)
            self._refresh_accounts_list(select_name=name)
            self.status.config(text=f"✅ Compte '{name}' créé (solde {balance:.2f} €, plafond {DEFAULT_LIMIT:.2f} €).")
            add_win.destroy()

        add_win = tk.Toplevel(self)
        add_win.title("➕ Ajouter un compte")
        add_win.geometry("340x210")
        add_win.resizable(False, False)
        ttk.Label(add_win, text="Nom du titulaire :").pack(pady=(12, 4))
        entry_name = ttk.Entry(add_win)
        entry_name.pack(pady=4, fill="x", padx=16)
        entry_name.focus_set()
        ttk.Label(add_win, text="Solde initial (€) :").pack(pady=(10, 4))
        entry_balance = ttk.Entry(add_win)
        entry_balance.insert(0, f"{DEFAULT_BALANCE:.0f}")
        entry_balance.pack(pady=4, fill="x", padx=16)
        buttons = ttk.Frame(add_win)
        buttons.pack(pady=14)
        ttk.Button(buttons, text="✅ Valider / Créer", command=create_account).grid(row=0, column=0, padx=6, ipadx=6, ipady=3)
        ttk.Button(buttons, text="❌ Annuler", command=add_win.destroy).grid(row=0, column=1, padx=6, ipadx=6, ipady=3)

    def _on_delete_account(self) -> None:
        acc = self._selected_account()
        if not acc:
            messagebox.showwarning("Attention", "Aucun compte sélectionné.")
            return
        if not messagebox.askyesno("Confirmation", f"Supprimer le compte '{acc.holder_name}' ?"):
            return
        del self.accounts[acc.holder_name]
        self._refresh_accounts_list()
        self.status.config(text=f"🗑️ Compte '{acc.holder_name}' supprimé.")

    def _on_deposit(self) -> None:
        acc = self._selected_account()
        try:
            amt = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        if acc.deposit(amt):
            self.status.config(text=f"💰 {amt:.2f} € déposés sur {acc.holder_name}.")
            self._refresh_info_panel()
        self.amount_entry.delete(0, tk.END)

    def _on_withdraw(self) -> None:
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
        source = self._selected_account()
        def do_transfer() -> None:
            try:
                amt = float(entry_amount.get())
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide.")
                return
            sel = target_list.curselection()
            if not sel:
                messagebox.showwarning("Erreur", "Choisissez un compte destinataire.")
                return
            target_name = targets[sel[0]]
            target_acc = self.accounts[target_name]
            if source.transfer(amt, target_acc):
                self.status.config(text=f"🔁 {amt:.2f} € transférés de {source.holder_name} à {target_acc.holder_name}.")
                self._refresh_info_panel()
                transfer_win.destroy()

        transfer_win = tk.Toplevel(self)
        transfer_win.title("Transfert")
        transfer_win.geometry("280x190")
        transfer_win.resizable(False, False)
        ttk.Label(transfer_win, text="Montant (€) :").pack(pady=(10, 4))
        entry_amount = ttk.Entry(transfer_win)
        entry_amount.pack(pady=4, fill="x", padx=12)
        ttk.Label(transfer_win, text="Vers le compte :").pack(pady=(10, 4))
        targets = [name for name in self.accounts if name != source.holder_name]
        target_var = tk.StringVar(value=targets)
        target_list = tk.Listbox(transfer_win, listvariable=target_var, height=min(6, len(targets)), exportselection=False)
        target_list.pack(padx=12, fill="x")
        ttk.Button(transfer_win, text="Transférer", command=do_transfer).pack(pady=12)

    def _on_show_history(self) -> None:
        acc = self._selected_account()
        hist_win = tk.Toplevel(self)
        hist_win.title(f"Historique — {acc.holder_name}")
        hist_win.geometry("460x260")
        hist_win.resizable(True, True)
        hist_list = tk.Listbox(hist_win)
        hist_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        if not acc.liste_historique:
            hist_list.insert(tk.END, "Aucune opération enregistrée.")
            return
        for op in acc.liste_historique:
            hist_list.insert(
                tk.END,
                f"{op['date']} | {op['type']} | {op['montant']:.2f} € | Solde: {op['solde_apres']:.2f} €"
            )

    def _on_set_limit(self) -> None:
        acc = self._selected_account()
        def apply_limit() -> None:
            try:
                new_limit = float(entry_limit.get())
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide.")
                return
            if acc.set_limit(new_limit):
                self.status.config(text=f"⚙️ Nouveau plafond de {acc.holder_name} : {new_limit:.2f} €")
                self._refresh_info_panel()
                limit_win.destroy()

        limit_win = tk.Toplevel(self)
        limit_win.title("Modifier le plafond")
        limit_win.geometry("260x140")
        limit_win.resizable(False, False)
        ttk.Label(limit_win, text="Nouvelle limite (€) :").pack(pady=(12, 6))
        entry_limit = ttk.Entry(limit_win)
        entry_limit.insert(0, f"{acc.limit:.0f}")
        entry_limit.pack(pady=4, fill="x", padx=14)
        ttk.Button(limit_win, text="Appliquer", command=apply_limit).pack(pady=12)

if __name__ == "__main__":
    app = BankApp()
    app.mainloop()
