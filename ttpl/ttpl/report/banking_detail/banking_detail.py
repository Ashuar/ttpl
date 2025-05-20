# Copyright (c) 2025, ashuar and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
#     columns = get_columns()
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
    # supplier_sql = f"""
    # SELECT
    #     gle.party,
    #     sp.supplier_name,
    #     '' as cash_accounts,
    #     gle.against as `Bank Accounts`,
    #     SUM(gle.debit)
    # FROM
    #     `tabGL Entry` gle
    # LEFT JOIN
    #     `tabSupplier` sp ON gle.party = sp.name
    # LEFT JOIN
    #     `tabAccount` acc ON gle.account = acc.name
    # WHERE
    #     gle.voucher_type IN ('Journal Entry', 'Payment Entry')
    #     AND gle.party_type = 'Supplier'
    #     AND gle.docstatus = 1
    #     AND gle.posting_date >= '{filters.get("from_date")}'
    #     AND gle.posting_date <= '{filters.get("to_date")}'
    # GROUP BY
    #     gle.party,
    #     sp.supplier_name
    # """

    # customer_data = frappe.db.sql(customer_sql)
    # total_customer = frappe.db.sql(total_customer_sql)
    # blank_row = tuple("-" for _ in range(len(total_customer[0]))) if total_customer else ()

    # supplier_data = frappe.db.sql(supplier_sql)
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
    # data = supplier_data

    # return columns, data

# def get_columns():
#     columns = [
#         {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
#         {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
#         {"fieldname": "cash_account", "fieldtype": "Currency", "label": "Cash", "width": 150},
#         {"fieldname": "bank_accounts", "feildtype": "Currency", "label": "Bank Accounts", "width": 200},
#         {"fieldname": "debit", "feildtype": "Currency", "label": "Debit", "width": 200}
#     ]
    # banks = frappe.db.get_all(
    #     "Bank Account",
    #      filters={"company": filters.get("company")},
    #     fields=["bank", "account"],
    # )
    # for bank in banks:
    #     obj = {"fieldname": bank.bank, "fieldtype": "Currency", "label": bank.bank}
    #     if obj in columns or not bank.account:
    #         continue
    #     columns.append(obj)
    # return columns
import frappe
def get_columns(banks):
    columns = [
        {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
        {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
        {"fieldname": "cash_account", "fieldtype": "Currency", "label": "Cash", "width": 150},
    ]

    seen_banks = set()
    for bank in banks:
        bank_name = bank.bank.strip()
        if bank_name not in seen_banks:
            seen_banks.add(bank_name)
            columns.append({
                "fieldname": bank_name.replace(" ", "_").lower(),
                "fieldtype": "Currency",
                "label": bank_name,
                "width": 150
            })

    return columns


def execute(filters=None):
    # Get list of bank accounts
    banks = frappe.get_all(
        "Bank Account",
        fields=["bank", "account"]
    )
    
    columns = get_columns(banks)
    
    # Fetch GL Entries
    supplier_sql = f"""
        SELECT
            gle.party,
            sp.supplier_name,
            gle.against,
            gle.debit
        FROM
            `tabGL Entry` gle
        LEFT JOIN
            `tabSupplier` sp ON gle.party = sp.name
        WHERE
            gle.voucher_type IN ('Journal Entry', 'Payment Entry')
            AND gle.party_type = 'Supplier'
            AND gle.docstatus = 1
            AND gle.posting_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}'
        
    """
    
    sp_raw_data = frappe.db.sql(supplier_sql, as_dict=True)
    
    # Aggregate data per supplier
    supplier_data = {}
    
    for row in sp_raw_data:
        party = row.party
        supplier_name = row.supplier_name or ""
        bank_account = row.against
        # journal_account = row.account
        debit = row.debit or 0

        # Initialize row if not already
        if party not in supplier_data:
            supplier_data[party] = {
                "party": party,
                "party_name": supplier_name,
                "cash_account": 0
            }
            for bank in banks:
                fieldname = bank.bank.replace(" ", "_").lower()
                supplier_data[party][fieldname] = 0

        # Check if against account matches a bank
        for bank in banks:
            if bank.account == bank_account:
                fieldname = bank.bank.replace(" ", "_").lower()
                supplier_data[party][fieldname] += debit
                break
    supplier_updated_data = list(supplier_data.values())

    supplier_total = {
    "party": "Total (Supplier)",
    "party_name": "",
    "cash_account": sum(row.get("cash_account", 0) for row in supplier_updated_data)
    }

    for bank in banks:
        fieldname = bank.bank.replace(" ", "_").lower()
        supplier_total[fieldname] = sum(row.get(fieldname, 0) for row in supplier_updated_data)

    # Fetch Customer GL Entries
    customer_sql = f"""
        SELECT
            gle.party,
            cu.customer_name,
            gle.against,
            gle.credit
        FROM
            `tabGL Entry` gle
        LEFT JOIN
            `tabCustomer` cu ON gle.party = cu.name
        WHERE
            gle.voucher_type IN ('Journal Entry', 'Payment Entry')
            AND gle.party_type = 'Customer'
            AND gle.docstatus = 1
            AND gle.posting_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}'
    """
    
    cu_raw_data = frappe.db.sql(customer_sql, as_dict=True)
    
    # Aggregate data per supplier
    customer_data = {}
    
    for row in cu_raw_data:
        party = row.party
        customer_name = row.customer_name or ""
        bank_account = row.against
        # journal_account = row.account
        credit = row.credit or 0

        # Initialize row if not already
        if party not in customer_data:
            customer_data[party] = {
                "party": party,
                "party_name": customer_name,
                "cash_account": 0
            }
            for bank in banks:
                fieldname = bank.bank.replace(" ", "_").lower()
                customer_data[party][fieldname] = 0

        # Check if against account matches a bank
        for bank in banks:
            if bank.account == bank_account:
                fieldname = bank.bank.replace(" ", "_").lower()
                customer_data[party][fieldname] += credit
                break
    customer_updated_data = list(customer_data.values())

    customer_total = {
    "party": "Total (Customer)",
    "party_name": "",
    "cash_account": sum(row.get("cash_account", 0) for row in customer_updated_data)
    }

    for bank in banks:
        fieldname = bank.bank.replace(" ", "_").lower()
        customer_total[fieldname] = sum(row.get(fieldname, 0) for row in customer_updated_data)
    
    #Internal Bank
    internal_transfer = frappe.db.sql(f"""
        SELECT 
        gl.account, 
        gl.against, 
        gl.debit, 
        gl.credit 
    FROM 
        `tabGL Entry` gl 
    LEFT JOIN 
        `tabPayment Entry` pe ON gl.voucher_no = pe.name 
    WHERE 
        pe.payment_type = 'Internal Transfer'
    """, as_dict=True)

    internal_data_updated = {}

    for row in internal_transfer:
        account = row.account
        against = row.against
        internal_debit = row.debit or 0
        credit = row.credit or 0
        internal_credit = -credit

        for bank in banks:
            fieldname = bank.bank.replace(" ", "_").lower()
            if bank.account == account:
                if fieldname not in internal_data_updated:
                    internal_data_updated[fieldname] = 0
                internal_data_updated[fieldname] -= internal_credit
            elif bank.account == against:
                if fieldname not in internal_data_updated:
                    internal_data_updated[fieldname] = 0
                internal_data_updated[fieldname] += internal_debit
                break
    internal_trans = list(internal_data_updated.values())

    

    data = customer_updated_data + [customer_total] +  supplier_updated_data + [supplier_total]
    return columns, data