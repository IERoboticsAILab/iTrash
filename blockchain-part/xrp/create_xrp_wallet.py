import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet

from xrp.utils import save_wallet_to_json



# Create a client to connect to the XRP Ledger Testnet
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")


for i in range(1, 10):
    # Generate a wallet using the testnet faucet
    wallet = generate_faucet_wallet(client, debug=True)

    # Prepare wallet data to be saved
    wallet_data = {
        "seed": wallet.seed,
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "address": wallet.classic_address
    }


    # Save the wallet data to a JSON file
    save_wallet_to_json(wallet, "wallet" + str(i) + ".json")

    print(f"Wallet created and saved to wallet1.json")
    print(f"Wallet Address: {wallet.classic_address}")
