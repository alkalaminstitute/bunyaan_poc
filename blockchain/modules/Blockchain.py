from datetime import datetime
from pip._vendor import requests
from Crypto.PublicKey import RSA
from urllib.parse import urlparse
from blockchain.modules.Escrow import Escrow
from blockchain.modules.Lender import Lender
from blockchain.modules.MusharakSmartContract import MusharakSmartContract
from blockchain.modules.ScTransaction import ScTransaction
from .Block import Block
from .Transaction import Transaction
from .Property import Property


class Blockchain:

    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []
        self.mining_reward = 10
        self.url = ""
        self.nodes = set()  # New

    def create_genesis_block(self):
        return Block("01/01/2022 8:90:23", "Genesis block")

    def get_last_block(self):
        return self.chain[-1]

    def mine_pending_txs(self, miner_address):

        # First reward the miner, could be done last
        self.pending_transactions.append(Transaction(
            None, miner_address, self.mining_reward))

        # If I successfully mine send reward to miningRewardAddress
        # In a real blockchain there are too many transactions to be put
        # in the same block so miners choose which transactions to include

        block = Block(
            datetime.now().strftime(
                "%m/%d/%Y, %H:%M:%S"),
            self.pending_transactions,
            self.get_last_block().hash
        )

        block.hash = block.calculate_hash()

        block.mine_block(self.difficulty)

        print("Block Successfully Mined")

        # rewarding the miner in the next block
        # If the miner adds extra rewards other nodes in the network will ignore it
        self.pending_transactions = []

        # broadcast to all other nodes
        self.broadcast_block(block)

        self.chain.append(block)

        return block

    def add_transaction(self, transaction):  # New
        if (not transaction.sender):
            raise ValueError('Transacton must include from address')

        is_valid = transaction.is_valid_transaction()

        if (not is_valid):
            raise ValueError('Cannot add invalid transaction to chain')

        self.pending_transactions.append(transaction)

        return "Transaction Added"

    def broadcast_block(self, block):

        count = 0
        block_json = self.object_tojson(block)
        data_json = block_json['data']
        print('data_json')
        print(data_json)

        payload = {
            # ['timestamp', 'data', 'previous_hash', 'hash']
            "timestamp":  block.timestamp,
            "data": data_json,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        }

        for node in self.nodes:
            if (node != self.url):
                url = "http://"+node+"/block_broadcast"
                print("THE URL" + url)
                response = requests.post(
                    url, json=payload)
                # print("POST RESPONSE")
                received_json = response.json()
                block_added = received_json.get('block_added')
                print("noded accepted block")
                print(block_added)

                # response = requests.post(url)
                # response.json()

    def broadcast_pendingtx(self, transaction):
        # broadcast transaction to
        payload = self.object_tojson(transaction)
        for node in self.nodes:
            if (node != self.url):
                url = "http://"+node+"/pendingtx_broadcast"
                print("THE URL" + url)
                response = requests.post(
                    url, json=payload)
                # print("POST RESPONSE")
                received_json = response.json()
                transaction_added = received_json.get('transaction_added')
                print("node accepted block")
                print(transaction_added)

    def is_chain_valid(self, chain):
        # Check if the Genesis block hasn't been tampered with by comparing
        # the output of createGenesisBlock with the first block on our chain
        real_genesis = self.create_genesis_block().json_encode()

        if (real_genesis != self.chain[0].json_encode()):
            print("GNESIS IS NOT VALID")
            return False

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            print("############################")
            print(current_block.data)
            print(current_block.hash)
            print("############################")
            print(previous_block.data)

            if (current_block.hash != current_block.calculate_hash()):
                print('curren is invalid')
                return False

            if (current_block.previous_hash != previous_block.hash):
                print(current_block.previous_hash)
                print(previous_block.hash)
                print('previous is invalid')
                return False

            # Check if all transactions in the current block are valid
            if (not current_block.has_valid_transactions()):
                print('has invalid transactions')
                return False

        return True

    def get_balance(self, wallet_address):
        balance = 1000
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            try:
                for j in range(0, len(block.data)):
                    transaction = block.data[j]
                    if hasattr(transaction, "property"):
                        if (transaction.sender == wallet_address):
                            balance -= int(transaction.downpayment)
                    elif hasattr(transaction, "func"):
                        if (transaction.sender == wallet_address):
                            balance -= int(transaction.amount)
                    else:
                        if (transaction.sender == wallet_address):
                            balance -= int(transaction.amount)
                        if (transaction.receiver == wallet_address):
                            balance += int(transaction.amount)
            except AttributeError:
                print("no transaction")
        return balance

    # lenders are all those who sent money to the SC wallet address
    def get_lenders(self, sc_wallet_address):
        lenders = []
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            try:
                for j in range(0, len(block.data)):
                    transaction = block.data[j]
                    if (transaction.reciever == sc_wallet_address):
                        lenders.append(transaction.sender)
            except AttributeError:
                print("no transaction")
        return lenders

    # def rentPaid():
    # TODO
    # distribute received rent over lenders

    # def rentNotPaid():
    # TODO
    # // distribute rent from borrowers position to lenders
    # // if borrower has not percentage from which rent can be
    # // taken our give the lender the option to sell

    # def sell():
    # TODO
    # // submit the property for sale

    # /*
    # we need pending transactions because we can only make a certain number of
    # transactions on a particular interval. Proof of Work makes sure only one block
    # is created every ten minutes. All other transactions are temporarily stored in this
    # pending transactions array
    #

    def add_node(self, address):  # New
        self.nodes.add(address)
        # parsed_url = urlparse(address)
        # self.nodes.add(parsed_url.netloc)

    def replace_chain(self):  # New
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            print("NODE IS BCHAIN" + str(self.nodes))
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            # TODO convert longest_chain to Blockchian class from json
            self.chain = self.chainJSONdecode(longest_chain)
            return longest_chain
        return {}

    # def execute_sc_transactions(self):
    #     for block in self.chain:
    #         for tx in block.data:
    #             block = self.chain[tx.bl_idx]
    #             smartcontract = block.data[tx.sctx_idx]
    #             if hasattr(tx, "func"):
    #                 if tx.func == "smartcontract.update_balance":
    #                     smartcontract.update_balance(tx.amount)
    #                 elif tx.func == "smartcontract.add_lender":
    #                     smartcontract.add_lender(
    #                         Lender(tx.sender, tx.amount))

    def chainJSONdecode(self, chainJSON):
        chain = []
        for blockJSON in chainJSON:

            # check if block is the Genesis block
            if blockJSON['data'] == "Genesis block" or len(blockJSON['data']) == 0:
                block = Block(blockJSON['timestamp'], "Genesis block")
                block.hash = blockJSON['hash']
                block.previous_hash = blockJSON['previous_hash']
                block.nonce = blockJSON['nonce']
                chain.append(block)
            else:
                tArr = self.json_to_transactions(blockJSON['data'])

                block = Block(blockJSON['timestamp'], tArr)
                print("HASH#####################")
                print(blockJSON['hash'])
                block.hash = blockJSON['hash']
                block.previous_hash = blockJSON['previous_hash']
                block.nonce = blockJSON['nonce']

                chain.append(block)

        return chain

    def json_to_transactions(self, tArrayJSON):

        tArr = []
        for tJSON in tArrayJSON:
            transaction = None
            # Check if it is a smartcontract
            if "property" in tJSON:
                lenders = []
                if (len(tJSON['lenders']) != 0):
                    for lend in tJSON['lenders']:
                        l = Lender(lend['wallet_address'],
                                   int(lend['loaned_amount']))
                        lenders.append(l)

                esc = tJSON['escrow']
                escrow = esc
                if tJSON['escrow'] is not None:
                    escrow = Escrow(
                        esc['name'], esc['wallet_address'], esc['property_id'])

                prop = tJSON['property']
                property = Property(prop['address'],
                                    prop['price'], prop['seller'], prop['rent'])
                property.property_id = prop['property_id']

                transaction = MusharakSmartContract(
                    int(tJSON['bl_idx']),
                    int(tJSON['sctx_idx']),
                    tJSON['wallet_address'],
                    tJSON['sender'], property,
                    int(tJSON['downpayment']),
                    int(tJSON['loan_granted']),
                    lenders, escrow, tJSON['timestamp'])

                transaction.signature = tJSON['signature']
                transaction.hash = tJSON['hash']
            # Check if it is smartcontract transaction
            elif "func" in tJSON:
                block = self.chain[int(tJSON['bl_idx'])]
                smartcontract = block.data[int(tJSON['sctx_idx'])]
                # getting the function using the funcname passed from get_chain
                func = getattr(smartcontract, tJSON['func'])

                transaction = ScTransaction(
                    tJSON['bl_idx'], tJSON['sctx_idx'], tJSON['sender'],
                    tJSON['receiver'], func, int(tJSON['amount']), tJSON['timestamp'])
                transaction.signature = tJSON['signature']
                transaction.hash = tJSON['hash']
            # If none of the above, it is a normal transaction
            else:
                # sender, receiver, amount, timestamp
                transaction = Transaction(tJSON['sender'], tJSON['receiver'], int(
                    tJSON['amount']), tJSON['timestamp'])
                transaction.signature = tJSON['signature']
                transaction.hash = tJSON['hash']

            tArr.append(transaction)

        return tArr

    def object_tojson(self, ob):
        jsonOb = {}
        func = None
        if hasattr(ob, "func"):
            # print(ob.func.__name__)
            jsonOb["func"] = ob.func.__name__
        for field in filter(lambda a: not a.startswith('__'), dir(ob)):
            attribute = getattr(ob, field)
            if (not callable(attribute)):
                if type(attribute) is Property:
                    jsonOb[str(field)] = self.object_tojson(attribute)
                    # print("PROPERTY CHANGED")
                elif type(attribute) is list:
                    # print("LENDER CHANGED")
                    lenders = []
                    for lender in attribute:
                        lnd = self.object_tojson(lender)
                        lenders.append(lnd)
                    jsonOb[str(field)] = lenders
                else:
                    jsonOb[str(field)] = attribute
        return jsonOb
