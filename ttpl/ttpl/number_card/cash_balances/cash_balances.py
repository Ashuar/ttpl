import frappe

@frappe.whitelist()
def get_cash_balances():
    query = """
        SELECT
            SUM(debit) AS total_debit,
            SUM(credit) AS total_credit,
            SUM(debit - credit) AS balance
        FROM
            `tabGL Entry`
        WHERE
            `account` IN (
                '10202001 - CASH IN HAND HEAD OFFICE - TTPL',
                '10202002 - CASH IN HAND FACTORY - TTPL'
            )
            AND is_cancelled = 0
    """
    value = frappe.db.sql(query)[0][0] or 0.0
    return {
        "value": value,
        "fieldtype": "Currency"
    }
