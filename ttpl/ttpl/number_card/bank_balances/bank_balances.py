import frappe
from erpnext.accounts.utils import get_account_balances

@frappe.whitelist()
def get_bank_balances():
    accounts = [
        "10201001 - BANK ALFALAH LTD ISLAMIC - GB - TTPL",
        "10201002 - HABIB METRO - DHA VIII - TTPL",
        "10201003 - MEEZAN BANK LIMITED - DHA VIII - TTPL",
        "10201004 - BANK AL HABIB DHA Phase VIII Branch - TTPL",
        "10201005 - Bank Alfalah Chak Jhumra - TTPL",
        "10201006 - BANK ALFALAH KARACHI - TTPL",
        "10201007 - Al BARAKA BANK LIMITED - TTPL",
    ]
    obj = []
    for account in accounts:
        if frappe.db.exists("Account", account):
            a = frappe.get_doc("Account", account)
            obj.append(
                {
                    "value": a.name,
                    "expandable": 0,
                    "root_type": a.root_type,
                    "account_currency": a.account_currency,
                    "parent": a.parent_account,
                }
            )
    data = get_account_balances(accounts=obj, company="Tapal Tex Pvt. Ltd")
    balance = 0
    for b in data:
        balance += b.get("balance", 0.0)
    return {"value": balance, "fieldtype": "Currency"}
