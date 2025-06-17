import frappe
from frappe import _

# Try importing correct function name
try:
    from erpnext.accounts.utils import get_running_finance_loan
except ImportError:
    get_running_finance_loan = None

@frappe.whitelist()
def calculate_running_finance_loan():
    accounts = [
        "20201001 - PRINCIPAL SHORT TERM LOAN-BAFL - TTPL",
        "20201002 - PRINCIPAL SHORT TERM LOAN- PCICL - TTPL",
        
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

    if get_running_finance_loan:
        data = get_running_finance_loan(accounts=obj, company="Tapal Tex Pvt. Ltd")
    else:
        # fallback manual logic
        data = frappe.db.sql("""
            SELECT account, SUM(debit - credit) as balance
            FROM `tabGL Entry`
            WHERE account IN %(accounts)s AND company = %(company)s AND is_cancelled = 0
            GROUP BY account
        """, {
            "accounts": [a['value'] for a in obj],
            "company": "Tapal Tex Pvt. Ltd"
        }, as_dict=True)

    balance = sum(b.get("balance", 0.0) for b in data)
    return {"value": balance, "fieldtype": "Currency"}
