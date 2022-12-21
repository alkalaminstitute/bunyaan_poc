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
from blockchain.modules.Escrow import Escrow
from blockchain.modules.Transaction import Transaction


class MusharakSmartContract:

    def __init__(self, bl_idx, sctx_idx, wallet_address, sender, property,
                 downpayment, loan_granted=0, lenders=[], escrow=None,
                 timestamp=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")):

        # smart contracts do not have a private key only a public address so they can receive coins
        # Its functions are in charge of sending coins

        self.bl_idx = bl_idx
        self.sctx_idx = sctx_idx
        self.wallet_address = wallet_address
        self.sender = sender
        self.receiver = None
        self.amount = None
        self.property = property
        self.downpayment = int(downpayment)
        self.loan_requested = self.property.price - self.downpayment
        self.loan_granted = int(loan_granted)
        self.loan_remaining = self.loan_requested - self.loan_granted
        self.balance = int(loan_granted) + int(downpayment)
        self.lenders = lenders
        self.escrow = escrow
        self.timestamp = timestamp  # change to current date
        self.signature = None
        self.hash = self.calculate_hash()

    def getPublicKeyRsa(self):
        # importing RSA public key from sender's address
        print(self.sender)
        return RSA.import_key(self.sender)

    def calculate_hash(self):
        hashString = str(self.sender) + str(self.loan_requested) + \
            str(self.balance) + str(self.timestamp)
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
        if not self.signature or len(self.signature) == 0:
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

    def set_rent(self, rent):
        self.property.rent = rent

    def add_lender(self, lender, loan_amount):
        self.lenders.append(lender)
        self.update_balance(loan_amount)

    def update_balance(self, loan_amount):
        self.balance += loan_amount
        self.loan_granted += loan_amount
        self.loan_remaining -= loan_amount

    def set_escrow(self, name, escrow_address, property_id):
        self.escrow = Escrow(name, escrow_address, property_id)

    def distribute_rent(self, keyPair):
        txs = []
        for lender in self.lenders:
            percentage = lender.loaned_amount/self.property.price
            # rent is set to 30 dinars by default
            amt = percentage * self.property.rent
            tx = Transaction(self.sender, lender.wallet_address, amt)
            tx.sign_transaction(keyPair)
            txs.append(tx)
        return txs

    def json_encode(self):
        return jsonpickle.encode(self)
