import json
from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.wallet import Wallet, generate_faucet_wallet
from utils import load_wallet_from_json

# Create a client to connect to the XRP Ledger Testnet
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# Load the saved wallet (wallet1)
wallet1 = load_wallet_from_json("wallets/wallet1.json")

# Generate another wallet (wallet2) using the testnet faucet
wallet2 = load_wallet_from_json("wallets/wallet2.json")

# Display wallet information
print(f"Wallet1 Address: {wallet1.classic_address}")
print(f"Wallet2 Address: {wallet2.classic_address}")

# Check the initial balances of the two wallets
print("Initial balances of wallets:")
balance1 = get_balance(wallet1.classic_address, client)
balance2 = get_balance(wallet2.classic_address, client)
print(f"Wallet1 Balance: {balance1} XRP")
print(f"Wallet2 Balance: {balance2} XRP")


'''
# Create a Payment transaction from wallet1 to wallet2
payment_tx = Payment(
    account=wallet1.classic_address,
    amount="1000",  # 1000 drops = 0.001 XRP
    destination=wallet2.classic_address,
)

# Submit the payment and wait for validation
payment_response = submit_and_wait(payment_tx, client, wallet1)
print("Transaction was submitted successfully.")

# Check the transaction hash
tx_hash = payment_response.result["hash"]
print(f"Transaction hash: {tx_hash}")

# Check the balances after the transaction
print("Balances of wallets after Payment transaction:")
balance1_after = get_balance(wallet1.classic_address, client)
balance2_after = get_balance(wallet2.classic_address, client)
print(f"Wallet1 Balance: {balance1_after} XRP")
print
'''