my_cookie = None
path = "//Users//ac71601//Documents//PycharmProjects//act//NaaS_Automation//NaaSFlow//DIA//test//Sample1.xls"
login = "/login"
UNI_workflow = "/workflow_engine/startJobWithOptions/LNAAS_CREATE_UNI_SL_V1"
skinny_workflow = "/workflow_engine/startJobWithOptions/Create_Resource_ASRI_AL"
SL_workflow = "/workflow_engine/startJobWithOptions/LNAAS_CREATE_DIA_SERVICE_SL_V1"
SL_D_workflow = "/workflow_engine/startJobWithOptions/LNAAS_DELETE_DIA_SERVICE_SL_V1"
SL_DUNI_workflow = "/workflow_engine/startJobWithOptions/LNAAS_DELETE_UNI_SL_V1"
SL_DOnline_workflow ="/workflow_engine/startJobWithOptions/LNAAS_DELETE_OLINE_PATH_ASRI_TL_V2"
mesh_path = "/inventory/v1/mesh/paths?aend=LABBRMCO&product=ETHERNET&numpaths=1&bandwidth=100&diversity=No&interface=Optical&protection=No&productType=simple_ethernet&lowLatency=No&dwdmOnly=No&metroLevel=2.0"
workflow_status = "/workflow_engine/getJobShallow/"
workflow_search = "/workflow_engine/tasks/search"
workflow_searchV2 = "/workflow_engine/getJobList/complete"
sasi_asri = "/wrappers/asri/naming/generate"
assign_ip ="/wrappers/nisws/ipAssign"
release_ip="/wrappers/nisws/ipRelease"
get_asri ="/inventory/v1/asri/services?name="