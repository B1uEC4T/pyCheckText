class car:
    def __init__(self, company, color):
        self.company = company
        self.color = color

    def drive(self):
        print("Driving")
        self.consume_power()

    def consume_power(self):
        print({call})

class electric_car(car):
    def drive(self):
        print("Gliding")
        self.drain_battery()
    
    def drain_battery(self):
        print({call})

class steam_car(car):
    def drive(self):
        print("Chuff chuff")
        self.use_coal()

    def use_coal(self):
        print({call})

class truck(car):
    def drive(self):
        print("Brrrrr")
        self.use_diesel()

    def use_diesel(self):
        print({call})