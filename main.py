from board import Board


def main():
    board = Board(16, 30, 2)
    print(board)
    while (cmd := input("Flag x y: ")) != "exit":
        cmd = cmd.split(" ")
        if cmd[0] == "flag":
            board.toggle_tile_flag(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == "reveal":
            result = board.reveal_tile(int(cmd[1]), int(cmd[2]))
            if result == "won":
                print(board)
                print("You won!")
                break
            elif not result:
                print(board)
                print("You lost!")
                break
        print("\n" * 10)
        print(board)



if __name__ == "__main__":
    main()
