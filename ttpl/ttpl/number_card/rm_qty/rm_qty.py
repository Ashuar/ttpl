import frappe

@frappe.whitelist()
def rm_qty():
    query = """
    SELECT 
        SUM(DISTINCT pi.total_qty)
        FROM `tabPurchase Invoice` as pi
        LEFT JOIN `tabPurchase Invoice Item` as pii ON pii.parent = pi.name
        WHERE pi.docstatus = 1
		AND pii.item_group = 'Raw Material'
        AND YEAR(pi.posting_date) = YEAR(CURRENT_DATE())
    """
    value = frappe.db.sql(query)
    return {"value": value, "fieldtype": "Currency"}