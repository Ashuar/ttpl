import frappe
from collections import defaultdict

def bank_fieldname(account_name):
    return account_name.replace(" ", "_").lower()

def get_columns(banks):
    columns = [
        {"fieldname": "party", "fieldtype": "Data", "label": "Party", "width": 200},
        {"fieldname": "party_name", "fieldtype": "Data", "label": "Party Name", "width": 200},
        {"fieldname": "cash_account", "fieldtype": "Currency", "label": "Cash", "width": 150},
    ]
    seen = set()
    for bank in banks:
        account_label = bank.account.strip()
        fieldname = bank_fieldname(account_label)
        if fieldname not in seen:
            seen.add(fieldname)
            columns.append({
                "fieldname": fieldname,
                "fieldtype": "Currency",
                "label": account_label,
                "width": 150
            })
    return columns

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    cash_account_name = "10202001 - CASH IN HAND HEAD OFFICE - TTPL"

    banks = frappe.get_all("Bank Account", fields=["account"])
    columns = get_columns(banks)

    def initialize_row(party, party_name):
        row = {
            "party": party,
            "party_name": party_name,
            "cash_account": 0
        }
        for bank in banks:
            row[bank_fieldname(bank.account)] = 0
        return row

    # ------------------- SUPPLIER DATA -------------------
    supplier_sql = f"""
        SELECT gle.party, sp.supplier_name, gle.against, gle.debit
        FROM `tabGL Entry` gle
        LEFT JOIN `tabSupplier` sp ON gle.party = sp.name
        WHERE gle.voucher_type IN ('Journal Entry', 'Payment Entry')
        AND gle.party_type = 'Supplier'
        AND gle.docstatus = 1
        AND gle.posting_date BETWEEN '{from_date}' AND '{to_date}'
    """
    sp_data = frappe.db.sql(supplier_sql, as_dict=True)

    supplier_rows = {}
    for row in sp_data:
        party = row.party
        party_name = row.supplier_name or ""
        bank_account = row.against
        amount = row.debit or 0

        if party not in supplier_rows:
            supplier_rows[party] = initialize_row(party, party_name)

        if bank_account == cash_account_name:
            supplier_rows[party]["cash_account"] += amount
        else:
            for bank in banks:
                if bank.account == bank_account:
                    fieldname = bank_fieldname(bank.account)
                    supplier_rows[party][fieldname] += amount
                    break

    supplier_data = list(supplier_rows.values())

    # ------------------- CUSTOMER DATA -------------------
    customer_sql = f"""
        SELECT gle.party, cu.customer_name, gle.against, gle.credit
        FROM `tabGL Entry` gle
        LEFT JOIN `tabCustomer` cu ON gle.party = cu.name
        WHERE gle.voucher_type IN ('Journal Entry', 'Payment Entry')
        AND gle.party_type = 'Customer'
        AND gle.docstatus = 1
        AND gle.posting_date BETWEEN '{from_date}' AND '{to_date}'
    """
    cu_data = frappe.db.sql(customer_sql, as_dict=True)

    customer_rows = {}
    for row in cu_data:
        party = row.party
        party_name = row.customer_name or ""
        bank_account = row.against
        amount = row.credit or 0

        if party not in customer_rows:
            customer_rows[party] = initialize_row(party, party_name)

        if bank_account == cash_account_name:
            customer_rows[party]["cash_account"] += amount
        else:
            for bank in banks:
                if bank.account == bank_account:
                    fieldname = bank_fieldname(bank.account)
                    customer_rows[party][fieldname] += amount
                    break

    customer_data = list(customer_rows.values())

    # ------------------- INTERNAL TRANSFERS -------------------
    internal_sql = f"""
        SELECT gl.voucher_no, gl.account, gl.debit, gl.credit
        FROM `tabGL Entry` gl
        LEFT JOIN `tabPayment Entry` pe ON gl.voucher_no = pe.name
        WHERE pe.payment_type = 'Internal Transfer'
        AND gl.docstatus = 1
        AND gl.posting_date BETWEEN '{from_date}' AND '{to_date}'
        ORDER BY gl.voucher_no
    """
    internal_entries = frappe.db.sql(internal_sql, as_dict=True)

    internal_by_voucher = defaultdict(list)
    for row in internal_entries:
        internal_by_voucher[row.voucher_no].append(row)

    internal_rows = []
    internal_total = initialize_row("Total (Internal Transfer)", "")

    for voucher_no, entries in internal_by_voucher.items():
        row = initialize_row(f"Internal Transfer: {voucher_no}", "")
        for entry in entries:
            net_amount = (entry.debit or 0) - (entry.credit or 0)
            if entry.account == cash_account_name:
                row["cash_account"] += net_amount
                internal_total["cash_account"] += net_amount
            else:
                for bank in banks:
                    if bank.account == entry.account:
                        fieldname = bank_fieldname(bank.account)
                        row[fieldname] += net_amount
                        internal_total[fieldname] += net_amount
                        break
        internal_rows.append(row)

    # ------------------- TOTALS -------------------
    def compute_total(data, label):
        total = initialize_row(label, "")
        for row in data:
            for key in total:
                if key in row and isinstance(row[key], (int, float)):
                    total[key] += row[key]
        return total

    total_supplier = compute_total(supplier_data, "Total (Supplier)")
    total_customer = compute_total(customer_data, "Total (Customer)")

    def merge_rows(row1, row2, subtract=False):
        result = initialize_row("Grand Total", "")
        for key in result:
            result[key] = (row1.get(key, 0)) + ((-1 if subtract else 1) * (row2.get(key, 0)))
        return result

    intermediate_total = merge_rows(total_customer, internal_total)
    grand_total = merge_rows(intermediate_total, total_supplier, subtract=True)
    grand_total["party"] = "Net Total"

    # ------------------- FINAL DATA -------------------
    data = (
        customer_data +
        [total_customer] +
        supplier_data +
        [total_supplier] +
        internal_rows +
        [internal_total] +
        [grand_total]
    )

    return columns, data


