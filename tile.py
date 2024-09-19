class Tile:
    def __init__(self):
        self.bomb = False
        self.revealed = False
        self.flagged = False
        self.bomb_neighbour_count = 0

    def set_bomb(self):
        self.bomb = True

    def no_bomb(self):
        self.bomb = False

    def reveal(self):
        self.revealed = True
        return not self.is_bomb()

    def toggle_flag(self):
        self.flagged = not self.flagged

    def is_bomb(self):
        return self.bomb
    
    def is_revealed(self):
        return self.revealed
    
    def is_flagged(self):
        return self.flagged
    
    def set_bomb_neighbours(self, count):
        self.bomb_neighbour_count = count

    def bomb_neighbours(self):
        return self.bomb_neighbour_count