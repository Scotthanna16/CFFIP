class PositionManager:
    def __init__(self):
        self.__positions = {}


    @property
    def positions(self):
        return self.__positions
    @positions.setter
    def pos.setter(self,value):
        self.__positions==value
        
    def update_position(self,order):
        if order['symbol'] not in self.__positions:
            self.__positions[order['symbol']] = 0
        if order['side'] == 'buy':
            self.__positions[order['symbol']]+=order['quantity'] * order['price']
        else:
            self.__positions[order['symbol']]-=order['quantity'] * order['price']

    
    def get_positions(self):
        return self.__positions
pm = PositionManager()

pm.update_position({'side':'buy', 'quantity':5, 'price': 5, 'symbol': "MSFT"})
pm.update_position({'side':'buy', 'quantity':10, 'price': 5, 'symbol': "MSFT"})

print(pm.get_positions())