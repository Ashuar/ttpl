# Copyright (c) 2025, ashuar and contributors
# For license information, please see license.txt

import frappe


# def execute(filters=None):
#     columns, banks = get_columns(filters)
#     _banks = []
#     for bank in banks:
#         if bank.account:
#             _banks.append(
#                 f"SUM(CASE WHEN pe.paid_to = '{bank.account}' THEN pe.paid_amount ELSE 0 END) AS `{bank.bank}`",
#             )

#     supplier_banks = []
#     for bank in banks:
#         if bank.account:
#             supplier_banks.append(
#                 f"SUM(CASE WHEN pe.paid_from = '{bank.account}' THEN pe.paid_amount ELSE 0 END) AS `{bank.bank}`",
#             )

#     #get customer data bankwise
#     customer_sql = f"""
# 	SELECT
# 		pe.party,
#         pe.party_name,
#         (
#             SELECT SUM(pe2.paid_amount)
#             FROM `tabPayment Entry` pe2
#             WHERE pe2.party = pe.party
#             AND pe2.payment_type = 'Receive'
#             AND pe2.mode_of_payment = 'Cash'
#             AND pe2.docstatus = 1
#             AND pe2.posting_date >= '{filters.get("from_date")}'
#             AND pe2.posting_date <= '{filters.get("to_date")}'
            
#         ) AS cash_accounts,
#         {",".join(_banks)}
# 	FROM
# 		`tabPayment Entry` pe
#     LEFT JOIN
# 		`tabBank Account` ba ON pe.paid_to = ba.account
# 	WHERE
# 		pe.payment_type = 'Receive'
# 		AND pe.docstatus = 1
#         AND pe.posting_date >= '{filters.get("from_date")}'
#         AND pe.posting_date <= '{filters.get("to_date")}'
# 	GROUP BY
# 		pe.party,
#         pe.party_name
#     """
#     #get total of customer

#     total_customer_sql = f"""
#     SELECT
#         '<b>Total</b>' as customer,
#         '' as party_name,
#         SUM(CASE 
#         WHEN pe.mode_of_payment = 'Cash' THEN pe.paid_amount 
#         ELSE 0 
#         END) AS cash_total,
#         {",".join(_banks)}
#     FROM
#         `tabPayment Entry` pe
#     LEFT JOIN
#         `tabBank Account` ba ON pe.paid_to = ba.account
#     WHERE
#         pe.payment_type = 'Receive'
#         AND pe.docstatus = 1
#         AND pe.posting_date >= '{filters.get("from_date")}'
#         AND pe.posting_date <= '{filters.get("to_date")}'
# 	"""

#     # get supplier data
#     supplier_sql = f"""
# 	SELECT
# 		pe.party,
#         pe.party_name,
#         (
#             SELECT SUM(pe2.paid_amount)
#             FROM `tabPayment Entry` pe2
#             WHERE pe2.party = pe.party
#             AND pe2.payment_type = 'Pay'
#             AND pe2.mode_of_payment = 'Cash'
#             AND pe2.docstatus = 1
#             AND pe2.posting_date >= '{filters.get("from_date")}'
#             AND pe2.posting_date <= '{filters.get("to_date")}'
            
#         ) AS cash_accounts,
#         {",".join(supplier_banks)}
# 	FROM
# 		`tabPayment Entry` pe
#     LEFT JOIN
# 		`tabBank Account` ba ON pe.paid_from = ba.account
# 	WHERE
# 		pe.payment_type = 'Pay'
# 		AND pe.docstatus = 1
#         AND pe.posting_date >= '{filters.get("from_date")}'
#         AND pe.posting_date <= '{filters.get("to_date")}'
# 	GROUP BY
# 		pe.party,
#         pe.party_name
#     """
#     # Supplier total query
#     total_supplier_sql = f"""
#     SELECT
#         '<b>Total</b>' as supplier,
#         '' as party_name,
#         SUM(CASE 
#         WHEN pe.mode_of_payment = 'Cash' THEN pe.paid_amount 
#         ELSE 0 
#         END) AS cash_total,
#         {",".join(supplier_banks)}
#     FROM
#         `tabPayment Entry` pe
#     LEFT JOIN
#         `tabBank Account` ba ON pe.paid_to = ba.account
#     WHERE
#         pe.payment_type = 'Pay'
#         AND pe.docstatus = 1
#         AND pe.posting_date >= '{filters.get("from_date")}'
#         AND pe.posting_date <= '{filters.get("to_date")}'

#     """
#     customer_data = frappe.db.sql(customer_sql)
#     total_customer = frappe.db.sql(total_customer_sql)
#     blank_row = tuple("-" for _ in range(len(total_customer[0])))

#     supplier_data = frappe.db.sql(supplier_sql)
#     total_supplier = frappe.db.sql(total_supplier_sql)
#     blank_row2 = tuple("-" for _ in range(len(total_supplier[0])))

#     # data = list(customer_data + total_customer + blank_row + supplier_data + total_supplier)
#     data = list(customer_data + total_customer)
#     data.append(blank_row)
#     data += list(supplier_data + total_supplier)
#     data.append(blank_row2)
    
#     #calculating net balance
#     customer_total = total_customer[0][2:]
#     supplier_total = total_supplier[0][2:]

#     net_balance = [b- c for b,c in zip(customer_total, supplier_total)]
#     net_balance_row = ("<b>Net Balance</b>", "", *net_balance)

    
#     data.append(net_balance_row)
#     return columns, data


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


def execute(filters=None):
    columns, banks = get_columns(filters)
    _banks = []
    for bank in banks:
        if bank.account:
            _banks.append(
                f"SUM(CASE WHEN gle.against = '{bank.account}' THEN gle.credit ELSE 0 END) AS `{bank.bank}`",
            )

    supplier_banks = []
    for bank in banks:
        if bank.account:
            supplier_banks.append(
                f"""SUM(
                    CASE WHEN (
                        (gle.voucher_type = 'Payment Entry' AND gle.against = '{bank.account}')
                        OR
                        (gle.voucher_type = 'Journal Entry' AND EXISTS (
                            SELECT SUM(CASE WHEN jea.against_account = '{bank.account}' THEN jea.debit ELSE 0 END)
                            FROM `tabJournal Entry Account` jea
                            WHERE jea.parent = gle.voucher_no
                        ))
                    ) THEN gle.debit ELSE 0 END
                ) AS `{bank.bank}`"""
        )
    # get customer data bankwise from GL Entry
    customer_sql = f"""
    SELECT
        gle.party,
        cu.customer_name,
        SUM(CASE
            WHEN acc.account_type = 'Cash' THEN gle.credit 
            ELSE 0 
        END) AS cash_accounts,
        {','.join(_banks)}
    FROM
        `tabGL Entry` gle
    LEFT JOIN 
        `tabCustomer` cu ON gle.party = cu.name
    LEFT JOIN `tabAccount` acc ON gle.account = acc.name
    WHERE
        gle.voucher_type IN ('Payment Entry', 'Journal Entry')
        AND gle.party_type = 'Customer'
        AND gle.docstatus = 1
        AND gle.posting_date >= '{filters.get("from_date")}'
        AND gle.posting_date <= '{filters.get("to_date")}'
    GROUP BY
        gle.party,
        cu.customer_name
    """

    total_customer_sql = f"""
    SELECT
        '<b>Total</b>' as customer,
        '' as party_name,
        SUM(CASE 
            WHEN acc.account_type = 'Cash' THEN gle.credit 
            ELSE 0 
        END) AS cash_total,
        {','.join(_banks)}
    FROM
        `tabGL Entry` gle
    LEFT JOIN `tabAccount` acc ON gle.account = acc.name
    WHERE
        gle.voucher_type IN ('Payment Entry', 'Journal Entry')
        AND gle.party_type = 'Customer'
        AND gle.docstatus = 1
        AND gle.posting_date >= '{filters.get("from_date")}'
        AND gle.posting_date <= '{filters.get("to_date")}'
    """

    # get supplier data from GL Entry
    supplier_sql = f"""
    SELECT
        gle.party,
        sp.supplier_name,
        SUM(CASE 
            WHEN acc.account_type = 'Cash' THEN gle.debit 
            ELSE 0 
        END) AS cash_accounts,
        {','.join(supplier_banks) if supplier_banks else 'NULL'}
    FROM
        `tabGL Entry` gle
    LEFT JOIN
        `tabSupplier` sp ON gle.party = sp.name
    LEFT JOIN
        `tabAccount` acc ON gle.account = acc.name
    WHERE
        gle.voucher_type IN ('Payment Entry', 'Journal Entry')
        AND gle.party_type = 'Supplier'
        AND gle.docstatus = 1
        AND gle.posting_date >= '{filters.get("from_date")}'
        AND gle.posting_date <= '{filters.get("to_date")}'
    GROUP BY
        gle.party,
        sp.supplier_name
    """
    print(supplier_sql)


    total_supplier_sql = f"""
    SELECT
        '<b>Total</b>' as supplier,
        '' as party_name,
        SUM(CASE 
            WHEN acc.account_type = 'Cash' THEN gle.debit 
            ELSE 0 
        END) AS cash_total,
        {','.join(supplier_banks)}
    FROM
        `tabGL Entry` gle
    LEFT JOIN `tabAccount` acc ON gle.account = acc.name
    WHERE
        gle.voucher_type IN ('Payment Entry', 'Journal Entry')
        AND gle.party_type = 'Supplier'
        AND gle.docstatus = 1
        AND gle.posting_date >= '{filters.get("from_date")}'
        AND gle.posting_date <= '{filters.get("to_date")}'
    """

    customer_data = frappe.db.sql(customer_sql)
    total_customer = frappe.db.sql(total_customer_sql)
    blank_row = tuple("-" for _ in range(len(total_customer[0]))) if total_customer else ()

    supplier_data = frappe.db.sql(supplier_sql)
    total_supplier = frappe.db.sql(total_supplier_sql)
    blank_row2 = tuple("-" for _ in range(len(total_supplier[0]))) if total_supplier else ()

    data = list(customer_data + total_customer)
    if blank_row:
        data.append(blank_row)
    data += list(supplier_data + total_supplier)
    if blank_row2:
        data.append(blank_row2)

    # calculating net balance
    customer_total = total_customer[0][2:] if total_customer else []
    supplier_total = total_supplier[0][2:] if total_supplier else []

    if customer_total and supplier_total:
        net_balance = [(b or 0.0) - (c or 0.0) for b, c in zip(customer_total, supplier_total)]
        net_balance_row = ("<b>Net Balance</b>", "", *net_balance)
        data.append(net_balance_row)

    return columns, data


def get_columns(filters):
    columns = [
        {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
        {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
        {"fieldname": "cash_account", "fieldtype": "Currency", "label": "Cash", "width": 150},
    ]
    banks = frappe.db.get_all(
        "Bank Account",
        filters={"company": filters.get("company")},
        fields=["bank", "account"],
    )
    for bank in banks:
        obj = {"fieldname": bank.bank, "fieldtype": "Currency", "label": bank.bank}
        if obj in columns or not bank.account:
            continue
        columns.append(obj)
    return columns, banks
