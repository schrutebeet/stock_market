class Rectagle:
    
    def create_square1(self, a):
        return a
    
    @classmethod
    def create_square2(cls, a):
        return a**2
    
    @staticmethod
    def create_square3(a):
        return a**2
    
poligon = Rectagle.create_square3(5)
print(poligon)