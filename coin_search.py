import os
from web3 import Web3
import web3
import json
import contracts as contracts

####################################################################################
####                            Declarations                                     ###
####################################################################################



####################################################################################
####                            Functions
####################################################################################


def get_balance(address):
	balance = int(w3.eth.get_balance(Web3.toChecksumAddress(address), block_identifier='latest'))
	return balance

def format_number(number):
    return "{:,}".format(number)

####################################################################################
####                            Script body
####################################################################################

with open("network_data.json") as f:
	network_data = json.load(f)

with open("addresses") as f:
	addresses = f.readlines()

for network, data in network_data.items():
	network_id = data['network_id']
	rpc = data['rpc']
	decimals = int(data['decimals'])
	w3 = Web3(Web3.HTTPProvider(rpc))
	print("------------------------------------------------------------------------")
	for address in addresses:
		address = address.strip()
		balance = get_balance(address)/(10 ** decimals)
		balance_formatted = "{:.6f}".format(balance)
		short_address = address[:6] + "..." + address[-4:]
		print(f"Network: {network} Address: {short_address} has balance: {balance_formatted} {network}")
		if network_id==1 or network_id==10001 or network_id==513100:
			hedron_contract = w3.eth.contract(address = contracts.hedron_address , abi = contracts.abi_hedron)
			hedron_balance = hedron_contract.functions.balanceOf(address).call()
			print("    Account Balance: ",format_number(round((hedron_balance/10e9),2))," HDRN")
			icsa_contract = w3.eth.contract(address = contracts.icsa_address , abi = contracts.abi_icsa)
			icsa_balance = icsa_contract.functions.balanceOf(address).call()
			print("    Account Balance: ",format_number(round(icsa_balance/10e8,2))," ICSA")			
	print("------------------------------------------------------------------------")