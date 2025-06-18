import frappe
from frappe import _

# Try importing correct function name
try:
    from erpnext.accounts.utils import get_trade_debtors
except ImportError:
    get_trade_debtors = None

@frappe.whitelist()
def calculate_trade_debtors_balance():
    accounts = [
        "10211001 - Nonwoven - TTPL",
        "10211002 - Trading - TTPL",
        "10211003 - Exports - TTPL",
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

    if get_trade_debtors:
        data = get_trade_debtors(accounts=obj, company="Tapal Tex Pvt. Ltd")
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
