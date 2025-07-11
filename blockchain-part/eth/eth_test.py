from web3 import Web3

# Conexión con el nodo de Ethereum
web3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545' ))


#print(web3.is_connected())



# Dirección del contrato
owner_address = '0x42606BDddB5AE77F236321838d35735E675E14C4'

#get balance
owner_balance = web3.eth.get_balance(owner_address)
print("Owner balance:" , owner_balance)


# Dirección del propietario

receiver_address = '0x31D32e5BF53A0d7F124B41412493758B521aAe35'
receiver_balance = web3.eth.get_balance(receiver_address)
print("Receiver balance:" , receiver_balance)


#send transaction

tx_hash = web3.eth.send_transaction({
    'from': owner_address,
    'to': receiver_address,
    'value': web3.to_wei(1, 'ether')
})

#print("Transaction hash:", tx_hash)

#wait for transaction to be mined
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

#print("Transaction receipt:", tx_receipt)
print("----------------")
print("TRAANSACTION SENT")
print("----------------")

#check balance

owner_balance = web3.eth.get_balance(owner_address)
print("Owner balance:" , owner_balance)

receiver_balance = web3.eth.get_balance(receiver_address)
print("Receiver balance:" , receiver_balance)


