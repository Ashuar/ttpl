import frappe

@frappe.whitelist()
def received_value():
    query = """
    SELECT 
        SUM(DISTINCT pi.grand_total)
        FROM `tabPurchase Invoice` as pi
        LEFT JOIN `tabPurchase Invoice Item` as pii ON pii.parent = pi.name
        WHERE pi.docstatus = 1
		AND pii.item_group = 'Raw Material'
        AND YEAR(pi.posting_date) = YEAR(CURRENT_DATE())
    """
    value = frappe.db.sql(query)
    return {"value": value, "fieldtype": "Currency"}