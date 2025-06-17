import frappe
from frappe import _

try:
    from erpnext.accounts.utils import get_accruals
except ImportError:
    get_accruals = None

@frappe.whitelist()
def calculate_accruals(company="Tapal Tex Pvt. Ltd"):
    account_names = [
"20203001 - ELECTRICITY BILL PAYABLE (MILL) - TTPL",
"20203002 - SOCIAL SECURITY PAYABLE - TTPL",
"20203003 - E.O.B.I. PAYABLE - TTPL",
"20203004 - LOADING UNLOADING PAYABLE - TTPL",
"20203005 - DAILY WAGES PAYABLE - TTPL",
"20203006 - AUDIT FEE PAYABLE - TTPL",
"20203007 - OVERTIME PAYABLE - TTPL",
"20203008 - SUI GASBILL POWERHOUSE PAYABLE - TTPL",
"20203009 - ELECTRICITY PAYABLE DIRECTORRESIDENCE - TTPL",
"20203010 - SUI GASDIRECTORS RESIDENCE PAYABLE - TTPL",
"20203011 - OTHERPAYABLES - TTPL",
"20203012 - ELECTRICITY BILL PAYABLE COLONY - TTPL",
"20203013 - CONTRACT LABORPACKING PAYABLE - TTPL",
"20203014 - BONUS PAYABLE (10C) - TTPL",
"20203015 - ELECTRICITY BILL PAYABLE HEAD OFFICE - TTPL",
"20203016 - TELEPHONE BILL PAYABLE HEAD OFFICE - TTPL",
"20203017 - TELEPHONE BILL PAYABLE (MILL) - TTPL",
"20203018 - EOBI PAYABLE HEAD OFFICE - TTPL",
"20203019 - WATERBILL PAYABLE - TTPL",
"20203020 - SALARY & WAGES PAYABLE-FACTORY - TTPL",
"20203021 - SALARY & WAGES PAYABLE-HEAD OFFICE - TTPL",
"20203022 - Accrued Quality Claim - TTPL",
"20203023 - RENT PAYABLE HEAD OFFICE - TTPL",
"20203024 - INTEREST PAYABLE ON LONG TERM LOAN-BAFL - TTPL",
"20203025 - INTEREST PAYABLE ON SHORT TERM LOAN (BANK ALFALAH) - TTPL",
"20203027 - INTEREST PAYABLE ON SHORT TERM LOAN (PAK CHINA) - TTPL",
"20203028 - INTEREST PAYABLE ON LONG TERM LOAN-PCICL - TTPL - TTPL",
"20203029 - GENERAL PAYABLES FACTORY - TTPL",
    ]

    accounts = frappe.get_all("Account", filters={"name": ["in", account_names]},
                              fields=["name", "root_type", "account_currency", "parent_account"])

    if get_accruals:
        data = get_accruals(accounts=[a["name"] for a in accounts], company=company)
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
