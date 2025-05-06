import frappe

@frappe.whitelist()
def calculate_total_receivable():
    outstand_value = """
        SELECT 
            SUM(outstanding_amount)
        FROM
            `tabSales Invoice`
        WHERE 
            docstatus = 1
    """
    value = frappe.db.sql(outstand_value)

    return {"value": value, "fieldtype": "Currency"}