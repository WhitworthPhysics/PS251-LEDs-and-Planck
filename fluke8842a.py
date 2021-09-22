import time

class Fluke8842A:
    def __init__(self, resource_manager, visa_addr):
        # Connect to instrument
        self.instr = resource_manager.open_resource(visa_addr)

        # Verify that this is a Fluke 8842A
        id_string = self.instr.query('G8')
        if ('FLUKE' in id_string) and ('8842A' in id_string):
            print("Connection to Fluke 8842A successful")
        else:
            self.instr.close()
            raise Exception("Failed to connect to a Fluke 8842A")

    def __del__(self):
        self.close()

    def close(self):
        self.instr.close()

    def get_reading(self):
        result = self.instr.query('?')
        return float(result)

    def set_mode(self, mode):
        if (mode == 'V DC'):
            self.instr.write('F1')
        elif (mode == 'V AC'):
            self.instr.write('F2')
        elif (mode == 'mA DC'):
            self.instr.write('F5')
        elif (mode == 'mA AC'):
            self.instr.write('F6')
        elif (mode == '2 wire'):
            self.instr.write('F3')
        elif (mode == '4 wire'):
            self.instr.write('F4')
        else:
            print('Mode not recognized. Valid modes are:')
            print('    "V DC", "V AC", "mA DC", "mA AC", "2 wire", and "4 wire"')

    def set_volt_range(self, code):
        if (code == 'auto'):
            self.instr.write('R0')
        elif (code == '20 mV'):
            self.inst.write('R8')
        elif (code == '200 mV'):
            self.instr.write('R1')
        elif (code == '2 V'):
            self.instr.write('R2')
        elif (code == '20 V'):
            self.instr.write('R3')
        elif (code == '200 V'):
            self.instr.write('R4')
        elif (code == '2000 V'):
            self.instr.write('R5')
        else:
            print('Range not recognized. Valid range codes are:')
            print('    "auto", "20 mV", "200 mV", "2 V", "20 V", "200 V", and "2000 V"')

    def set_current_range(self, code):
        if (code == 'auto'):
            self.instr.write('R0')
        elif (code == '2000 mA'):
            self.instr.write('R5')
        elif (code == '200 mA'):
            self.instr.write('R4')
        else:
            print('Range not recognized. Valid range codes are:')
            print('    "auto", "200 mA", and "2000 mA"')



  