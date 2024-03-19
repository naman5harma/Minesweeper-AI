import random
import time


def generate_minesweeper_board(rows, cols, num_bombs):
    board = [[0 for _ in range(cols)] for _ in range(rows)]

    bomb_coords = []
    while len(bomb_coords) < num_bombs:
        bomb_row = random.randint(0, rows - 1)
        bomb_col = random.randint(0, cols - 1)
        if (bomb_row, bomb_col) not in bomb_coords:
            bomb_coords.append((bomb_row, bomb_col))

    for row, col in bomb_coords:
        board[row][col] = 9
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= row + i < rows and 0 <= col + j < cols and board[row + i][col + j] != 9:
                    board[row + i][col + j] += 1

    return board

def recursive_uncover(x, y):
    if 0 <= x < rX and 0 <= y < rY and cleared_board[x][y] == 0 and played_board[x][y] == -1:
        cleared_board[x][y] = 1
        tiles_popped += 1
        if game_board[x][y] == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    recursive_uncover(x + i, y + j)
        elif game_board[x][y] != 9:
            played_board[x][y] = game_board[x][y]

def ai_make_move():
    global game_board, played_board, rX, rY, loss
    global surrounding_bombs, flagged_bombs, loss, tiles_popped
    move_made = False
    surrounding_bombs = 0

    for x in range(rX):
        for y in range(rY):
            if played_board[x][y] == 0 and cleared_board[x][y] == 0:
                recursive_uncover(x, y)

    for a in range(rY):
        for b in range(rX):
            if cleared_board[b][a] == 0:
                surrounding_bombs = 0
                for c in range(-1, 2):
                    for d in range(-1, 2):
                        if 0 <= b+c < rX and 0 <= a+d < rY:
                            if flagged_board[b+c][a+d] == 1:
                                surrounding_bombs += 1

                if played_board[b][a] == surrounding_bombs:
                    for c in range(-1, 2):
                        for d in range(-1, 2):
                            new_b = b + c
                            new_a = a + d
                            if 0 <= new_b < rX and 0 <= new_a < rY:
                                if flagged_board[new_b][new_a] == 0 and played_board[new_b][new_a] == -1:
                                    played_board[new_b][new_a] = game_board[new_b][new_a]
                                    tiles_popped += 1
                    cleared_board[b][a] = 1
                    # print(f"Cleared Square: {{{b},{a}}}")
                    move_made = True


    move_made2 = False
    if not move_made:
        surrounding_numbers = 0
        for a in range(rY):
            for b in range(rX):
                if 1 <= played_board[b][a] <= 8:
                    surrounding_numbers = 0
                    for c in range(-1, 2):
                        for d in range(-1, 2):
                            if 0 <= b + c < rX and 0 <= a + d < rY:
                                if not (c == 0 and d == 0):
                                    if 0<=played_board[b+c][a+d]<=8:
                                        surrounding_numbers+=1
                            else:
                                surrounding_numbers+=1
                    # print(f"Coord {{{b},{a}}} has {surrounding_numbers} numbers around it")
                    # print(f"        {played_board[b][a]} | {8 - surrounding_numbers}")
                    if played_board[b][a] == (8 - surrounding_numbers) and cleared_board[b][a] == 0:
                        for c in range(-1, 2):
                            for d in range(-1, 2):
                                if 0 <= b + c < rX and 0 <= a + d < rY:
                                    if played_board[b + c][a + d] == -1:
                                        if flagged_board[b + c][a + d] == 0:
                                            flagged_board[b + c][a + d] = 1
                                            flagged_bombs += 1
                                        # print(f"        Flagged Bomb {{{b+c},{a+d}}}")
                                        move_made2 = True
                        cleared_board[b][a] = 1


    if not move_made2 and not move_made:
        probability_move_made = False
        probability_matrix = calculate_probability_matrix(played_board)

        min_probability = 2
        min_x, min_y = -1, -1

        for x in range(rX):
            for y in range(rY):
                if 0 <= probability_matrix[x][y] < min_probability and played_board[x][y] == -1 and flagged_board[x][y] == 0:
                    min_probability = probability_matrix[x][y]
                    min_x, min_y = x, y

        if min_x != -1 and min_y != -1:
            played_board[min_x][min_y] = game_board[min_x][min_y]
            # print(f"AI Revealed Cell with Low Probability: {{{min_x}, {min_y}}}")
            probability_move_made = True

        if not probability_move_made:
            while True:
                x = random.randint(0, rX - 1)
                y = random.randint(0, rY - 1)
                if played_board[x][y] == -1 and flagged_board[x][y] == 0:
                    break
            
            played_board[x][y] = game_board[x][y]
            # print(f"AI Made Random Move: {{{x}, {y}}}")

    for x in range(rX):
        for y in range(rY):
            if played_board[x][y] == 9:
                loss = True
                # print("AI hit a bomb! You lost.")

def calculate_probability_matrix(played_board):
    probability_matrix = [[-1 for _ in range(rY)] for _ in range(rX)]

    for x in range(rX):
        for y in range(rY):
            if played_board[x][y] == -1:
                mines_info = []

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        nx, ny = x + i, y + j
                        if 0 <= nx < rX and 0 <= ny < rY:
                            if played_board[nx][ny] >= 1 and played_board[nx][ny] <= 8:  # Numbered cell
                                flagged, unrevealed = count_flagged_and_unrevealed(nx, ny, played_board)
                                mines_info.append((played_board[nx][ny] - flagged, unrevealed))

                if mines_info:
                    total_weight = sum(1 / unrevealed for _, unrevealed in mines_info if unrevealed > 0)
                    weighted_probabilities = [(mines / unrevealed) * (1 / unrevealed) for mines, unrevealed in mines_info if unrevealed > 0]
                    if weighted_probabilities:
                        probability_matrix[x][y] = sum(weighted_probabilities) / total_weight

    return probability_matrix

def count_flagged_and_unrevealed(x, y, played_board):
    flagged, unrevealed = 0, 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            nx, ny = x + i, y + j
            if 0 <= nx < rX and 0 <= ny < rY:
                if played_board[nx][ny] == -1:
                    unrevealed += 1
                elif played_board[nx][ny] == 9:
                    flagged += 1
    return flagged, unrevealed

def initialize_game():
    global tiles_popped, game_board, rX, rY, num_bombs, played_board, cleared_board, flagged_board, flagged_bombs, loss

    tiles_popped = 0
    rowsH = 30
    colsW = 16
    num_bombs = 48

    game_board = generate_minesweeper_board(rowsH, colsW, num_bombs)

    rX = rowsH
    rY = colsW

    played_board = [[-1 for _ in range(colsW)] for _ in range(rowsH)]
    cleared_board = [[0 for _ in range(colsW)] for _ in range(rowsH)]
    flagged_board = [[0 for _ in range(colsW)] for _ in range(rowsH)]

    flagged_bombs = 0
    loss = False

def count_flagged_mines():
    global flagged_bombs

    flagged_bombs = 0

    for x in range(rX):
        for y in range(rY):
            if game_board[x][y] == 9 and flagged_board[x][y] == 1:
                flagged_bombs += 1

def showing():
    print("Game Board:")
    for row in game_board:
        print(' '.join(map(str, row)))

    print("\nPlayed Board:")
    for row in played_board:
        print(' '.join(map(str, row)))

    print("\nCleared Board:")
    for row in cleared_board:
        print(' '.join(map(str, row)))

    print("\nFlagged Board:")
    for row in flagged_board:
        print(' '.join(map(str, row)))

    print("\nFlagged Bombs:", flagged_bombs)
    print("Loss:", loss)

def play_game():
    initialize_game()
    first_move = True

    while not loss and flagged_bombs < num_bombs:
        if first_move:
            x, y = random.randint(0, rX - 1), random.randint(0, rY - 1)
            while game_board[x][y] == 9:
                x, y = random.randint(0, rX - 1), random.randint(0, rY - 1)
            first_move = False
        ai_make_move()
        # showing()

    return not loss

def run_multiple_games(num_games):
    wins = 0
    total_tiles_popped = 0
    total_bombs_flagged = 0

    for _ in range(num_games):
        initialize_game()
        if play_game():
            wins += 1
        total_tiles_popped += tiles_popped
        total_bombs_flagged += flagged_bombs

    average_tiles_popped = total_tiles_popped / num_games
    average_bombs_flagged = total_bombs_flagged / num_games

    return wins, average_tiles_popped, average_bombs_flagged

num_games = 100  # Set the number of games to play
total_wins, avg_tiles_popped, avg_bombs_flagged = run_multiple_games(num_games)
average_win_rate = total_wins / num_games

print(f"Played {num_games} games, won {total_wins} times.")
print(f"Average Win Rate: {average_win_rate * 100:.2f}%")
print(f"Average Tiles Popped: {avg_tiles_popped:.2f}")
print(f"Average Bombs Flagged: {avg_bombs_flagged:.2f}")
