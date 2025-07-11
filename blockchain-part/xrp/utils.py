import json
from xrpl.wallet import Wallet

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
