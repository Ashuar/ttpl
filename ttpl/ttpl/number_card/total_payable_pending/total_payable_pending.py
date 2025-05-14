import frappe
import frappe.defaults
from erpnext.accounts.utils import get_account_balances

@frappe.whitelist()
def calculate_total_payable():
    outstand_value = """
        SELECT 
            SUM(outstanding_amount)
        FROM
            `tabPurchase Invoice`
        WHERE 
            docstatus = 1
    """
    out_value = frappe.db.sql(outstand_value)
    company = frappe.defaults.get_user_default("company")
    account_name = ["20201001 - PRINCIPAL SHORT TERM LOAN-BAFL - TTPL",
                    "20201002 - PRINCIPAL SHORT TERM LOAN- PCICL - TTPL",
                    "20203007 - OVERTIME PAYABLE - TTPL",
                    "20203015 - ELECTRICITY BILL PAYABLE HEAD OFFICE - TTPL",
                    "20203020 - SALARY & WAGES PAYABLE-FACTORY - TTPL",
                    "20203021 - SALARY & WAGES PAYABLE-HEAD OFFICE - TTPL",
                    "20203023 - RENT PAYABLE HEAD OFFICE - TTPL",
                    "20203024 - INTEREST PAYABLE ON LONG TERM LOAN-BAFL - TTPL",
                    "20203025 - INTEREST PAYABLE ON SHORT TERM LOAN (BANK ALFALAH) - TTPL",
                    "20203027 - INTEREST PAYABLE ON SHORT TERM LOAN (PAK CHINA) - TTPL",
                    "20203028 - INTEREST PAYABLE ON LONG TERM LOAN-PCICL - TTPL - TTPL",
                    "20204003 - EOBI PAYABLE - TTPL",
    ]
    account_balance ={}
    for account_name in account_name:
        account_currency = frappe.get_cached_value("Account", account_name, "account_currency")
        accounts = [{
            "value": account_name,
            "account_currency": account_currency
        }]
        
        account_value = get_account_balances(accounts=accounts, company=company)
        
        if account_value:
            balance = account_value[0]["balance"]
            account_balance[account_name] = balance
            total_balance = abs(sum(account_balance.values()))
            

    list_value = out_value[0][0]
    value = total_balance + float(list_value)
    return {"value": value, "fieldtype": "Currency"}
