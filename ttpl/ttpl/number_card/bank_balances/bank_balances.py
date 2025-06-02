import frappe

@frappe.whitelist()
def get_bank_balances():
    query = """
        SELECT
            SUM(debit) AS total_debit,
            SUM(credit) AS total_credit,
            SUM(debit - credit) AS balance
        FROM
            `tabGL Entry`
        WHERE
            account IN (
                '10201001 - BANK ALFALAH LTD ISLAMIC - GB - TTPL',
                '10201002 - HABIB METRO - DHA VIII - TTPL',
                '10201003 - MEEZAN BANK LIMITED - DHA VIII - TTPL',
                '10201004 - BANK AL HABIB DHA Phase VIII Branch - TTPL',
                '10201005 - Bank Alfalah Chak Jhumra - TTPL',
                '10201006 - BANK ALFALAH KARACHI - TTPL',
                '10201007 - Al BARAKA BANK LIMITED - TTPL'
            )
            AND is_cancelled = 0
    """
    value = frappe.db.sql(query)[0][0] or 0.0
    return {
        "value": value,
        "fieldtype": "Currency"
    }
