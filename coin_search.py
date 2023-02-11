import os
from web3 import Web3
import json
import contracts as contracts
import requests
import ctypes
import time
libgcc_s = ctypes.CDLL('libgcc_s.so.1')
from threading import Thread

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

def get_icsa_stake(address):
	icsa_stake= icsa_contract.functions.icsaStakes(address).call()

def get_hdrn_stake(address):
	hedron_stake= icsa_contract.functions.hdrnStakes(address).call()

def calc_days_to_end_HdrnIcsa_stake(contract,address,current_day):
	icsa_stake = contract.functions.icsaStakes(address).call()
	hdrn_stake = contract.functions.hdrnStakes(address).call()
	
	if icsa_stake[3]==True:
		minStakeLengthIcsa=icsa_stake[7]
		capitalAddedIcsa=icsa_stake[1]
		days_to_end_icsa_stake=minStakeLengthIcsa-(current_day-capitalAddedIcsa)
		if days_to_end_icsa_stake>= 0:
			print(f"Days to end ICSA stake: {days_to_end_icsa_stake}")
		else:
			printf(f"ICSA stake ended: {-days_to_end_icsa_stake} days ago !!!!!!!!!!")
	if hdrn_stake[3]==True:
		minStakeLengthHdrn=hdrn_stake[7]
		capitalAddedHdrn=hdrn_stake[1]
		days_to_end_hdrn_stake=minStakeLengthHdrn-(current_day-capitalAddedHdrn)
		if days_to_end_hdrn_stake>= 0:
			print(f"Days to end HDRN stake: {days_to_end_hdrn_stake}")
		else:
			print(f"HDRN stake ended: {-days_to_end_hdrn_stake} days ago !!!!!!!!!!")

def get_dict_from_hex_stake(hex_stake):
	stake = {
		"stake_id":int(hex_stake[0]),
		"Hex_staked":(round(hex_stake[1]/10**8,2)),		
		"T-shares":round(hex_stake[2]/10**12,2),
		"stake_start_on_hex_day":int(hex_stake[3]),
		"stake_days":int(hex_stake[4]),
		"stake_ends_in_days":0
	}
	return(stake)


def stake_find(*args):
	address=args[0]
	hsiIndex=args[1]-1
	stake_type=args[2]
	if stake_type==2:
		token_id=hsi_contract.functions.tokenOfOwnerByIndex(address,hsiIndex).call()
		hsi_address = hsi_contract.functions.hsiToken(token_id).call()
		stake = hex_contract.functions.stakeLists(hsi_address,0).call()	
	if stake_type==1:
		hsi_address = hsi_contract.functions.hsiLists(address,hsiIndex).call()
		stake = hex_contract.functions.stakeLists(hsi_address,0).call()
	elif stake_type==0:
		stake=hex_contract.functions.stakeLists(address,hsiIndex).call()
	stake_dict=get_dict_from_hex_stake(stake)
	days_to_end=calc_days_to_end_HexStake(stake_dict)
	stake_dict['stake_ends_in_days']=days_to_end
	if stake_type==2:
		stakes_tokenized.append(stake_dict)	
	elif stake_type==1:
		stakes_hsi.append(stake_dict)
	elif stake_type==0:
		stakes_native.append(stake_dict)

def get_Stakes_threads(hex_contract,hsi_contract,address):
	#stakes_count=hsi_contract.functions.stakeCount(address).call()
	hsi_count=hsi_contract.functions.hsiCount(address).call()
	native_count=hex_contract.functions.stakeCount(address).call()
	tokenized_count=hsi_contract.functions.balanceOf(address).call()
	print(f"amount of native stakes: {native_count}")
	threads_native=['1']
	for nativec in range(1,native_count+1,1):
		threads_native.append(Thread(target=stake_find, args=[address,nativec,0]))
		threads_native[nativec].start()
	for nativec in range(1,native_count+1,1):
		threads_native[nativec].join()
	print(f"amount of hsi detokenized stakes: {hsi_count}")
	threads_hsi=['1']
	for hsic in range(1,hsi_count+1,1):
		threads_hsi.append(Thread(target=stake_find, args=[address,hsic,1]))
		threads_hsi[hsic].start()
	for hsic in range(1,hsi_count+1,1):
		threads_hsi[hsic].join()
	print(f"amount of hsi tokenized stakes: {tokenized_count}")
	threads_tokenized=['1']
	for tokenizedc in range(1,tokenized_count+1,1):
		threads_tokenized.append(Thread(target=stake_find, args=[address,tokenizedc,2]))
		threads_tokenized[tokenizedc].start()
	for tokenizedc in range(1,tokenized_count+1,1):
		threads_tokenized[tokenizedc].join()

def calc_days_to_end_HexStake(hex_stake_dict):
	hex_stake_end_on_day=hex_stake_dict['stake_start_on_hex_day']+hex_stake_dict['stake_days']
	days_till_hex_stake_end = hex_stake_end_on_day-current_hex_day-1
	return(days_till_hex_stake_end)

def get_balance_hedron(*args):
	balances[0]=hedron_contract.functions.balanceOf(args[0]).call()

def get_balance_icsa(*args):
	balances[1]=icsa_contract.functions.balanceOf(args[0]).call()

def get_balance_hex(*args):
	balances[2]=hex_contract.functions.balanceOf(args[0]).call()

def get_HDRN_ICSA_HEX_balances(address):
	threads_balance=['1']
	threads_balance.append(Thread(target=get_balance_hedron, args=[address]))
	threads_balance.append(Thread(target=get_balance_icsa, args=[address]))
	threads_balance.append(Thread(target=get_balance_hex, args=[address]))
	threads_balance[1].start()
	threads_balance[2].start()
	threads_balance[3].start()
	threads_balance[1].join()
	threads_balance[2].join()
	threads_balance[3].join()

####################################################################################
####                            Script body
####################################################################################

with open("network_data.json") as f:
	network_data = json.load(f)

with open("addresses") as f:
	addresses = f.readlines()



balances=[0,0,0]

list_networks_adresses=[]


for network, data in network_data.items():
	network_id = data['network_id']
	rpc = data['rpc']
	decimals = int(data['decimals'])
	w3 = Web3(Web3.HTTPProvider(rpc))
	hedron_contract = w3.eth.contract(address = contracts.hedron_address , abi = contracts.abi_hedron)
	hedron_decimals=hedron_contract.functions.decimals().call()
	icsa_contract = w3.eth.contract(address = contracts.icsa_address , abi = contracts.abi_icsa)
	icsa_decimals=icsa_contract.functions.decimals().call()
	hex_contract = w3.eth.contract(address = contracts.hex_address , abi = contracts.abi_hex)
	hex_decimals=hex_contract.functions.decimals().call()
	hsi_contract = w3.eth.contract(address = contracts.hsi_address , abi = contracts.abi_hsi)
	current_hex_day= hex_contract.functions.currentDay().call()
	current_hdrn_day= icsa_contract.functions.currentDay().call()
	print(f"-------------------------------------{network}-----------------------------------")
	for address in addresses:
		stakes_native=[]
		stakes_hsi=[]
		stakes_tokenized=[]		
		try:
			address = address.strip()
			address = Web3.toChecksumAddress(address)
			balance = get_balance(address)/(10 ** decimals)
			balance_formatted = "{:.6f}".format(balance)
			short_address = address[:6] + "..." + address[-4:]
			print("")
			print(f"Address: {short_address} has balance:")
			print(f"{network} : {balance_formatted}")
			if network_id==1 or network_id==10001 or network_id==513100 or network_id==942:
				get_HDRN_ICSA_HEX_balances(address)
				hedron_balance=balances[0]
				icsa_balance=balances[1]
				hex_balance=balances[2]
				print(f"HDRN: {format_number(round((hedron_balance/10**(hedron_decimals)),2))}")
				print(f"ICSA: {format_number(round(icsa_balance/10**(icsa_decimals),2))}")
				print(f"HEX: {format_number(round(hex_balance/10**(hex_decimals),2))}")
				get_Stakes_threads(hex_contract,hsi_contract,address)
				print("\nnative stakes:")
				for stake in stakes_native:
					if stake['stake_ends_in_days']>0:
						print(f"{stake}")
					else:
						print(f"{stake} stake already ended in:{-stake['stake_ends_in_days']} days !!!!!!")
				print("\nhsi stakes:")
				for stake in stakes_hsi:
					if stake['stake_ends_in_days']>0:
						print(f"{stake}")
					else:
						print(f"{stake} stake already ended in:{-stake['stake_ends_in_days']} days !!!!!!")
				print("\ntokenized stakes:")
				for stake in stakes_tokenized:
					if stake['stake_ends_in_days']>0:
						print(f"{stake}")
					else:
						print(f"{stake} stake already ended in:{-stake['stake_ends_in_days']} days !!!!!!")						
				print("")
				calc_days_to_end_HdrnIcsa_stake(icsa_contract,address,current_hdrn_day)
		except Exception as err:
			print("exception error : ",err)
	print("")
