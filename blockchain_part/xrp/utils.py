import json
from xrpl.wallet import Wallet
from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.wallet import Wallet, generate_faucet_wallet

def load_wallet_from_json(file_path):
    with open(file_path, "r") as wallet_file:
        wallet_data = json.load(wallet_file)
    wallet = Wallet(
        seed=wallet_data["seed"],
        public_key=wallet_data["public_key"],
        private_key=wallet_data["private_key"]
    )
    return wallet

def save_wallet_to_json(wallet, file_path):
    wallet_data = {
        "seed": wallet.seed,
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "address": wallet.classic_address
    }
    with open(file_path, "w") as wallet_file:
        json.dump(wallet_data, wallet_file)


def send_xrp(sender, receiver, amount):

    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    # Create a Payment transaction from wallet1 to wallet2
    payment_tx = Payment(
        account=sender.classic_address,
        amount=amount,  # 1000 drops = 0.001 XRP
        destination=receiver.classic_address,
    )

    # Submit the payment and wait for validation
    payment_response = submit_and_wait(payment_tx, client, sender)
    print("Transaction was submitted successfully.")