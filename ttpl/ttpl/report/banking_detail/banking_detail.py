# Copyright (c) 2025, ashuar and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    print(filters)
    columns, banks = get_columns(filters)
    banks = [
        f"SUM(CASE WHEN paid_to = '{bank.name}' THEN paid_amount ELSE 0 END) AS `{bank.name}`"
        for bank in banks
    ]
    sql = f"""
	SELECT
		party AS customer,
        {",".join(banks)}
	FROM
		`tabPayment Entry`
	WHERE
		payment_type = 'Receive'
		AND docstatus = 1
        AND posting_date >= '{filters.get("from_date")}'
        AND posting_date <= '{filters.get("to_date")}'
	GROUP BY
		party;
	"""
    print(sql)
    data = frappe.db.sql(sql)
    return columns, data


def get_columns(filters):
    columns = [{"fieldname": "party", "fieldtype": "Data", "label": "Party"}]
    banks = frappe.db.get_all(
        "Account",
        filters={
            "account_type": "Bank",
            "company": filters.get("company"),
            "is_group":0
        },
        fields=["name"],
    )
    for bank in banks:
        columns.append(
            {"fieldname": bank.name, "fieldtype": "Currency", "label": bank.name}
        )
    return columns, banks
