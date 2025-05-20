# Copyright (c) 2025, ashuar and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    # _banks = []
    # for bank in banks:
    #     if bank.account:
    #         _banks.append(
    #             f"SUM(CASE WHEN gle.against = '{bank.account}' THEN gle.credit ELSE 0 END) AS `{bank.bank}`",
    #         )

    # supplier_banks = []
    # for bank in banks:
    #     if bank.account:
    #         supplier_banks.append(
    #             f"SUM(CASE WHEN gle.against = '{bank.account}' THEN gle.debit ELSE 0 END) AS `{bank.bank}`",
    #         )
    # get customer data bankwise from GL Entry
    # customer_sql = f"""
    # SELECT
    #     gle.party,
    #     cu.customer_name,
    #     SUM(CASE
    #         WHEN acc.account_type = 'Cash' THEN gle.credit 
    #         ELSE 0 
    #     END) AS cash_accounts,
    #     {','.join(_banks)}
    # FROM
    #     `tabGL Entry` gle
    # LEFT JOIN 
    #     `tabCustomer` cu ON gle.party = cu.name
    # LEFT JOIN `tabAccount` acc ON gle.account = acc.name
    # WHERE
    #     gle.voucher_type IN ('Payment Entry', 'Journal Entry')
    #     AND gle.party_type = 'Customer'
    #     AND gle.docstatus = 1
    #     AND gle.posting_date >= '{filters.get("from_date")}'
    #     AND gle.posting_date <= '{filters.get("to_date")}'
    # GROUP BY
    #     gle.party,
    #     cu.customer_name
    # """

    # total_customer_sql = f"""
    # SELECT
    #     '<b>Total</b>' as customer,
    #     '' as party_name,
    #     SUM(CASE 
    #         WHEN acc.account_type = 'Cash' THEN gle.credit 
    #         ELSE 0 
    #     END) AS cash_total,
    #     {','.join(_banks)}
    # FROM
    #     `tabGL Entry` gle
    # LEFT JOIN `tabAccount` acc ON gle.account = acc.name
    # WHERE
    #     gle.voucher_type IN ('Payment Entry', 'Journal Entry')
    #     AND gle.party_type = 'Customer'
    #     AND gle.docstatus = 1
    #     AND gle.posting_date >= '{filters.get("from_date")}'
    #     AND gle.posting_date <= '{filters.get("to_date")}'
    # """

    # get supplier data from GL Entry
    supplier_sql = f"""
    SELECT
        gle.party,
        sp.supplier_name,
        '' as cash_accounts,
        gle.against as `Bank Accounts`,
        SUM(gle.debit)
    FROM
        `tabGL Entry` gle
    LEFT JOIN
        `tabSupplier` sp ON gle.party = sp.name
    LEFT JOIN
        `tabAccount` acc ON gle.account = acc.name
    WHERE
        gle.voucher_type IN ('Journal Entry', 'Payment Entry')
        AND gle.party_type = 'Supplier'
        AND gle.docstatus = 1
        AND gle.posting_date >= '{filters.get("from_date")}'
        AND gle.posting_date <= '{filters.get("to_date")}'
    GROUP BY
        gle.party,
        sp.supplier_name
    """

    # customer_data = frappe.db.sql(customer_sql)
    # total_customer = frappe.db.sql(total_customer_sql)
    # blank_row = tuple("-" for _ in range(len(total_customer[0]))) if total_customer else ()

    supplier_data = frappe.db.sql(supplier_sql)
    # total_supplier = frappe.db.sql(total_supplier_sql)
    # blank_row2 = tuple("-" for _ in range(len(total_supplier[0]))) if total_supplier else ()

    # data = list(customer_data + total_customer)
    # if blank_row:
    #     data.append(blank_row)
    # data += list(supplier_data + total_supplier)
    # if blank_row2:
        # data.append(blank_row2)

    # calculating net balance
    # customer_total = total_customer[0][2:] if total_customer else []
    # supplier_total = total_supplier[0][2:] if total_supplier else []

    # if customer_total and supplier_total:
    #     net_balance = [(b or 0.0) - (c or 0.0) for b, c in zip(customer_total, supplier_total)]
    #     net_balance_row = ("<b>Net Balance</b>", "", *net_balance)
    #     data.append(net_balance_row)
    data = supplier_data

    return columns, data

def get_columns():
    columns = [
        {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
        {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
        {"fieldname": "cash_account", "fieldtype": "Currency", "label": "Cash", "width": 150},
        {"fieldname": "bank_accounts", "feildtype": "Currency", "label": "Bank Accounts", "width": 200},
        {"fieldname": "debit", "feildtype": "Currency", "label": "Debit", "width": 200}
    ]
    # banks = frappe.db.get_all(
    #     "Bank Account",
    #     filters={"company": filters.get("company")},
    #     fields=["bank", "account"],
    # )
    # for bank in banks:
    #     obj = {"fieldname": bank.bank, "fieldtype": "Currency", "label": bank.bank}
    #     if obj in columns or not bank.account:
    #         continue
    #     columns.append(obj)
    return columns

# def execute(filters=None):
#     columns, banks = get_columns(filters)
#     data = []
    
#     # Get all supplier payments in date range
#     gl_entries = frappe.get_all("GL Entry",
#         filters={
#             "voucher_type": ["in", ["Payment Entry", "Journal Entry"]],
#             "party_type": "Supplier",
#             "docstatus": 1,
#             "posting_date": ["between", [filters.from_date, filters.to_date]]
#         },
#         fields=["party", "voucher_type", "voucher_no", "debit", "credit", "account", "against"]
#     )
    
#     # Process each entry
#     for entry in gl_entries:
#         row = {
#             "party": entry.party,
#             "supplier_name": frappe.get_value("Supplier", entry.party, "supplier_name"),
#             "cash_accounts": 0
#         }
        
#         # Set bank amounts
#         for bank in banks:
#             if bank.account:
#                 if (entry.voucher_type == "Payment Entry" and entry.against == bank.account):
#                         row[bank.bank] = entry.debit
#                 elif (entry.voucher_type == "Journal Entry" and entry.against == bank.account):
#                         row[bank.bank] = entry.credit
        
#         data.append(row)
    
#     return columns, data

# # def is_bank_in_journal_entry(voucher_no, account):
# #     return frappe.db.exists("Journal Entry Account", {
# #         "parent": voucher_no,
# #         "account": account,
# #         "party_type": "Supplier"
# #     })


# def get_columns(filters):
#     columns = [
#         {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
#         {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
#         {"fieldname": "cash_account", "fieldtype": "Currency", "label": "Cash", "width": 150},
#     ]
#     banks = frappe.db.get_all(
#         "Bank Account",
#         filters={"company": filters.get("company")},
#         fields=["bank", "account"],
#     )
#     for bank in banks:
#         obj = {"fieldname": bank.bank, "fieldtype": "Currency", "label": bank.bank}
#         if obj in columns or not bank.account:
#             continue
#         columns.append(obj)
#     return columns, banks