import frappe
from frappe import _

try:
    from erpnext.accounts.utils import get_longterm_loan
except ImportError:
    get_longterm_loan = None

@frappe.whitelist()
def calculate_longterm_loan(company="Tapal Tex Pvt. Ltd"):
    account_names = [
        "20108001 - LONG TERM LOAN  BANK ALFALAH LTD ISLAMIC - TTPL",
        "20108002 - LONGTERM LOAN from PAK CHINA INVESTMENT - TTPL"
    ]

    accounts = frappe.get_all("Account", filters={"name": ["in", account_names]},
                              fields=["name", "root_type", "account_currency", "parent_account"])

    if get_longterm_loan:
        data = get_longterm_loan(accounts=[a["name"] for a in accounts], company=company)
    else:
        data = frappe.db.sql("""
            SELECT account, SUM(debit - credit) as balance
            FROM `tabGL Entry`
            WHERE account IN %(accounts)s AND company = %(company)s AND is_cancelled = 0
            GROUP BY account
        """, {
            "accounts": [a["name"] for a in accounts],
            "company": company
        }, as_dict=True)

    balance = sum(b.get("balance", 0.0) for b in data)
    return {"value": balance, "fieldtype": "Currency"}
