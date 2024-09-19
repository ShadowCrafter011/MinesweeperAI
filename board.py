from termcolor import colored
from tile import Tile
import numpy as np


class Board:
    def __init__(self, height=16, width=30, bombs=99):
        self.height = height
        self.width = width
        self.bombs = bombs
        self.board = []
        tile_indices = []
        self.no_tiles_revealed = True

        self.colors = { 1: "light_blue", 2: "green", 3: "magenta", 4: "cyan", 5: "yellow", 6: "light_green", 7: "light_red", 8: "blue" }

        self.neighbour_transform = [
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [1, -1],
            [1, 0],
            [1, 1]
        ]

        for y in range(height):
            self.board.append([])
            for x in range(width):
                self.board[y].append(Tile())
                tile_indices.append([y, x])
        
        np.random.shuffle(tile_indices)
        for i in range(bombs):
            self.board[tile_indices[i][0]][tile_indices[i][1]].set_bomb()

        self.count_bombs()

    def __str__(self):
        output = ["- " * (self.width + 2)]
        for y in range(self.height):
            row = ["|"]
            for tile in self.board[y]:
                if tile.is_flagged():
                    row.append(colored("◼", "red"))
                elif not tile.is_revealed():
                    row.append("◼")
                elif tile.is_bomb():
                    row.append(colored("X", "red"))
                elif (neighs := tile.bomb_neighbours()) > 0:
                    row.append(colored(str(neighs), self.colors[neighs]))
                else:
                    row.append(" ")
            row.append("|")
            output.append(" ".join(row))
        output.append("- " * (self.width + 2))
        return "\n".join(output)

    def count_bombs(self):
        for y in range(self.height):
            for x in range(self.width):
                bomb_count = 0
                for i in range(len(self.neighbour_transform)):
                    neighbour_index = [y + self.neighbour_transform[i][0], x + self.neighbour_transform[i][1]]
                    if self.index_in_board(*neighbour_index) and self.board[neighbour_index[0]][neighbour_index[1]].is_bomb():
                        bomb_count += 1
                self.board[y][x].set_bomb_neighbours(bomb_count)
    
    def print_solved(self):
        output = ["- " * (self.width + 2)]
        for y in range(self.height):
            row = ["|"]
            for tile in self.board[y]:
                if tile.is_bomb():
                    row.append(colored("X", "red"))
                elif (neighs := tile.bomb_neighbours()) > 0:
                    row.append(colored(str(neighs), self.colors[neighs]))
                else:
                    row.append(" ")
            row.append("|")
            output.append(" ".join(row))
        output.append("- " * (self.width + 2))
        return "\n".join(output)
    
    def index_in_board(self, y, x):
        return y >= 0 and x >=0 and y < self.height and x < self.width
    
    def toggle_tile_flag(self, y, x):
        if self.board[y][x].is_revealed():
            return

        self.board[y][x].toggle_flag()

    def reveal_tile(self, y, x):
        revealed_tile = self.board[y][x]
        if revealed_tile.is_flagged():
            return True
        
        # Reveal all adjecant tiles if tile was revealed with enough flagged neighbours
        if revealed_tile.is_revealed():
            neigh_flags = 0
            for transform in self.neighbour_transform:
                index = [y + transform[0], x + transform[1]]
                if not self.index_in_board(*index):
                    continue
                if self.board[index[0]][index[1]].is_flagged():
                    neigh_flags += 1
            if neigh_flags == revealed_tile.bomb_neighbours():
                for transform in self.neighbour_transform:
                    rev_index = [y + transform[0], x + transform[1]]
                    if not self.index_in_board(*rev_index):
                        continue
                    if not self.auto_reveal(*rev_index):
                        return False

        can_continue = revealed_tile.reveal()

        # Move bomb if it is the first tile clicked
        if not can_continue and self.no_tiles_revealed:
            can_continue = True
            revealed_tile.no_bomb()
            found_bomb = False
            for ny in range(self.height):
                if found_bomb:
                    break
                for tile in self.board[ny]:
                    if tile == revealed_tile:
                        continue
                    if not tile.is_bomb():
                        tile.set_bomb()
                        found_bomb = True
                        break
            self.count_bombs()

        # Flood reveal if tile has no bomb neighbours
        if revealed_tile.bomb_neighbours() == 0:
            for transform in self.neighbour_transform:
                index = [y + transform[0], x + transform[1]]
                if not self.index_in_board(*index):
                    continue
                self.auto_reveal(*index)

        # Check if non interacted tiles are all bombs and end the game if so
        all_bombs_remain = True
        for y in range(self.height):
            for tile in self.board[y]:
                if tile.is_bomb() or tile.is_revealed():
                    continue
                all_bombs_remain = False
        if all_bombs_remain:
            # Flag remaining tiles
            for y in range(self.height):
                for tile in self.board[y]:
                    if tile.is_revealed() or tile.is_flagged():
                        continue
                    tile.toggle_flag()
            return "won"

        self.no_tiles_revealed = False
        return can_continue
    
    def auto_reveal(self, y, x):
        tile = self.board[y][x]
        
        if tile.is_flagged() or tile.is_revealed():
            return True
        
        can_continue = tile.reveal()

        if tile.bomb_neighbours() == 0:
            for transform in self.neighbour_transform:
                index = [y + transform[0], x + transform[1]]
                if not self.index_in_board(*index):
                    continue
                self.auto_reveal(*index)

        return can_continue
