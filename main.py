from web3 import Web3
from loguru import logger
from config import *


def claim(wallet: list):

    for privatekey in wallet:
        w3 = Web3(Web3.HTTPProvider(RPC))
        contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)
        address = w3.to_checksum_address(w3.eth.account.from_key(privatekey).address)
        balance = w3.from_wei(w3.eth.get_balance(address), 'ether')
        if balance < 0.000099:
            logger.error(f'insufficient for gas: wallet - {address}')
            continue
        nonce = w3.eth.get_transaction_count(address)

        tx = contract.functions.claim().build_transaction(
                {
                    'chainId': 42161,
                    'from': address,
                    'nonce': nonce,
                    'gasPrice': 100_000_000,
                    'gas': 1_000_000
                }
        )

        signed_tx = w3.eth.account.sign_transaction(tx, privatekey)

        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt['status'] != 1:
                logger.error(f'fail transaction: wallet - {address}, hash - {tx_hash.hex()}')
            else:
                logger.success(f'succes claimed: wallet - {address}, hash - {tx_hash.hex()}')
                with open('success.txt', 'a') as f:
                    f.write(f'{address}:{privatekey}\n')

        except Exception as e:
            logger.error(f'Error {e}: wallet - {address}')


if __name__ == '__main__':
    with open('privatekeys.txt') as file:
        wallets = [wallet.strip() for wallet in file]

    claim(wallets)
