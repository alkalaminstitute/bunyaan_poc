import socket
import sys
import os
import json
import types
from pip._vendor import requests
from urllib import request
from uuid import uuid4
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from Crypto.PublicKey import RSA
from datetime import datetime
from blockchain.modules.Transaction import Transaction  # New
from blockchain.modules.Blockchain import Blockchain
from blockchain.modules.Block import Block
from blockchain.modules.MusharakSmartContract import MusharakSmartContract
from blockchain.modules.Lender import Lender
from blockchain.modules.Property import Property
from blockchain.modules.ScTransaction import ScTransaction
from django.urls import path
from django.urls import re_path as url


# Creating our Blockchain
blockchain = Blockchain()


def generate_keys():

    keyFileExists = True
    keyPair = None
    # If blockchain keyPair already exists locally
    # Then return it
    # If blockchain keyPair does not exist
    # Then create one and save it in the file system
    try:
        # Retrieving keyPair from file if creatd before

        modules_file = open("blockchain_module_n.txt", "r")
        modules = int(modules_file.read())

        pubExp_file = open("blockchain_public_e.txt", "r")
        pubExp = int(pubExp_file.read())

        privExp_file = open("blockchain_private_e.txt", "r")
        privExp = int(privExp_file.read())

        # reconstructing the keyPair from keyPair.n, keyPair.ed and keyPair.d
        keyPair = RSA.construct((modules, pubExp, privExp))

    except:
        keyFileExists = False
        print("NO SUCH FILE")

    if (not keyFileExists):
        keyPair = RSA.generate(1024)

        # Saving the modules (keyPair.n), Public exponent e (keyPair.e) and
        # Private exponent d (keyPair.d) to file so we don't create keyPair everytime
        modules = keyPair.n
        file_out = open("blockchain_module_n.txt", "w")
        file_out.write(str(modules))
        file_out.close

        public_key_com = keyPair.e
        file_out = open("blockchain_public_e.txt", "w")
        file_out.write(str(public_key_com))
        file_out.close

        private_key_com = keyPair.d
        file_out = open("blockchain_private_e.txt", "w")
        file_out.write(str(private_key_com))
        file_out.close

    # print(keyPair)
    return keyPair

    # return key.publickey().export_key().decode('ASCII')


keyPair = generate_keys()
publicKey = keyPair.publickey().exportKey("PEM").decode()

# get running server url

prefix_url = "http://"
server_url = socket.gethostbyname('localhost')
server_port = sys.argv[-1]
node_address = server_url+":"+server_port
full_url = prefix_url + node_address
print(full_url)

# add blockchain to peer-to-peer network
my_url = {
    # will also add the public_key/wallet_key of this node for testing purposes
    "nodes": [[node_address, publicKey]]
}

# print(my_url)

blockchain.nodes.add(node_address)
wallet_addresses = set()
wallet_addresses.add(publicKey)

if (int(server_port) != 8000):
    response = requests.post(
        f'http://127.0.0.1:8000/connect_node', json=my_url)
    # print("POST RESPONSE")
    received_json = response.json()
    blockchain_nodes = received_json.get('blockchain_nodes')
    master_pk = received_json.get('my_pk')
    wallet_addresses.add(master_pk)
    # print(blockchain_nodes[0])
    for adr in wallet_addresses:
        wallet_addresses.add(adr)
    for node in blockchain_nodes:
        blockchain.add_node(node)
    blockchain.replace_chain()


def object_tojson(ob):
    t = {}
    func = None
    if hasattr(ob, "func"):
        # print(ob.func.__name__)
        t["func"] = ob.func.__name__
    for field in filter(lambda a: not a.startswith('__'), dir(ob)):
        attribute = getattr(ob, field)
        if (not callable(attribute)):
            if type(attribute) is Property:
                t[str(field)] = object_tojson(attribute)
                # print("PROPERTY CHANGED")
            elif type(attribute) is list:
                # print("LENDER CHANGED")
                lenders = []
                for lender in attribute:
                    lnd = object_tojson(lender)
                    lenders.append(lnd)
                t[str(field)] = lenders
            else:
                t[str(field)] = attribute
    return t

# Mining a new block


def get_wallets(request):
    if request.method == 'GET':
        response = {'wallets': list(wallet_addresses)}
    return JsonResponse(response)


@csrf_exempt
def mine_block(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        block = blockchain.mine_pending_txs(received_json.get('miner_address'))

        transactions = []
        for tx in blockchain.pending_transactions:
            t = object_tojson(tx)
            transactions.append(t)

        # transactions = []
        # for tx in block.data:
        #     transactions.append(tx.json_encode())
        response = {'message': 'Congratulations, you just mined a block!',
                    'timestamp': block.timestamp,
                    'nonce': block.nonce,
                    'previous_hash': block.previous_hash,
                    'data': transactions,
                    'hash': block.hash}
        blockchain.pending_transactions = []
    return JsonResponse(response)

# Getting the full Blockchain


def get_chain(request):
    if request.method == 'GET':
        chain_json = []
        for bl in blockchain.chain:
            if (type(bl) is dict):
                chain_json.append(bl)
            else:
                if bl.data == "Genesis block" or len(bl.data) == 0:
                    block = {
                        'timestamp': bl.timestamp,
                        'data': "Genesis block",
                        'previous_hash': bl.previous_hash,
                        'nonce': bl.nonce,
                        'hash': bl.hash
                    }
                    # block = object_tojson(bl)
                    chain_json.append(block)
                else:
                    txs = []
                    for tx in bl.data:
                        if str(type(tx)) == "<class 'str'>":
                            continue
                        if (type(tx) is dict):
                            t = tx
                        else:
                            t = object_tojson(tx)
                        txs.append(t)
                    block = {
                        'timestamp': bl.timestamp,
                        'data': txs,
                        'previous_hash': bl.previous_hash,
                        'nonce': bl.nonce,
                        'hash': bl.hash
                    }
                    chain_json.append(block)

        p_tx = []
        for tx in blockchain.pending_transactions:
            if str(type(tx)) == "<class 'str'>":
                continue
            if (type(tx) is dict):
                t = tx
            else:
                t = object_tojson(tx)
            p_tx.append(t)

        response = {'chain': chain_json,
                    'public_key': publicKey,
                    'pending_transactions': p_tx,
                    'mining_reward': blockchain.mining_reward,
                    'difficulty': blockchain.difficulty,
                    'length': len(blockchain.chain)}

    return JsonResponse(response)

# Get balance


@csrf_exempt
def get_wallet_balance(request):
    received_json = json.loads(request.body)
    transaction_keys = ['wallet_address']

    if not all(key in received_json for key in transaction_keys):
        return 'Some elements of the transaction are missing', HttpResponse(status=400)

    wallet_address = received_json.get('wallet_address')
    wallet_balance = blockchain.get_balance(wallet_address)

    response = {'wallet_balance': wallet_balance}

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

        sender = received_json.get('sender')
        receiver = received_json.get('receiver')
        amount = received_json.get('amount')

        transaction = Transaction(
            sender,
            receiver,
            amount)

        transaction.sign_transaction(keyPair)

        blockchain.add_transaction(transaction)
        tx_block_index = len(blockchain.chain)
        response = {
            'message': f'This transaction will be added to Block {tx_block_index}'}
    return JsonResponse(response)


@csrf_exempt
def add_smartcontract(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        transaction_keys = ['wallet_address',
                            'address', 'price', 'downpayment', 'seller']

        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)

        #address, price, seller
        property = Property(received_json.get('address'),
                            int(received_json.get('price')),
                            received_json.get('seller'))

        sc_key_pair = RSA.generate(1024)

        # index, sc_key_pair, borrower_sender, property,
        # loan_requested, downpayment,
        # print("TEEEEEEST")
        # print(received_json.get('wallet_address'))
        transaction = MusharakSmartContract(
            len(blockchain.chain),
            len(blockchain.pending_transactions),
            sc_key_pair.publickey().exportKey("PEM").decode(),
            received_json.get('wallet_address'),
            property,
            int(received_json.get('downpayment')))

        transaction.sign_transaction(keyPair)

        blockchain.add_transaction(transaction)

        contract_tx_index = len(blockchain.pending_transactions)-1
        # An assumption is being made here that the transaction will be mined in
        # the next block
        contract_block_index = len(blockchain.chain)
        response = {
            'contract_tx_index': contract_tx_index,
            'contract_block_index': contract_block_index}
    return JsonResponse(response)

# Connecting new nodes


def get_smartcontract(request):
    if request.method == 'GET':
        contract_block_index = int(request.GET.get('block_index'))
        contract_tx_index = int(request.GET.get('tx_index'))
        # received_json = json.loads(request.params)
        # transaction_keys = ['contract_block_index',
        #                     'contract_tx_index']

        # if not all(key in received_json for key in transaction_keys):
        #     return 'Some elements of the transaction are missing', HttpResponse(status=400)

        block = blockchain.chain[contract_block_index]
        sc = block.data[contract_tx_index]

        response = {'borrower': sc.sender,
                    'loan_requested': sc.loan_requested,
                    'loan_remaining': sc.loan_remaining,
                    'balance': sc.balance,
                    'property': sc.property.address}

        return JsonResponse(response)


def get_musharak_scs(request):
    if request.method == 'GET':
        txs = []
        for bl in blockchain.chain:
            if type(bl) is dict:
                for tx in bl['data']:
                    if "property" in tx.keys():
                        txs.append(tx)
            else:
                for transaction in bl.data:
                    if str(type(transaction)) == "<class 'str'>":
                        continue
                    if (type(transaction) is dict):
                        if "property" in transaction.keys():
                            txs.append(transaction)
                    else:
                        if transaction.receiver is None:
                            t = object_tojson(transaction)
                            t['pending'] = False
                            txs.append(t)

        for tx in blockchain.pending_transactions:
            if tx.receiver is None:
                t = object_tojson(tx)
                t['pending'] = True
                txs.append(t)

        response = {'musharaka_scs': txs,
                    'number': len(txs)}

    return JsonResponse(response)


@csrf_exempt
def pay_rent(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        response_keys = ['contract_block_index',
                         'contract_tx_index']

        if not all(key in received_json for key in response_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)

        bl_idx = received_json.get('contract_block_index')
        sctx_idx = received_json.get('contract_tx_index')

        block = blockchain.chain[int(bl_idx)]
        smartcontract = block.data[int(sctx_idx)]
        rent_transactions = smartcontract.distribute_rent()
        for tx in rent_transactions:
            blockchain.pending_transactions.append(tx)

        response = {'payed': True}

    return JsonResponse(response)


@csrf_exempt
def add_lender_tocontract(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        response_keys = ['lender_wallet_address',
                         'contract_block_index',
                         'contract_tx_index',
                         'loan_amount']

        if not all(key in received_json for key in response_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)

        lender_wallet_address = received_json.get(
            'lender_wallet_address')
        loan_amount = int(received_json.get('loan_amount'))
        bl_idx = received_json.get('contract_block_index')
        sctx_idx = received_json.get('contract_tx_index')

        block = blockchain.chain[int(bl_idx)]
        smartcontract = block.data[int(sctx_idx)]

        # each of these transactions will incurr a transaction fee
        st_add_lender = ScTransaction(bl_idx, sctx_idx, lender_wallet_address,
                                      smartcontract.wallet_address, smartcontract.add_lender)
        st_add_lender.sign_transaction(keyPair)

        st_update_balance = ScTransaction(bl_idx, sctx_idx, lender_wallet_address,
                                          smartcontract.wallet_address, smartcontract.update_balance, loan_amount)
        st_update_balance.sign_transaction(keyPair)

        # add SmartcontractTrans to blockchain so other nodes can excute it as well
        blockchain.pending_transactions.append(st_add_lender)
        blockchain.pending_transactions.append(st_update_balance)

        # When other nodes are synching the block to their blockchain, after adding the new block
        # they should check for all ScTransaction and call the code in them on the right smartcontract

        lender = Lender(lender_wallet_address, loan_amount)
        smartcontract.add_lender(lender)
        smartcontract.update_balance(loan_amount)

        # loan_transaction = Transaction(received_json.get('lender_wallet_address'),
        #                                smartcontract.wallet_address,
        #                                received_json.get('loan_amount'))

        # blockchain.pending_transactions.append(loan_transaction)

        # sc_balance = blockchain.get_balance(
        #     smartcontract.wallet_address) + smartcontract.downpayment

        # sc_lenders =
        # lender = Lender(received_json.get('lender_wallet_address'),
        #                 smartcontract.property.property_id, received_json.get('loan_amount'))

        # smartcontract.lenders.append(lender)
        # smartcontract.loan_granted = + received_json.get('loan_amount')

        # 1. Other than the borrower any wallet_key from which we receive funds
        # can be considered a lender
        # 2. Lenders are send money to the smart contract using regular transaction with
        # their walet key as the from address and the smartcontracts key as the to address
        # this way we can calculate the amount/balance of the SC by calling blockchain's normal
        # get balance method.
        # The challenge with updating sc fields as more grant are received is propogating the updated
        # smartcontract through the blockchain as blockchain nodes are not designed to make updates
        # to old SC transctions and this goes agains a block's/transaction's immutibility.
        # Everytime money is funded into the SC we check to see if the amount has reached the price of
        # the property, if yes the SC will send a notice to the borrower that we are ready for escrow
        # with a link for the escrow company to to provide their wallet_key
        # 4. Once the the SC receives the escrow's wallet_key 3% of the funds are sent to the escrow
        # 5. After a month if non of the conditions are triggered and escrwo confirms, the rest of the funds
        # are sent from the SC to the escrow
        # 6. Now the borrower will have to send rent in the desiganted amount to the SC everymonth
        # 7. Everytime the blockchain detects the SC wallet_key receiving rent it will distribute to
        # lender wallet_keys through new transactions

        response = {
            'amount_remaining': f'{smartcontract.property.price - smartcontract.balance}',
            'loan_granted': f'{smartcontract.balance - smartcontract.downpayment}'}

    return JsonResponse(response)


@csrf_exempt
def initiate_escrow(request):
    # called by escrow agency
    if request.method == 'POST':

        received_json = json.loads(request.body)
        transaction_keys = ['contract_block_index',
                            'contract_tx_index',
                            'escrow_name',
                            'escrow_address']

        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)

        block = blockchain[int(received_json.get('contract_block_index'))]
        smartcontract = block.pending_transaction[int(
            received_json.get('contract_tx_index'))]

        escrow_tx = Transaction(smartcontract.sc_address,
                                received_json.get('escrow_address'),
                                0.03*smartcontract.property.price)
        blockchain.pending_transactions.append(escrow_tx)

        paid_to_escrow = 0.03*smartcontract.property.price

        response = {
            'message': f'The amount paid to escrow is {paid_to_escrow}',
            'date': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
    return JsonResponse(response)


@csrf_exempt
def connect_node(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        nodes_adds = []
        for node in nodes:
            # print("NODES ARE" + node)
            nodes_adds.append(node[0])
            blockchain.add_node(node[0])
            wallet_addresses.add(node[1])
            blockchain.replace_chain()

        # if master broadcast new node to all connected nodes (this will avoid loops)
        # another option would be to return a traversed nodes array which are skipped by the node
        # when broadcasting to avoid loops.
        if int(server_port) == 8000:
            for (i, n) in enumerate(blockchain.nodes):
                # add a check to make sure you skip the running node, the calling node, and the
                # nodes it is connected to, to avoide loops
                if n in nodes_adds or n == node_address:
                    continue
                else:
                    node_url = {
                        "nodes": nodes
                    }
                    res = requests.post(
                        f'http://{n}/connect_node', json=node_url)
                    print("CONNECTING ALL NODES" + res.reason)

        response = {'message': 'All the nodes are now connected. The Bunyaan Blockchain now contains the following nodes:',
                    'blockchain_nodes': list(blockchain.nodes),
                    'wallet_addresses': list(wallet_addresses),
                    "my_pk": publicKey}

    return JsonResponse(response)

# Replacing the chain by the longest chain if needed


def replace_chain(request):  # New
    if request.method == 'GET':
        new_chain = blockchain.replace_chain()
        if len(new_chain) != 0:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain': new_chain}
        else:
            response = {'message': 'All good. The chain is the largest one.',
                        'actual_chain': "current"}
    return JsonResponse(response)
