import xlrd
global sno
from xlutils.copy import copy
def update_counter(counter):
    return counter

def verify_records(file):
    wb1 = xlrd.open_workbook(file)
    ws = wb1.sheet_by_index(0)
    total_records=ws.nrows
    for i in range(1,total_records):
        input_dict=xl_read(i,ws)
        # Keep the API/PY test method here
        xl_update("project1.xls",input_dict,uniid,actid,asriid)

import xlrd
def xl_read(i,ws):
    sno = update_counter(i)
    input_dict={}
    input_dict['sno']=sno
    input_dict['Scenario']=ws.cell_value(i,1)
    input_dict['Product_type'] = ws.cell_value(i,2)
    input_dict['U_interfaceType'] = ws.cell_value(i,3)
    print(input_dict)
    return input_dict

def xl_update(file,dict, Uni_ID, ACT_ID, ASRI_ID):
    va2 = xlrd.open_workbook(file)
    ca = copy(va2)
    sheet = ca.get_sheet(0)
    row=dict['sno']
    sheet.write(row, 6, row)
    sheet.write(row, 7, Uni_ID)
    sheet.write(row, 8, ACT_ID)
    sheet.write(row, 9, ASRI_ID)
    ca.save(file)

uniid="a1b2c3"
actid="actid__"
asriid="//asriid"
verify_records("project1.xls")