class PositionManager:
    def __init__(self):
        self.positions = {}
    
    def add(self, position, number):
        self.positions[position]=number
    def display_positions(self):
        return self.positions


pm1 = PositionManager()

pm1.add("MSFT", 100)

print(pm1.display_positions())
