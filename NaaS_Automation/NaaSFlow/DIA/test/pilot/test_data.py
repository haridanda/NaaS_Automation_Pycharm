#out={'Uni_ID':1,'ACT_ID':'2','ASRI_ID' : 'www'}
#print(type(out))
def update_counter(counter):
    return counter

def out(counter):
    return {'Uni_ID':f'UNI{counter}','ACT_ID':'2','ASRI_ID' : f'www{counter}'}



import pytest
def get_data(file):
    import xlrd
    input_list=[]
    wb1 = xlrd.open_workbook(file)
    ws = wb1.sheet_by_index(0)
    total_records = ws.nrows
    print(total_records)
    for i in range(1,total_records):
        sno = update_counter(i)
        # xl_update("project_16a.xls", sno, "abc", "bbc", "mmn", "status")
        input_dict = {}
        input_dict['sno'] = sno
        print(ws.cell_value(i, 1))
        input_dict['Scenario'] = ws.cell_value(i, 1)
        input_dict['ProductType'] = ws.cell_value(i, 2)
        input_dict['aend'] = ws.cell_value(i, 3)
        input_dict['U_interfaceType'] = ws.cell_value(i, 4)
        input_dict['uniType_1'] = ws.cell_value(i, 5)
        input_dict['failfast'] = ws.cell_value(i, 6)
        input_list.append(input_dict)
    print("!@#$%^&*()",input_list)
    return input_list

def write_data(file,i,dict_output):
    import xlrd
    from xlutils.copy import copy
    rb = xlrd.open_workbook(file)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    sheet.write(i, 7, dict_output['Uni_ID'])
    sheet.write(i, 8, dict_output['ACT_ID'])
    sheet.write(i, 9, dict_output['ASRI_ID'])
    wb.save(file)


#Scenario	ProductType	aend	U_interfaceType	uniType_1	failfast	S.no	Uni ID	ACT ID	ASRI ID
@pytest.mark.regression
@pytest.mark.parametrize("input_dict",get_data("Sample1.xls"))
def test_method_1(input_dict):
    print(input_dict['Scenario'])
    print(input_dict['ProductType'])
    print(input_dict['aend'])
    print(input_dict['U_interfaceType'])
    print(input_dict['uniType_1'])
    print(input_dict['failfast'])
   # write_data("Sample1.xls",input_dict['sno'], )
   # write_data("Sample1.xls", input_dict['sno'], dict_output=out)
    write_data("Sample1.xls", input_dict['sno'], dict_output=out(input_dict['sno']))