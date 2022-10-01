import json
from uuid import uuid4
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from Crypto.PublicKey import RSA
from blockchain.modules.Transaction import Transaction  # New
from blockchain.modules.Blockchain import Blockchain


# Creating our Blockchain
blockchain = Blockchain()
# Creating an address for the node running our server

keyPair = RSA.generate(bits=1024)
print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
print(f"Private key: (n={hex(keyPair.n)}, d={hex(keyPair.d)})")

node_address = str(uuid4()).replace('-', '')  # New
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d'  # New

# Mining a new block


@csrf_exempt
def mine_block(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        block = blockchain.mine_pending_txs(received_json.get('miner_address'))

        transactions = []
        for tx in block.data:
            transactions.append(tx.json_encode())
        response = {'message': 'Congratulations, you just mined a block!',
                    'timestamp': block.timestamp,
                    'nonce': block.nonce,
                    'previous_hash': block.previous_hash,
                    'transactions': transactions}
    return JsonResponse(response)

# Getting the full Blockchain


def get_chain(request):
    if request.method == 'GET':
        chain_json = []
        for block in blockchain.chain:
            txs = []
            for tx in block.data:
                # print(str(type(tx)))
                if str(type(tx)) == "<class 'str'>":
                    continue
                t = {
                    'sender': tx.sender,
                    'receiver': tx.receiver,
                    'amount': tx.amount,
                    'time': tx.time,
                    'hash': tx.hash
                }
                txs.append(t)
            bc = {
                'timestamp': block.timestamp,
                'hash': block.hash,
                'prev_hash': block.previous_hash,
                'nonce': block.nonce,
                'transactions': txs
            }
            chain_json.append(bc)
            p_tx = [{'sender': "HARDCODEDTRANSCTION",
                    'receiver': "FORTESTINGPURPOSES",
                     'amount': 20,
                     'time': "12/10/22 08:23:43",
                     'hash': "DFSIFHWNOWIEBNVAPC24034399DFKNCNSC"}]
            for tx in blockchain.pending_transactions:
                t = {
                    'sender': tx.sender,
                    'receiver': tx.receiver,
                    'amount': tx.amount,
                    'time': tx.time,
                    'hash': tx.hash
                }
                p_tx.append(t)

        response = {'chain': chain_json,
                    'pending_transactions': p_tx,
                    'mining_reward': blockchain.mining_reward,
                    'difficulty': blockchain.difficulty,
                    'length': len(blockchain.chain)}

    return JsonResponse(response)

# Checking if the Blockchain is valid


def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'Good: The Blockchain is valid.'}
        else:
            response = {
                'message': 'Bad: The Blockchain is not valid.'}
    return JsonResponse(response)

# Adding a new transaction to the Blockchain


@csrf_exempt
def add_transaction(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        transaction_keys = ['sender', 'receiver', 'amount']

        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)
        print("PRINTING_KEYPAIR")
        print(keyPair)
        transaction = Transaction(
            keyPair.publickey().export_key(),
            received_json.get('receiver'),
            received_json.get('amount'))

        transaction.sign_transaction(keyPair)

        index = blockchain.add_transaction(transaction)
        response = {
            'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)

# Connecting new nodes


@csrf_exempt
def connect_node(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'All the nodes are now connected. The Sudocoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes)}
    return JsonResponse(response)

# Replacing the chain by the longest chain if needed


def replace_chain(request):  # New
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain': blockchain.chain}
        else:
            response = {'message': 'All good. The chain is the largest one.',
                        'actual_chain': blockchain.chain}
    return JsonResponse(response)
