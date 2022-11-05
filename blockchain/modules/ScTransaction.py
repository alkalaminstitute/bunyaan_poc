from textwrap import dedent
from urllib.parse import urlparse
from Crypto.PublicKey import RSA
from Crypto.Signature import *
from time import time
from datetime import datetime
from hashlib import sha512
import hashlib
import json
import jsonpickle
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

# There are two types of smart contract transaction
# 1. is the one that creates the contract which is the contract state variable and its functions
# 2. is the one that interracts with the contract and in the place of amount, this transaction has the
# code that interacts with the created smartcontract.
# User accounts can then interact with a smart contract by submitting
# transactions that execute a function defined on the smart contract.
# Smart contracts can define rules, like a regular contract,
# and automatically enforce them via the code.


class ScTransaction:

    def __init__(self, bl_idx, sctx_idx, sender, receiver, func, amount=0,
                 timestamp=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")):

        self.bl_idx = bl_idx
        self.sctx_idx = sctx_idx
        self.sender = sender
        self.receiver = receiver
        self.func = func
        self.amount = int(amount)
        self.timestamp = timestamp  # change to current date
        self.signature = None
        self.hash = self.calculate_hash()

    def getPublicKeyRsa(self):
        # importing RSA public key from sender's address
        print(self.sender)
        return RSA.import_key(self.sender)

    def calculate_hash(self):
        hashString = str(self.bl_idx) + str(self.sctx_idx) + \
            str(self.sender) + str(self.receiver) + str(self.timestamp)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def is_valid_transaction(self):
        # takes care of the mining reward transaction
        if (self.sender is None):
            return True
        if (self.hash != self.calculate_hash()):
            print("Hash is not correct!")
            return False
        if (self.sender is self.receiver):
            print("Sender is the same as the receiver")
            return False
        if not self.signature or len(self.signature) is 0:
            print("No Signature!")
            return False

        #### SIG VERIFCATION ####

        # message which will be signed is the has of the tx
        hashTx = self.calculate_hash()

        digest = SHA256.new()
        digest.update(hashTx.encode('utf-8'))

        sig = bytes.fromhex(self.signature)  # convert string to bytes object

        # Load public key (not private key) and verify signature

        # it currently fails because self.sender is not the publickey.
        # we are passing a random number in postman
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^
        print(self.sender)
        # importing RSA public key from sender's address
        senderPublicKey = self.getPublicKeyRsa()
        verifier = PKCS1_v1_5.new(senderPublicKey)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^

        verified = verifier.verify(digest, sig)

        if not verified:
            print('FAILED')
            return False

        print('Successfully verified message')
        return True

    def sign_transaction(self, keyPair):

        if (self.hash != self.calculate_hash()):
            print("transaction tampered error")
            return False

        # print(keyPair.publickey().exportKey())
        # print(str(self.sender.exportKey()))
        senderPublicKey = self.getPublicKeyRsa()
        if (str(keyPair.publickey().exportKey()) != str(senderPublicKey.exportKey())):
            print("Transaction attempt to be signed from another wallet")
            return False

        # message which will be signed is the hash of the tx
        # for signing and veirifcation used: https://gist.github.com/aellerton/2988ff93c7d84f3dbf5b9b5a09f38ceb
        hashTx = self.calculate_hash()

        digest = SHA256.new()
        digest.update(hashTx.encode('utf-8'))

        # Sign the message
        signer = PKCS1_v1_5.new(keyPair)
        sig = signer.sign(digest)

        # sig is bytes object, so convert to hex string.
        # (could convert using b64encode or any number of ways)
        # print("Signature:")
        print(sig.hex())

        # sig = key.sign(hashTx, 'base64')
        self.signature = sig.hex()

        return True

    def json_encode(self):
        return jsonpickle.encode(self)
