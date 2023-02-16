import xlrd
from xlutils.copy import copy
def update_counter(counter):
    return counter

import xlrd
def xl_read(file):
    wb1 = xlrd.open_workbook(file)
    ws = wb1.sheet_by_index(0)
    total_records=ws.nrows
    for i in range(total_records):
        sno = update_counter(i)
        #xl_update("project_16a.xls", sno, "abc", "bbc", "mmn", "status")
        input_dict={}
        input_dict['sno']=sno
        input_dict['Scenario']=ws.cell_value(i,1)
        input_dict['Product_type'] = ws.cell_value(i,2)
        print(input_dict)
    return sno,input_dict

def xl_update(file,row, Uni_ID, ACT_ID, ASRI_ID):
    va2 = xlrd.open_workbook(file)
    ca = copy(va2)
    sheet = ca.get_sheet(0)
    sheet.write(row, 4, row)
    sheet.write(row, 5, Uni_ID)
    sheet.write(row, 6, ACT_ID)
    sheet.write(row, 7, ASRI_ID)
    ca.save(file)

uniid="a1b2c3"
actid="actid__"
asriid="//asriid"
sno,input_dict=xl_read("project.xls")
xl_update("project.xls",sno,uniid,actid,asriid)


