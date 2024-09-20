from multiprocessing import Process, Queue
from player import Player
from board import Board
import hashlib
import pickle
import shutil
import os
import re


def main():
    training_name = input("Please input a training name: ")
    os.mkdir(f"players/{training_name}")

    last_archive = 0
    archive_size = 1000
    for gen in range(100_000):
        os.mkdir(f"players/{training_name}/gen{gen}")

        if gen > archive_size + last_archive:
            archive_folder_name = f"players/{training_name}/archive[{last_archive}-{last_archive + archive_size - 1}]"
            os.mkdir(archive_folder_name)
            for x in range(archive_size):
                os.rename(f"players/{training_name}/gen{last_archive + x}", f"{archive_folder_name}/gen{last_archive + x}")
            shutil.make_archive(archive_folder_name, "zip", archive_folder_name)
            shutil.rmtree(archive_folder_name)
            last_archive += archive_size

        if gen == 0:
            players = [Player(str(x)) for x in range(100)]
        else:
            player_pathes = []
            highest = -100
            average = 0
            for path in os.listdir(f"players/{training_name}/gen{gen - 1}"):
                score = float(re.search(r"\[(-?\d*\.?\d*?)\]", path).group(1))
                average += score
                if score > highest:
                    highest = score
                player_pathes.append([score, path])

            print(f"Generation {gen - 1} finished with an average score of {average / len(player_pathes)} and a maximum score of {highest}")

            player_pathes.sort(key=lambda x: x[0], reverse=True)
            player_pathes = [p[1] for p in player_pathes[:10]]

            players = []
            for p in player_pathes:
                path = os.path.join(f"players/{training_name}/gen{gen - 1}", p)
                with open(path, "rb") as f:
                    original_player = pickle.load(f)
                    original_player.id += "-0"
                    players.append(original_player)
                for x in range(9):
                    with open(path, "rb") as f:
                        new_player = pickle.load(f)
                        new_player.mutate()
                        new_player.id += f"-{x + 1}"
                        players.append(new_player)

        pathes = Queue()
        for player in players:
            id_hash = hashlib.sha1(player.id.encode("utf-8")).hexdigest()[:8]
            path = f"players/{training_name}/gen{gen}/player-{id_hash}.pickle"
            pathes.put(path)
            with open(path, "wb") as f:
                pickle.dump(player, f)

        processes = []
        for _ in range(16):
            p = Process(target=get_average_score, args=(pathes, 25))
            p.start()
            processes.append(p)
        [p.join() for p in processes]
    

def get_average_score(pathes, num_games):
    while not pathes.empty():
        player_path = pathes.get()
        total = 0
        with open(player_path, "rb") as f:
            player = pickle.load(f)

            for _ in range(num_games):
                total += play_game(player)
        
        new_name = player_path.replace(".pickle", f"[{total / num_games}].pickle")
        os.rename(player_path, new_name)


def play_game(player):
    board = Board()
    max_moves = board.width * board.height
    while max_moves > 0:
        result = player.play(board)
        max_moves -= 1
        if result == "won":
            return board.revealed_tiles_count() + 50
        elif not result:
            return board.revealed_tiles_count()
    return board.revealed_tiles_count() - 50


if __name__ == "__main__":
    main()
