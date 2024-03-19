import random
import time
import tkinter as tk
from tkinter import messagebox

class MinesweeperAI:
    def __init__(self, rows=16, cols=30, num_bombs=48):
        self.rows = rows
        self.cols = cols
        self.num_bombs = num_bombs
        self.game_board = self.generate_minesweeper_board()
        self.played_board = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cleared_board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged_board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged_bombs = 0
        self.loss = False
        self.tiles_popped = 0

    def generate_minesweeper_board(self):
        board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        bomb_coords = []
        while len(bomb_coords) < self.num_bombs:
            bomb_row = random.randint(0, self.rows - 1)
            bomb_col = random.randint(0, self.cols - 1)
            if (bomb_row, bomb_col) not in bomb_coords:
                bomb_coords.append((bomb_row, bomb_col))

        for row, col in bomb_coords:
            board[row][col] = 9
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= row + i < self.rows and 0 <= col + j < self.cols and board[row + i][col + j] != 9:
                        board[row + i][col + j] += 1

        return board

    def recursive_uncover(self, x, y):
        if 0 <= x < self.rows and 0 <= y < self.cols and self.cleared_board[x][y] == 0 and self.played_board[x][y] == -1:
            self.cleared_board[x][y] = 1
            self.tiles_popped += 1
            if self.game_board[x][y] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        self.recursive_uncover(x + i, y + j)
            elif self.game_board[x][y] != 9:
                self.played_board[x][y] = self.game_board[x][y]

    def ai_make_move(self):
        move_made = False
        surrounding_bombs = 0

        for x in range(self.rows):
            for y in range(self.cols):
                if self.played_board[x][y] == 0 and self.cleared_board[x][y] == 0:
                    self.recursive_uncover(x, y)

        for a in range(self.cols):
            for b in range(self.rows):
                if self.cleared_board[b][a] == 0:
                    surrounding_bombs = 0
                    for c in range(-1, 2):
                        for d in range(-1, 2):
                            if 0 <= b+c < self.rows and 0 <= a+d < self.cols:
                                if self.flagged_board[b+c][a+d] == 1:
                                    surrounding_bombs += 1

                    if self.played_board[b][a] == surrounding_bombs:
                        for c in range(-1, 2):
                            for d in range(-1, 2):
                                new_b = b + c
                                new_a = a + d
                                if 0 <= new_b < self.rows and 0 <= new_a < self.cols:
                                    if self.flagged_board[new_b][new_a] == 0 and self.played_board[new_b][new_a] == -1:
                                        self.played_board[new_b][new_a] = self.game_board[new_b][new_a]
                                        self.tiles_popped += 1
                        self.cleared_board[b][a] = 1
                        move_made = True


        move_made2 = False
        if not move_made:
            surrounding_numbers = 0
            for a in range(self.cols):
                for b in range(self.rows):
                    if 1 <= self.played_board[b][a] <= 8:
                        surrounding_numbers = 0
                        for c in range(-1, 2):
                            for d in range(-1, 2):
                                if 0 <= b + c < self.rows and 0 <= a + d < self.cols:
                                    if not (c == 0 and d == 0):
                                        if 0<=self.played_board[b+c][a+d]<=8:
                                            surrounding_numbers+=1
                                else:
                                    surrounding_numbers+=1
                        if self.played_board[b][a] == (8 - surrounding_numbers) and self.cleared_board[b][a] == 0:
                            for c in range(-1, 2):
                                for d in range(-1, 2):
                                    if 0 <= b + c < self.rows and 0 <= a + d < self.cols:
                                        if self.played_board[b + c][a + d] == -1:
                                            if self.flagged_board[b + c][a + d] == 0:
                                                self.flagged_board[b + c][a + d] = 1
                                                self.flagged_bombs += 1
                                            move_made2 = True
                            self.cleared_board[b][a] = 1


        if not move_made2 and not move_made:
            probability_move_made = False
            probability_matrix = self.calculate_probability_matrix()

            min_probability = 2
            min_x, min_y = -1, -1

            for x in range(self.rows):
                for y in range(self.cols):
                    if 0 <= probability_matrix[x][y] < min_probability and self.played_board[x][y] == -1 and self.flagged_board[x][y] == 0:
                        min_probability = probability_matrix[x][y]
                        min_x, min_y = x, y

            if min_x != -1 and min_y != -1:
                self.played_board[min_x][min_y] = self.game_board[min_x][min_y]
                probability_move_made = True

            if not probability_move_made:
                while True:
                    x = random.randint(0, self.rows - 1)
                    y = random.randint(0, self.cols - 1)
                    if self.played_board[x][y] == -1 and self.flagged_board[x][y] == 0:
                        break
                
                self.played_board[x][y] = self.game_board[x][y]

        for x in range(self.rows):
            for y in range(self.cols):
                if self.played_board[x][y] == 9:
                    self.loss = True
                    self.reveal_bombs()
                    return
    def reveal_bombs(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.game_board[x][y] == 9:  # Where the bombs are located
                    self.played_board[x][y] = 9

    def calculate_probability_matrix(self):
        probability_matrix = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]

        for x in range(self.rows):
            for y in range(self.cols):
                if self.played_board[x][y] == -1:
                    mines_info = []

                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            nx, ny = x + i, y + j
                            if 0 <= nx < self.rows and 0 <= ny < self.cols:
                                if self.played_board[nx][ny] >= 1 and self.played_board[nx][ny] <= 8:  # Numbered cell
                                    flagged, unrevealed = self.count_flagged_and_unrevealed(nx, ny)
                                    mines_info.append((self.played_board[nx][ny] - flagged, unrevealed))

                    if mines_info:
                        total_weight = sum(1 / unrevealed for _, unrevealed in mines_info if unrevealed > 0)
                        weighted_probabilities = [(mines / unrevealed) * (1 / unrevealed) for mines, unrevealed in mines_info if unrevealed > 0]
                        if weighted_probabilities:
                            probability_matrix[x][y] = sum(weighted_probabilities) / total_weight

        return probability_matrix
    
    def count_flagged_and_unrevealed(self, x, y):
        flagged, unrevealed = 0, 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx, ny = x + i, y + j
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if self.played_board[nx][ny] == -1:
                        unrevealed += 1
                    elif self.played_board[nx][ny] == 9:
                        flagged += 1
        return flagged, unrevealed

    def count_flagged_mines(self):
        self.flagged_bombs = 0

        for x in range(self.rows):
            for y in range(self.cols):
                if self.game_board[x][y] == 9 and self.flagged_board[x][y] == 1:
                    self.flagged_bombs += 1

    def showing(self):
        print("Game Board:")
        for row in self.game_board:
            print(' '.join(map(str, row)))

        print("\nPlayed Board:")
        for row in self.played_board:
            print(' '.join(map(str, row)))

        print("\nCleared Board:")
        for row in self.cleared_board:
            print(' '.join(map(str, row)))

        print("\nFlagged Board:")
        for row in self.flagged_board:
            print(' '.join(map(str, row)))

        print("\nFlagged Bombs:", self.flagged_bombs)
        print("Loss:", self.loss)

    def play_game(self):
        self.__init__()
        first_move = True
        while not self.loss and self.flagged_bombs < self.num_bombs:
            if first_move:
                first_move = False
            self.ai_make_move()
        return not self.loss

    def run_multiple_games(self, num_games):
        wins = 0
        total_tiles_popped = 0
        total_bombs_flagged = 0

        for _ in range(num_games):
            if self.play_game():
                wins += 1
            total_tiles_popped += self.tiles_popped
            total_bombs_flagged += self.flagged_bombs

        average_tiles_popped = total_tiles_popped / num_games
        average_bombs_flagged = total_bombs_flagged / num_games

        return wins, average_tiles_popped, average_bombs_flagged


class MinesweeperGUI:
    def __init__(self, master, ai):
        self.master = master
        self.ai = ai
        self.labels = [[None for _ in range(self.ai.cols)] for _ in range(self.ai.rows)]
        self.init_gui()

    def init_gui(self):
        self.master.title("Minesweeper AI")
        self.master.state('zoomed')  # For fullscreen
        self.master.configure(bg='black')

        for x in range(self.ai.rows):
            for y in range(self.ai.cols):
                label = tk.Label(self.master, text='', borderwidth=1, relief="solid", width=4, height=2, bg='grey', fg='white')
                label.grid(row=x, column=y, sticky='nsew')

                # Configure row and column weights for uniform sizing
                self.master.grid_rowconfigure(x, weight=1)
                self.master.grid_columnconfigure(y, weight=1)

                self.labels[x][y] = label
        self.master.grid_rowconfigure(self.ai.rows, weight=1)
        self.status_label = tk.Label(self.master, text="Initializing...", bg='black', fg='white')
        self.status_label.grid(row=self.ai.rows, column=0, columnspan=self.ai.cols, sticky='nsew')


    def update_gui(self):
        bomb_img = tk.PhotoImage(file='bomb.png')  # Update the file path
        flag_img = tk.PhotoImage(file='flag.png')  # Update the file path

        for x in range(self.ai.rows):
            for y in range(self.ai.cols):
                if self.ai.flagged_board[x][y] == 1:
                    self.labels[x][y].config(image=flag_img, text='')
                    self.labels[x][y].image = flag_img  # Keep a reference
                elif self.ai.played_board[x][y] == 9:
                    self.labels[x][y].config(image=bomb_img, text='')
                    self.labels[x][y].image = bomb_img  # Keep a reference
                elif self.ai.played_board[x][y] == -1:
                    self.labels[x][y].config(text=' ', image='')
                else:
                    self.labels[x][y].config(text=str(self.ai.played_board[x][y]), image='')
        status_text = f"Total Bombs: {self.ai.num_bombs} | Bombs Flagged: {self.ai.flagged_bombs} | Tiles Popped: {self.ai.tiles_popped}"
        self.status_label.config(text=status_text)
        self.master.update()

    def run_ai(self, num_games):
        for _ in range(num_games):
            self.ai.__init__(self.ai.rows, self.ai.cols, self.ai.num_bombs)
            while not self.ai.loss and self.ai.flagged_bombs < self.ai.num_bombs:
                self.ai.ai_make_move()
                self.update_gui()
                time.sleep(0.05)
            result_message = "AI won!" if self.ai.flagged_bombs == self.ai.num_bombs else "AI lost!"
            messagebox.showinfo("Game Over", result_message)

def main():
    root = tk.Tk()
    ai = MinesweeperAI()
    gui = MinesweeperGUI(root, ai)
    num_games = 10
    root.after(1000, lambda: gui.run_ai(num_games))
    root.mainloop()


if __name__ == "__main__":
    main()