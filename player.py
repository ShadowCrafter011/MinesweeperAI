from random import randint, random, sample
import pickle


class Node:
    def __init__(self, index, layer, node_type, threshold=1):
        self.index = index
        self.node_type = node_type
        self.threshold = threshold
        self.layer = layer
        self.value = 0
        self.connections = []

        self.active = False

    def connection_visualisation(self, before=""):
        this_node = f"{self.node_type}({self.index}, {self.value}) "

        if len(self.connections) == 0:
            return [before + this_node]

        output = []
        for con in self.connections:
            visualisation = before + f"{self.node_type}({self.index}, {self.value}) --{con.strength}--> "
            output += con.next_node.connection_visualisation(visualisation)
        return output


class Connection:
    def __init__(self, strength, next_node):
        self.strength = strength
        self.next_node = next_node


class Player:
    @classmethod
    def load(cls, model_file):
        with open(model_file, "rb") as f:
            return pickle.load(f)

    def __init__(self, id, board=None, inputs=16*30):
        self.id = id

        self.treshold_modification_chance = 1
        self.strength_modification_chance = 1
        self.add_connection_chance = 1
        self.remove_connection_chance = 0.2
        self.add_node_chance = 1
        self.remove_node_chance = 0.2
        self.new_node_index = inputs

        if board:
            inputs = board.width * board.height
        self.input_nodes = [Node(x, -1, "I") for x in range(inputs)]
        self.output_nodes = [Node(1, -1, "O")]
        self.intermediate_nodes = [[] for _ in range(10)]
        self.connections = []

    def __str__(self):
        connections = []
        for input_node in self.input_nodes:
            connections += input_node.connection_visualisation()
        return "\n".join(connections)
    
    def play(self, board):
        self.calculate_node_values(board.as_flat_numerical())
        action = self.get_action(board)
        index = action[1:]
        if action[0] == "flag":
            board.toggle_tile_flag(*index)
            return True
        else:
            return board.reveal_tile(*index)
    
    def get_action(self, board):
        return ["flag", 0, 0]

    def calculate_node_values(self, flat_board):
        for i in range(len(flat_board)):
            self.input_nodes[i].value = flat_board[i]
            for input_node in self.input_nodes:
                for con in input_node.connections:
                    con.next_node.value += con.strength * input_node.value
            for layer in self.intermediate_nodes:
                for intermediate_node in layer:
                    if intermediate_node.value <= intermediate_node.threshold:
                        continue
                    for con in intermediate_node.connections:
                        con.next_node.value += con.strength * intermediate_node.value
    
    def mutate(self, mutation_chance=1):
        if random() > mutation_chance:
            return False

        # 1: modify node threshold
        # 2: modify connection strength
        # 3: add connection
        # 4: remove connection
        # 5: add intermediate node
        # 6: remove intermediate node
        mutation = randint(1, 6)
        match mutation:
            case 1:
                if random() < self.treshold_modification_chance:
                    active_layers = self.active_intermediate_layers()
                    if len(active_layers) > 0:
                        layer = self.intermediate_nodes[active_layers[randint(0, len(active_layers) - 1)]]
                        layer[randint(0, len(layer) - 1)].threshold += random() - 0.5
            case 2:
                if random() < self.strength_modification_chance:
                    if len(self.connections) > 0:
                        self.connections[randint(0, len(self.connections) - 1)].strength += random() - 0.5
            case 3:
                if random() < self.add_connection_chance:
                    active_layers = ["in"] + self.active_intermediate_layers() + ["out"]
                    choices = sample(range(len(active_layers)), 2)
                    from_node_layer = active_layers[min(choices)]
                    to_node_layer = active_layers[max(choices)]
                    from_node = self.get_node(from_node_layer)
                    to_node = self.get_node(to_node_layer)
                    connection = Connection(random() - 0.5, to_node)
                    from_node.connections.append(connection)
                    self.connections.append(connection)
            case 4:
                if random() < self.remove_connection_chance:
                    if len(self.connections) > 0:
                        connection = self.connections[randint(0, len(self.connections) - 1)]
                        self.connections.remove(connection)
                        for node in self.all_nodes():
                            if connection in node.connections:
                                node.connections.remove(connection)
            case 5:
                if random() < self.add_node_chance:
                    i = randint(0, len(self.intermediate_nodes) - 1)
                    layer = self.intermediate_nodes[i]
                    layer.append(Node(self.new_node_index, i, "B", random() - 0.5))
                    self.new_node_index += 1
            case 6:
                if random() < self.remove_node_chance:
                    active_layers = self.active_intermediate_layers()
                    if len(active_layers) > 0:
                        layer = self.intermediate_nodes[active_layers[randint(0, len(active_layers) - 1)]]
                        node = layer[randint(0, len(layer) - 1)]
                        layer.remove(node)
                        for n in self.all_nodes():
                            for con in n.connections:
                                if con.next_node == node:
                                    n.connections.remove(con)
        
        return mutation
        
    def active_intermediate_layers(self):
        layers_with_nodes = []
        for i in range(len(self.intermediate_nodes)):
            if len(self.intermediate_nodes[i]) > 0:
                layers_with_nodes.append(i)
        return layers_with_nodes
    
    def get_node(self, layer):
        if layer == "in":
            return self.input_nodes[randint(0, len(self.input_nodes) - 1)]
        elif layer == "out":
            return self.output_nodes[randint(0, len(self.output_nodes) - 1)]
        else:
            intermediate_layer = self.intermediate_nodes[layer]
            return intermediate_layer[randint(0, len(intermediate_layer) - 1)]
        
    def all_nodes(self):
        nodes = []
        nodes += self.input_nodes
        nodes += self.output_nodes
        for layer in self.intermediate_nodes:
            nodes += layer
        return nodes
    
    def save(self, model_file):
        with open(model_file, "wb") as f:
            pickle.dump(self, f)
