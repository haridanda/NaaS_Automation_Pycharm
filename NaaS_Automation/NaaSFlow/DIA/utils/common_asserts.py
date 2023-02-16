class CommonAsserts():
    def check_mesh_response(self, get_port_Aval_MESH):
        global flag
        flag = False
        result = get_port_Aval_MESH['resources'][0]['pathElements'][0]['type']
        if result in ['ME', 'ENNI']:
            assert get_port_Aval_MESH['resources'][0]['pathElements'][0]['subElements'][0]['aendPort'][
                       'name'] is not None
            attributes = (
            get_port_Aval_MESH['resources'][0]['pathElements'][0]['subElements'][0]['aendPort']['attributes'][0])
            if attributes['name'] == 'Class':
                assert attributes['value'] in ['temp']
                flag = True
        return flag