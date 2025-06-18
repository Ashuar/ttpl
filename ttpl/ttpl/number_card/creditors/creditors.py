import frappe
from frappe import _

# Try importing correct function name
try:
    from erpnext.accounts.utils import get_creditors
except ImportError:
    get_creditors = None

@frappe.whitelist()
def calculate_creditors():
    accounts = [
        "20202001 - STORE SUPPLIERS - TTPL",
        "20202002 - RAW MATERIAL SUPPLIERS - TTPL",
        "20202003 - PACKING MATERIAL SUPPLIER - TTPL",
        "20202004 - BROKER COMMISSION ON RAW MATERIAL - TTPL",
        "20202005 - BROKER COMMISSION ON LOCAL SALE - TTPL",
        "20202006 - BROKER COMMISSION ON EXPORT SALE - TTPL",
        "20202007 - SERVICES CREDITORS - TTPL",
        "20202008 - FREIGHT PAYABLE ON FG SALE - TTPL",
        "20202009 - OTHER PAYABLES - TTPL",
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

    if get_creditors:
        data = get_creditors(accounts=obj, company="Tapal Tex Pvt. Ltd")
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
