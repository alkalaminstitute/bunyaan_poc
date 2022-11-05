from uuid import uuid4


class Property:

    def __init__(self, address, price, seller, rent=100):
        self.property_id = str(uuid4())
        self.address = address
        self.price = price
        self.seller = seller
        self.rent = rent
