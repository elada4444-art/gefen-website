#!/usr/bin/env python3
"""Turn the Excel workbook into SQL that (re)loads the contacts table.

Usage:  python3 tools/build_phonebook.py "<path to workbook>.xlsx" > seed.sql

Reads the sheet "ספר טלפונים", columns A-G (header in row 1), skips empty
rows and prints an INSERT statement for public.contacts. Run the output in
the Supabase SQL editor (prefix with `delete from public.contacts;` to
replace everything). The live site reads contacts from Supabase, so the
workbook is only a one-off import source, not the source of truth.
"""
import sys

import openpyxl

SHEET = "ספר טלפונים"
COLS = 7  # A-G -> company, department, name, role, office_phone, mobile, email

if len(sys.argv) < 2:
    sys.exit("usage: build_phonebook.py <workbook.xlsx>")

wb = openpyxl.load_workbook(sys.argv[1], data_only=True, read_only=True)
ws = wb[SHEET]
rows_iter = ws.iter_rows(min_row=1, max_col=COLS, values_only=True)
next(rows_iter)  # header


def q(v):
    return "'" + ("" if v is None else str(v).strip()).replace("'", "''") + "'"


values = []
for row in rows_iter:
    cells = ["" if v is None else str(v).strip() for v in row]
    if not any(cells):
        continue
    values.append("(" + ",".join(q(c) for c in cells) + ")")

print("insert into public.contacts (company, department, name, role, office_phone, mobile, email) values")
print(",\n".join(values) + ";")
print(f"-- {len(values)} rows", file=sys.stderr)
