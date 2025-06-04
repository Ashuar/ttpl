import frappe
import frappe.defaults
from erpnext.accounts.utils import get_account_balances

@frappe.whitelist()
def journal_payable():
    company = frappe.defaults.get_user_default("company")
    account_name = [
            "20201001 - PRINCIPAL SHORT TERM LOAN-BAFL - TTPL",
            "20201002 - PRINCIPAL SHORT TERM LOAN- PCICL - TTPL",
            "20203007 - SITE OVER TIME PAYABLE - TTPL",
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
            

    return {"value": total_balance, "fieldtype": "Currency"}