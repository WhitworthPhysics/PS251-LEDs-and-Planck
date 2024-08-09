import time

class BenchMultimeter:
    def __init__(self, resource_manager, visa_addr):
        # Connect to instrument
        self.instr = resource_manager.open_resource(visa_addr)
        # self.instr.read_termination = '\n'
        # self.instr.write_termination = '\n'
        # self.instr.baud_rate = 9600

        # Verify that this is a supported multimeter
        if 'GPIB' in visa_addr: # this might be a Fluke 8842A
            id_string = self.instr.query('G8')
            if ('FLUKE' in id_string) and ('8842A' in id_string):
                self.model = '8842A'
                print("Connection to Fluke 8842A successful")
            else:
                self.instr.close()
                raise Exception("Failed to connect to a BK multimeter")
        else:
            id_string = self.instr.query('*IDN?').split(",")
            if 'B&K PRECISION' in id_string[0].upper():
                if '2831' in id_string[1]:
                    self.model = '2831'
                else:
                    raise Exception(f"Model {id_string[1]} is not supported")
                print(f"Connection to BK {self.model} successful")
            else:
                self.instr.close()
                raise Exception("Failed to connect to a BK multimeter")

        if self.model == '2831':
            self.cmd_wait = 0.01
            self.supported_modes = {'V DC': 'VOLT:DC',
                                    'V AC': 'VOLT:AC',
                                    'I DC': 'CURR:DC',
                                    'I AC': 'CURR:AC',
                                    'resistance': 'RES',
                                    'frequency': 'FREQ',
                                    'diode': 'DIOD',
                                    'continuity': 'CONT'}
            self.select_mode_string = 'FUNC %s'
            self.select_V_range_depends_on_vtype = True
            self.supported_V_ranges = {'auto': 'AUTO ON',
                                       'max': 'MAX',
                                       '200 mV': 0.2,
                                       '2 V': 2,
                                       '20 V': 20,
                                       '200 V': 200}
            self.select_V_range_float = 'VOLT:%s:RANGE %.3f'
            self.select_V_range_string = 'VOLT:%s:RANGE:%s'
            self.select_I_range_depends_on_ctype = True
            self.supported_I_ranges = {'auto': 'AUTO ON',
                                       '2 mA': 0.002,
                                       '20 mA': 0.02,
                                       '200 mA': 0.2,
                                       '2 A': 2,
                                       '20 A': 20}
            self.support_I_range_by_float = True
            self.select_I_range_float = 'CURR:%s:RANGE %.3f'
            self.select_I_range_string = 'CURR:%s:RANGE:%s'
            self.measure_query = 'MEAS?'
            #### MORE SUPPORTED COMMANDS CAN BE IMPLEMENTED ####
        elif self.model == '8842A':
            self.supported_modes = {'V DC': 'F1',
                        'V AC': 'F2',
                        'I DC': 'F5',
                        'I AC': 'F6',
                        '2 wire': 'F3',
                        '4 wire': 'F4'}
            self.select_mode_string = '%s'
            self.select_V_range_depends_on_vtype = False
            self.supported_V_ranges = {'auto': 'R0',
                                       'max': 'R5',
                                       '20 mV': 'R8',
                                       '200 mV': 'R1',
                                       '2 V': 'R2',
                                       '20 V': 'R3',
                                       '200 V': 'R4'}
            self.select_V_range_float = None
            self.select_V_range_string = '%s'
            self.select_I_range_depends_on_ctype = False
            self.supported_I_ranges = {'auto': 'R0',
                                       '200 mA': 'R4',
                                       '2 A': 'R5'}
            self.support_I_range_by_float = False
            self.select_I_range_float = None
            self.select_I_range_string = '%s'
            self.measure_query = '?'
    

    def __del__(self):
        self.close()
        return None
    
    def close(self):
        self.instr.close()
        return None
    
    def get_reading(self):
        result = self.instr.query(self.measure_query)
        return float(result)
    
    def set_mode(self, mode):
        if mode in self.supported_modes:
            self.mode = mode
            mode_str = self.supported_modes[mode]
            self.instr.write(self.select_mode_string % mode_str)
        else:
            print('Mode not recognized. Valid modes are:')
            print('    %s' % list(self.supported_modes.keys()))

    def set_volt_range(self, code):
        if self.mode == 'V DC':
            vtype = 'DC'
        elif self.mode == 'V AC':
            vtype = 'AC'
        else:
            raise Exception('Voltage range may only be set after setting mode to voltage')
        if code in self.supported_V_ranges:
            code_val = self.supported_V_ranges[code]
            if self.select_V_range_depends_on_vtype:
                fill_in_stuff = (vtype,code_val)
            else:
                fill_in_stuff = code_val
            if isinstance(code_val, str):
                self.instr.write(self.select_V_range_string % fill_in_stuff)
            else:
                self.instr.write(self.select_V_range_float % fill_in_stuff)
        else:
            print('Range not recognized. Valid range codes are:')
            print('    %s' % list(self.supported_V_ranges.keys()))

    def set_current_range(self, code):
        if self.mode == 'I DC':
            ctype = 'DC'
        elif self.mode == 'I AC':
            ctype = 'AC'
        else:
            raise Exception('Current range may only be set after setting mode to current')
        if isinstance(code, (int, float)) and self.support_I_range_by_float:
            if self.select_I_range_depends_on_ctype:
                self.instr.write(self.select_I_range_float % (ctype, code))
            else:
                self.instr.write(self.select_I_range_float % code)
        elif code in self.supported_I_ranges:
            code_val = self.supported_I_ranges[code]
            if self.select_I_range_depends_on_ctype:
                fill_in_stuff = (ctype,code_val)
            else:
                fill_in_stuff = code_val
            if isinstance(code_val, str):
                self.instr.write(self.select_I_range_string % fill_in_stuff)
            else:
                self.instr.write(self.select_I_range_float % fill_in_stuff)
        else:
            print('Range not recognized. Valid range codes are:')
            if self.support_I_range_by_float:
                print('    float equal to maximum expected current (in A) or')
            print('    %s' % list(self.supported_I_ranges.keys()))
 
