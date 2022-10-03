from hashlib import sha512
import hashlib
import json
import jsonpickle
from Crypto.Signature import *
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from datetime import datetime


class Transaction (object):
    def __init__(self, sender, receiver, amount, timestamp=datetime.now().strftime(
            "%m/%d/%Y, %H:%M:%S")):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = timestamp  # change to current date
        self.signature = None
        self.hash = self.calculate_hash()

    def getPublicKeyRsa(self):
        # importing RSA public key from sender's address
        print(self.sender)
        return RSA.import_key(self.sender)

    def calculate_hash(self):
        hashString = str(self.sender) + str(self.receiver) + \
            str(self.amount) + str(self.time)
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

        # message which will be signed is the has of the tx
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
