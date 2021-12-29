#!/usr/bin/python3
import time
import argparse
from argparse import RawTextHelpFormatter
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils


parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('-i', '--ip-address', action='store', dest='ip_opt', required=True, help='IP address for the EmonDmon being queried', metavar='ip-addr')
exclusive_group = parser.add_mutually_exclusive_group(required=True)
exclusive_group.add_argument('-a', '--all', action='store_true', dest='all_data_opt', help='Get all data from device')
exclusive_group.add_argument('-g', '--graph', action='store', type=int, dest='graph_opt', choices=range(1, 11), metavar='(n)',
help="""Get data for a specific graph (1,2,3,4,5,6,7,8,9,10)
1) Voltage Line to N
        - Voltage Combined
        - Voltage A-N
        - Voltage B-N
        - Voltage C-N
2) Voltage Line to Line
        - Voltage Combined
        - Voltage A-B
        - Voltage B-C
        - Voltage C-A
3) KW Load
        - Delivered (Energy in from grid)
        - Received (Energy out to grid)
4) Power Factor
        - Combined
        - Leg A
        - Leg B
        - Leg C
5) Amperage
        - Combined
        - Leg A
        - Leg B
        - Leg C
6) Frequency
        - Frequency
7) Power Combined
        - Real Power
        - Reactive Power
        - Apparent Power
8) Real Power by Leg
        - Leg A
        - Leg B
        - Leg C
9) Reactive Power by Leg
        - Leg A
        - Leg B
        - Leg C
10) Apparent Power by Leg
        - Leg A
        - Leg B
        - Leg C
""")

args = parser.parse_args()

registers = {
	'volt-12n':1020,
	'volt-a2n':1058,
	'volt-b2n':1060,
	'volt-c2n':1062,
	'volt-121':1022,
	'volt-a2b':1064,
	'volt-b2c':1066,
	'volt-c2a':1068,
	'load-d':1000,
	'load-r':1002,
	'pf':1014,
	'pf-a':1046,
	'pf-b':1048,
	'pf-c':1050,
	'amp':1018,
	'amp-a':1052,
	'amp-b':1054,
	'amp-c':1056,
	'freq':1024,
	'pwr-real':1008,
	'pwr-reac':1010,
	'pwr-appa':1012,
	'pwr-real-a':1028,
	'pwr-real-b':1030,
	'pwr-real-c':1032,
	'pwr-reac-a':1034,
	'pwr-reac-b':1036,
	'pwr-reac-c':1038,
	'pwr-appa-a':1040,
	'pwr-appa-b':1042,
	'pwr-appa-c':1044
}
graphs = {
	1:['volt-12n', 'volt-a2n', 'volt-b2n', 'volt-c2n'],
	2:['volt-121', 'volt-a2b', 'volt-b2c', 'volt-c2a'],
	3:['load-d', 'load-r'],
	4:['pf', 'pf-a', 'pf-b', 'pf-c'],
	5:['amp', 'amp-a', 'amp-b', 'amp-c'],
	6:['freq'],
	7:['pwr-real', 'pwr-reac', 'pwr-appa'],
	8:['pwr-real-a', 'pwr-real-b', 'pwr-real-c'],
	9:['pwr-reac-a', 'pwr-reac-b', 'pwr-reac-c'],
	10:['pwr-appa-a', 'pwr-appa-b', 'pwr-appa-c']
}

def ReadEmonDmon(conn, register):
	"""Queries a Emon-Dmon endpoint and returns two registers (32 bit) of data formated as a float
	Args:
		conn (obj): The connection to the modbus device established prior
		register (int): The modbus address being queried
	Retun:
		float: data from queried register
	"""
	data = conn.read_holding_registers(register, 2)
	if data:
		return utils.decode_ieee(utils.word_list_to_long(data)[0])
	else:
		print(f"Did not find any data at address {register}")
		return None

def main(args, registers, graphs):
	"""If all_data cli option is set, query and print all values from modbus device. Else query and print all values for specified graph
	Args:
		args (class): Arguments taken from command line
		registers (dict): modbus addresses to data
		graphs (dict): lists of modbus addresses related to a specific graph
	"""
	c = ModbusClient(args.ip_opt, port=502, auto_open=True, unit_id=1)
	if not c.is_open():
		if not c.open():
			print("can not connect to Emod-Dmon device")
			return None
	if args.all_data_opt:
		for k, v in registers.items():
			print(f"{k}: {ReadEmonDmon(c, v)}")
			time.sleep(.5) # important as modbus implementations sometimes choke with too many queries in quick succession
	else:
		data_list = []
		for k in graphs[args.graph_opt]:
			data = f"{k}:{ReadEmonDmon(c, registers[k])}"
			data_list.append(data)
		print(*data_list)
	c.close()

if __name__ == "__main__":
    main(args, registers, graphs)


