import pyvisa

asrl_device_library = [
  {'baud': 57600, 'read_term': '\r\n', 'write_term': '\r\n', 'id_query': '*IDN?'}, # BK powers supplies
  {'baud': 9600, 'read_term': None, 'write_term': None, 'id_query': '*IDN?'} # BK multimeter
]

gpib_device_library = [
  {'baud': 9600, 'read_term': '\n', 'write_term': '\n', 'id_query': 'G8'} # Fluke 8842A
]

def instrument_scan():
  rm = pyvisa.ResourceManager()
  addr_list = rm.list_resources('?*::INSTR')
  instruments = []
  for addr in addr_list:
    try:
      instr = rm.open_resource(addr)
      dev_info = None
      if 'GPIB' in addr:
        dev_lib = gpib_device_library
      else:
        dev_lib = asrl_device_library

      for dev_type in dev_lib:
        instr.baud_rate = dev_type['baud']
        instr.read_termination = dev_type['read_term']
        instr.write_termination = dev_type['write_term']
        try:
          id = instr.query(dev_type['id_query']).split(",")
        except pyvisa.errors.VisaIOError:
          id = None
        if id:
          dev_info = {'addr': addr,
                      'manufacturer': id[0],
                      'model': id[1],
                      'baud': dev_type['baud'],
                      'read_term': dev_type['read_term'],
                      'write_term': dev_type['write_term']
                    }
          break
      if dev_info:
        instruments.append(dev_info)
      instr.close()
    except:
      pass
  return instruments
