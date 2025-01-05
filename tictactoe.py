import math
from functools import lru_cache

def print_board(board):
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print("\n")

def check_winner(board, player):
    win_conditions = [
        [0, 1, 2],  
        [3, 4, 5],  
        [6, 7, 8],  
        [0, 3, 6],  
        [1, 4, 7],  
        [2, 5, 8],  
        [0, 4, 8],  
        [2, 4, 6]  
    ]
    for condition in win_conditions:
        if all(board[i] == player for i in condition):
            return True
    return False

def is_board_full(board):
    return all(space != ' ' for space in board)

def get_available_moves(board):
    return [i for i, spot in enumerate(board) if spot == ' ']

def player_move(board, player):
    while True:
        try:
            move = int(input(f"Player {player}, enter your move (1-9): ")) - 1
            if move in get_available_moves(board):
                board[move] = player
                break
            else:
                print("Invalid move. The cell is already occupied or out of range.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")

def print_instructions():
    print("Enter a number between 1 and 9 to place your symbol on the corresponding cell.")
    print("""
     1 | 2 | 3
    ---+---+---
     4 | 5 | 6
    ---+---+---
     7 | 8 | 9
    """)

def play_game():
    board = [' ' for _ in range(9)]
    current_player = 'X'
    print_instructions()
    print_board(board)

    while True:
        display_move_probabilities(board, current_player)
        player_move(board, current_player)
        print_board(board)

        if check_winner(board, current_player):
            print(f"Player {current_player} wins!")
            break

        if is_board_full(board):
            print("It's a draw!")
            break

        # Switch player
        current_player = 'O' if current_player == 'X' else 'X'

def main():
    while True:
        play_game()
        replay = input("Do you want to play again? (y/n): ").lower()
        if replay != 'y':
            print("Thank you for playing Tic-Tac-Toe!")
            break
        else:
            print("\nStarting a new game...\n")

@lru_cache(maxsize=None)

def compute_shortest_paths(board_tuple, current_player):
    board = list(board_tuple)
    opponent = 'O' if current_player == 'X' else 'X'

    # Check win
    if check_winner(board, opponent):
        if opponent == 'X':
            return (0, math.inf, math.inf)  
        else:
            return (math.inf, 0, math.inf) 

    # Check draw
    if is_board_full(board):
        return (math.inf, math.inf, 0)

    available_moves = get_available_moves(board)

    # Initialize shortest paths
    shortest_x_win = math.inf
    shortest_o_win = math.inf
    shortest_draw = math.inf

    for move in available_moves:
        board[move] = current_player

        if check_winner(board, current_player):
            if current_player == 'X':
                path_x_win = 1
                path_o_win = math.inf
                path_draw = math.inf
            else:
                path_x_win = math.inf
                path_o_win = 1
                path_draw = math.inf
        else:
            sub_x_win, sub_o_win, sub_draw = compute_shortest_paths(tuple(board), opponent)
            if sub_x_win != math.inf:
                path_x_win = sub_x_win + 1
            else:
                path_x_win = math.inf

            if sub_o_win != math.inf:
                path_o_win = sub_o_win + 1
            else:
                path_o_win = math.inf

            if sub_draw != math.inf:
                path_draw = sub_draw + 1
            else:
                path_draw = math.inf

        # Update shortest paths
        shortest_x_win = min(shortest_x_win, path_x_win)
        shortest_o_win = min(shortest_o_win, path_o_win)
        shortest_draw = min(shortest_draw, path_draw)

        board[move] = ' '  

    return (shortest_x_win, shortest_o_win, shortest_draw)

def display_move_probabilities(board, current_player):
    available_moves = get_available_moves(board)
    move_probabilities = []
    recommendation_scores = []

    for move in available_moves:
        board[move] = current_player
        board_tuple = tuple(board)

        # Compute shortest paths 
        shortest_x_win, shortest_o_win, shortest_draw = compute_shortest_paths(board_tuple, 'O' if current_player == 'X' else 'X')
        board[move] = ' ' 
        paths = []
        if shortest_x_win != math.inf:
            paths.append(shortest_x_win)
        if shortest_o_win != math.inf:
            paths.append(shortest_o_win)
        if shortest_draw != math.inf:
            paths.append(shortest_draw)
    
        epsilon = 1e-6 # Avoid division by zero
        weight_x = 1 / (shortest_x_win + epsilon) if shortest_x_win != math.inf else 0
        weight_o = 1 / (shortest_o_win + epsilon) if shortest_o_win != math.inf else 0
        weight_d = 1 / (shortest_draw + epsilon) if shortest_draw != math.inf else 0

        total_weight = weight_x + weight_o + weight_d
        if total_weight == 0:
            x_prob = o_prob = draw_prob = 0
        else:
            x_prob = (weight_x / total_weight) * 100
            o_prob = (weight_o / total_weight) * 100
            draw_prob = (weight_d / total_weight) * 100

        move_probabilities.append((move + 1, round(x_prob, 2), round(o_prob, 2), round(draw_prob, 2)))

        # Best move calculation
        if current_player == 'X':
            recommendation_score = x_prob - o_prob
        else:
            recommendation_score = o_prob - x_prob

        recommendation_scores.append((move + 1, recommendation_score))

    # Determine the Best move {biggest percentage}
    if recommendation_scores:
        max_score = max(score for _, score in recommendation_scores)
        best_moves = [move for move, score in recommendation_scores if score == max_score]
        recommended_move = best_moves[0] if best_moves else None
    else:
        recommended_move = None

    # Display probabilities
    header = f"{'Move':<5} | {'X Win Probability':<18} | {'O Win Probability':<18} | {'Draw Probability':<15}"
    separator = "-" * len(header)
    print(header)
    print(separator)
    for move, x_prob, o_prob, draw_prob in move_probabilities:
        print(f"{move:<5} | {x_prob:>17.2f}% | {o_prob:>17.2f}% | {draw_prob:>13.2f}%")
    print(separator + "\n")

    # Display Best Move
    print(f"Best Move: {recommended_move}\n")

if __name__ == "__main__":
    main()
