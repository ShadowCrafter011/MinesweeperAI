from player import Player, Node


class Player1(Player):
    def __init__(self, id, board=None, inputs=16*30):
        super().__init__(id, board, inputs)
        self.output_nodes = [Node(x, -1, "O") for x in range(inputs)]

    def get_action(self, board):
        biggest = self.output_nodes[0]
        for output_node in self.output_nodes:
            if abs(output_node.value) > abs(biggest.value):
                biggest = output_node
        return ["flag" if biggest.value < 0 else "reveal", biggest.index // board.width, biggest.index % board.width]


class Player2(Player):
    def __init__(self, id, board=None, inputs=16*30):
        super().__init__(id, board, inputs)
        self.output_nodes = [Node(1, -1, "O")]

    def get_action(self, board):
        output_node = self.output_nodes[0]
        index = abs(output_node.value) * board.width * board.height
        index = max(0, min(board.width * board.height - 1, index))
        return ["flag" if output_node.value < 0 else "reveal", int(index // board.width), int(index % board.width)]
    