import frappe

@frappe.whitelist()
def get_account_balance():
    """
    Returns the total balance of selected stock-related accounts as a single Currency value.
    """

    query = """
        SELECT
            SUM(debit - credit) AS balance
        FROM
            `tabGL Entry`
        WHERE
            `account` IN (
                '10203001 - STORE & SPARES - TTPL',
                '10205001 - STOCK IN TRADE - TTPL',
                '10205002 - STOCK IN TRANSIT - TTPL',
                '10205004 - HEATER FUEL MATERIAL - TTPL',
                '10206000 - RAW MATERIAL STORAGE - TTPL',
                '10207003 - FINISHED GOODS (ALL GSM STOCK IN HAND) - TTPL',
                '10209000 - WORK IN PROCESS - TTPL'
            )
            AND is_cancelled = 0
    """

    value = frappe.db.sql(query)[0][0] or 0.0
    return {
        "value": value,
        "fieldtype": "Currency"
    }
