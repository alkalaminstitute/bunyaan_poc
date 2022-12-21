from uuid import uuid4


class Property:

    def __init__(self, address, price, seller, rent=30):
        self.property_id = str(uuid4())
        self.address = address
        self.price = int(price)
        self.seller = seller
        self.rent = int(rent)
