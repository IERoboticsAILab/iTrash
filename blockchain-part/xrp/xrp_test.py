from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models import Payment, Tx
from xrpl.transaction import submit_and_wait
from xrpl.wallet import generate_faucet_wallet

# Create a client to connect to the test network
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Create two wallets to send money between on the test network
#wallet1 = 'r9ChPwe68WrXxmCVbB7t7uiJEqu814PMs3' #generate_faucet_wallet(client, debug=True)
wallet2 = generate_faucet_wallet(client, debug=True)

print("Wallet1: ", wallet2)

#print private key of wallet1


'''
# Both balances should be zero since nothing has been sent yet
print("Balances of wallets before Payment tx")
print(get_balance(wallet1.address, client))
print(get_balance(wallet2.address, client))

# Create a Payment transaction from wallet1 to wallet2
payment_tx = Payment(
    account=wallet1.address,
    amount="1000",
    destination=wallet2.address,
)

# Submit the payment to the network and wait to see a response
#   Behind the scenes, this fills in fields which can be looked up automatically like the fee.
#   It also signs the transaction with wallet1 to prove you own the account you're paying from.
payment_response = submit_and_wait(payment_tx, client, wallet1)
print("Transaction was submitted")

# Create a "Tx" request to look up the transaction on the ledger
tx_response = client.request(Tx(transaction=payment_response.result["hash"]))

# Check whether the transaction was actually validated on ledger
print("Validated:", tx_response.result["validated"])

# Check balances after 1000 drops (.001 XRP) was sent from wallet1 to wallet2
print("Balances of wallets after Payment tx:")
print(get_balance(wallet1.address, client))
print(get_balance(wallet2.address, client))

'''