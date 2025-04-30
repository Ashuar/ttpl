# Copyright (c) 2025, ashuar and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, banks = get_columns(filters)
    _banks = []
    for bank in banks:
        print(bank)
        if bank.account:
            _banks.append(
                f"SUM(CASE WHEN pe.paid_to = '{bank.account}' THEN pe.paid_amount ELSE 0 END) AS `{bank.bank}`"
            )
    customer_sql = f"""
	SELECT
		pe.party AS customer,
        pe.party_name,
        {",".join(_banks)}
	FROM
		`tabPayment Entry` pe
    LEFT JOIN
		`tabBank Account` ba ON pe.paid_to = ba.account
	WHERE
		payment_type = 'Receive'
		AND pe.docstatus = 1
        AND pe.posting_date >= '{filters.get("from_date")}'
        AND pe.posting_date <= '{filters.get("to_date")}'
	GROUP BY
		pe.party,
        pe.party_name
    """
    total_customer_sql = f"""
    SELECT
        'Total' as customer,
        '' as party_name,
        {",".join(_banks)}
    FROM
        `tabPayment Entry` pe
    LEFT JOIN
        `tabBank Account` ba ON pe.paid_to = ba.account
    WHERE
        pe.payment_type = 'Receive'
        AND pe.docstatus = 1
        AND pe.posting_date >= '{filters.get("from_date")}'
        AND pe.posting_date <= '{filters.get("to_date")}'
	"""
    supplier_sql = f"""
    SELECT
		pe.party AS supplier,
        pe.party_name,
        {",".join(_banks)}
	FROM
		`tabPayment Entry` pe
    LEFT JOIN
		`tabBank Account` ba ON pe.paid_to = ba.account
	WHERE
		payment_type = 'Pay'
		AND pe.docstatus = 1
        AND pe.posting_date >= '{filters.get("from_date")}'
        AND pe.posting_date <= '{filters.get("to_date")}'
	GROUP BY
		pe.party,
        pe.party_name
    
    """
    total_supplier_sql = f"""
    SELECT
        'Total' as supplier,
        '' as party_name,
        {",".join(_banks)}
    FROM
        `tabPayment Entry` pe
    LEFT JOIN
        `tabBank Account` ba ON pe.paid_to = ba.account
    WHERE
        pe.payment_type = 'Pay'
        AND pe.docstatus = 1
        AND pe.posting_date >= '{filters.get("from_date")}'
        AND pe.posting_date <= '{filters.get("to_date")}'

    """
    
    customer_data = frappe.db.sql(customer_sql)
    total_customer = frappe.db.sql(total_customer_sql)
    supplier_data = frappe.db.sql(supplier_sql)
    total_supplier = frappe.db.sql(total_supplier_sql)

    data = customer_data + total_customer + supplier_data + total_supplier
    return columns, data


def get_columns(filters):
    columns = [
        {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
        {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
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
