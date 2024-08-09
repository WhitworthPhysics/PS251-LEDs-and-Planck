import time

class BKPowerSupply:
    def __init__(self, resource_manager, visa_addr):
        # Connect to instrument
        self.instr = resource_manager.open_resource(visa_addr)
        self.instr.read_termination = '\r\n'
        self.instr.write_termination = '\r\n'
        self.instr.baud_rate = 57600

        # Verify that this is a supported BK power supply
        id_string = self.instr.query('*IDN?').split(",")
        if 'B&K PRECISION' in id_string[0].upper():
            if '9172' in id_string[1]:
                self.model = '9172'
            elif '1697B' in id_string[1]:
                self.model = '1697B'
            else:
                raise Exception(f"Model {id_string[1]} is not supported")
            print(f"Connection to BK {self.model} successful")
        else:
            raise Exception("Failed to connect to a BK power supply")

        # Turn off the beep
        if self.model == '9172':
            self.instr.write('SYS:BEEP OFF')
            self.cmd_wait = 0.01
            self.output_on_str = 'OUT ON'
            self.output_off_str = 'OUT OFF'
            self.output_state_str = 'OUT?'
            self.output_state_on_val = '1'
            self.set_current_lim_str = 'OUT:LIM:CURR %.3f'
            self.set_voltage_str = 'SOUR:VOLT %.3f'
            self.set_current_str = 'SOUR:CURR %.3f'
            self.set_current_min = 0.001
            self.get_current_str = 'MEASURE:CURRENT?'
            self.get_current_units = False
            self.get_voltage_str = 'VOUT?'
            self.get_voltage_units = False
            self.supports_slew_rate = True
            self.slew_rate_max = 7.00
            self.slew_rate_min = 0.01
            self.slew_rate_str = 'OUT:SR:VOLT %.3f'
        elif self.model == '1697B':
            self.cmd_wait = 0.01
            self.output_on_str = 'OUTPUT 0'
            self.output_off_str = 'OUTPUT 1'
            self.output_state_str = 'OUTPUT?'
            self.output_state_on_val = '0'
            self.set_current_lim_str = 'CURR:LIM %.3fA'
            self.set_voltage_str = 'VOLT %.3fV'
            self.set_current_str = 'CURR %.3fA'
            self.set_current_min = 0
            self.get_current_str = 'MEASURE:CURRENT?'
            self.get_current_units = True
            self.get_voltage_str = 'MEASURE:VOLTAGE?'
            self.get_voltage_units = True
            self.supports_slew_rate = False
            self.slew_rate_max = None
            self.slew_rate_min = None
            self.slew_rate_str = None

    def enable(self, enable_output):
        if enable_output:
            self.instr.write(self.output_on_str)
        else:
            self.instr.write(self.output_off_str)
        time.sleep(self.cmd_wait)

    def get_output_state(self):
        resp = self.instr.query(self.output_state_str)
        return resp == self.output_state_on_val

    def set_current_limit(self, max_current):
        self.instr.write(self.set_current_lim_str % max_current)
        time.sleep(self.cmd_wait)
    
    def set_voltage(self, voltage):
        self.instr.write(self.set_voltage_str % voltage)
        time.sleep(self.cmd_wait)

    def set_current(self, current):
        if (current < self.set_current_min):
            current = self.set_current_min
        self.instr.write(self.set_current_str % current)
        time.sleep(self.cmd_wait)
    
    def get_current(self):
        result = self.instr.query(self.get_current_str)
        if self.get_current_units:
            result = result[:-1]
        return float(result)

    def get_voltage(self):
        result = self.instr.query(self.get_voltage_str)
        if self.get_voltage_units:
            result = result[:-1]
        return float(result)
    
    def set_slew_rate(self, slew_rate):
        if self.supports_slew_rate:
            if slew_rate == 'MAX':
                slew_rate = self.slew_rate_max
            if slew_rate == 'MIN':
                slew_rate = self.slew_rate_min
            self.instr.write(self.set_slew_rate_str % slew_rate)
            time.sleep(self.cmd_wait)
        else:
            raise Exception('Slew rate cannot be set on this power supply.')

    def close(self):
        time.sleep(self.cmd_wait) # delay to give time for previous command to finish
        self.instr.close()

    def __del__(self):
        self.close()



