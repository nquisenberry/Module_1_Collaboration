import copy


FILES = "abcdefgh"


class Piece:
    def __init__(self, color, kind):
        self.color = color
        self.kind = kind

    @property
    def symbol(self):
        symbols = {
            "white": {"pawn": "♙", "rook": "♖", "knight": "♘", "bishop": "♗", "queen": "♕", "king": "♔"},
            "black": {"pawn": "♟", "rook": "♜", "knight": "♞", "bishop": "♝", "queen": "♛", "king": "♚"},
        }
        return symbols[self.color][self.kind]


class ChessGame:
    def __init__(self):
        self.board = self._create_initial_board()
        self.current_turn = "white"

    def _create_initial_board(self):
        board = {}
        back_rank = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]

        for file_index, piece_name in enumerate(back_rank):
            board[(0, file_index)] = Piece("black", piece_name)
            board[(7, file_index)] = Piece("white", piece_name)

        for file_index in range(8):
            board[(1, file_index)] = Piece("black", "pawn")
            board[(6, file_index)] = Piece("white", "pawn")

        return board

    def render(self):
        print("\n  a b c d e f g h")
        for row in range(8):
            cells = []
            for col in range(8):
                piece = self.board.get((row, col))
                cells.append(piece.symbol if piece else "·")
            print(f"{8 - row} {' '.join(cells)}")
        print()

    def coordinate_to_square(self, notation):
        notation = notation.strip().lower()
        if len(notation) != 2:
            raise ValueError("Moves must be in the format 'e2 e4' or 'e2e4'.")
        file_char, rank_char = notation[0], notation[1]
        if file_char not in FILES or rank_char not in "12345678":
            raise ValueError(f"Invalid square: {notation}")
        file_index = FILES.index(file_char)
        row = 7 - (int(rank_char) - 1)
        return row, file_index

    def _in_bounds(self, square):
        row, col = square
        return 0 <= row < 8 and 0 <= col < 8

    def _find_king(self, board, color):
        for square, piece in board.items():
            if piece is not None and piece.color == color and piece.kind == "king":
                return square
        return None

    def _is_square_attacked(self, board, target_square, attacker_color):
        for square, piece in board.items():
            if piece is None or piece.color != attacker_color:
                continue
            row, col = square
            tr, tc = target_square
            dr = tr - row
            dc = tc - col

            if piece.kind == "pawn":
                direction = -1 if attacker_color == "white" else 1
                if (dr == direction) and abs(dc) == 1:
                    return True
                continue

            if piece.kind == "knight":
                if (abs(dr), abs(dc)) in {(1, 2), (2, 1)}:
                    return True
                continue

            if piece.kind == "bishop":
                if abs(dr) != abs(dc):
                    continue
                step_r = 1 if dr > 0 else -1
                step_c = 1 if dc > 0 else -1
                r, c = row + step_r, col + step_c
                while (r, c) != target_square:
                    if board.get((r, c)) is not None:
                        break
                    r += step_r
                    c += step_c
                else:
                    return True
                continue

            if piece.kind == "rook":
                if dr != 0 and dc != 0:
                    continue
                if dr == 0:
                    step = 1 if dc > 0 else -1
                    for c in range(col + step, tc, step):
                        if board.get((row, c)) is not None:
                            break
                    else:
                        return True
                else:
                    step = 1 if dr > 0 else -1
                    for r in range(row + step, tr, step):
                        if board.get((r, col)) is not None:
                            break
                    else:
                        return True
                continue

            if piece.kind == "queen":
                if dr == 0 and dc == 0:
                    continue
                if dr == 0 or dc == 0 or abs(dr) == abs(dc):
                    if dr == 0:
                        step = 1 if dc > 0 else -1
                        for c in range(col + step, tc, step):
                            if board.get((row, c)) is not None:
                                break
                        else:
                            return True
                    elif dc == 0:
                        step = 1 if dr > 0 else -1
                        for r in range(row + step, tr, step):
                            if board.get((r, col)) is not None:
                                break
                        else:
                            return True
                    else:
                        step_r = 1 if dr > 0 else -1
                        step_c = 1 if dc > 0 else -1
                        r, c = row + step_r, col + step_c
                        while (r, c) != target_square:
                            if board.get((r, c)) is not None:
                                break
                            r += step_r
                            c += step_c
                        else:
                            return True
                continue

            if piece.kind == "king":
                if max(abs(dr), abs(dc)) == 1:
                    return True

        return False

    def is_in_check(self, board, color):
        king_square = self._find_king(board, color)
        if king_square is None:
            return False
        enemy_color = "black" if color == "white" else "white"
        return self._is_square_attacked(board, king_square, enemy_color)

    def generate_pseudo_moves(self, board, square):
        piece = board.get(square)
        if piece is None:
            return []

        row, col = square
        moves = []

        if piece.kind == "pawn":
            direction = -1 if piece.color == "white" else 1
            start_row = 6 if piece.color == "white" else 1
            one_step = (row + direction, col)
            if self._in_bounds(one_step) and board.get(one_step) is None:
                moves.append(one_step)
                two_step = (row + 2 * direction, col)
                if row == start_row and board.get(two_step) is None:
                    moves.append(two_step)
            for delta_col in (-1, 1):
                capture_square = (row + direction, col + delta_col)
                if self._in_bounds(capture_square):
                    target = board.get(capture_square)
                    if target is not None and target.color != piece.color:
                        moves.append(capture_square)

        elif piece.kind == "knight":
            for dr, dc in ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)):
                dest = (row + dr, col + dc)
                if self._in_bounds(dest):
                    target = board.get(dest)
                    if target is None or target.color != piece.color:
                        moves.append(dest)

        elif piece.kind in {"bishop", "rook", "queen"}:
            directions = []
            if piece.kind in {"bishop", "queen"}:
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            if piece.kind in {"rook", "queen"}:
                directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while self._in_bounds((r, c)):
                    occupant = board.get((r, c))
                    if occupant is None:
                        moves.append((r, c))
                    else:
                        if occupant.color != piece.color:
                            moves.append((r, c))
                        break
                    r += dr
                    c += dc

        elif piece.kind == "king":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    dest = (row + dr, col + dc)
                    if self._in_bounds(dest):
                        occupant = board.get(dest)
                        if occupant is None or occupant.color != piece.color:
                            moves.append(dest)

        return moves

    def get_legal_moves(self, board, color):
        legal = []
        for square, piece in list(board.items()):
            if piece is None or piece.color != color:
                continue
            for target in self.generate_pseudo_moves(board, square):
                new_board = copy.deepcopy(board)
                moving_piece = new_board.pop(square)
                if new_board.get(target) is not None:
                    del new_board[target]
                new_board[target] = moving_piece
                if not self.is_in_check(new_board, color):
                    legal.append((square, target))
        return legal

    def is_game_over(self, board, color):
        legal = self.get_legal_moves(board, color)
        if not legal:
            if self.is_in_check(board, color):
                return "checkmate", "black" if color == "white" else "white"
            return "stalemate", None
        return None, None

    def parse_move(self, text):
        cleaned = text.strip().lower()
        if not cleaned:
            raise ValueError("Please enter a move.")
        if " " in cleaned:
            pieces = cleaned.split()
            if len(pieces) != 2:
                raise ValueError("Move must include two squares.")
            return self.coordinate_to_square(pieces[0]), self.coordinate_to_square(pieces[1])
        if len(cleaned) == 4:
            return self.coordinate_to_square(cleaned[:2]), self.coordinate_to_square(cleaned[2:])
        raise ValueError("Move format must look like 'e2 e4' or 'e2e4'.")

    def coordinate_to_square(self, notation):
        if len(notation) != 2:
            raise ValueError(f"Invalid square: {notation}")
        file_char, rank_char = notation[0], notation[1]
        if file_char not in FILES or rank_char not in "12345678":
            raise ValueError(f"Invalid square: {notation}")
        col = FILES.index(file_char)
        row = 7 - (int(rank_char) - 1)
        return row, col

    def make_move(self, start, end):
        if self.board.get(start) is None:
            raise ValueError("There is no piece on that square.")

        piece = self.board[start]
        if piece.color != self.current_turn:
            raise ValueError(f"It is {self.current_turn}'s turn.")

        legal = self.get_legal_moves(self.board, self.current_turn)
        if (start, end) not in legal:
            raise ValueError("Illegal move for that piece.")

        new_board = copy.deepcopy(self.board)
        moving_piece = new_board.pop(start)
        if new_board.get(end) is not None:
            del new_board[end]

        if moving_piece.kind == "pawn" and end[0] in (0, 7):
            moving_piece.kind = "queen"

        new_board[end] = moving_piece
        self.board = new_board

    def play(self):
        while True:
            self.render()
            print(f"{self.current_turn.capitalize()}'s turn.")
            command = input("Enter move (example: e2 e4) or 'quit': ").strip().lower()

            if command in {"quit", "exit", "q"}:
                print("Thanks for playing!")
                return

            try:
                start, end = self.parse_move(command)
                self.make_move(start, end)
            except ValueError as exc:
                print(f"Invalid move: {exc}")
                continue

            game_over, winner = self.is_game_over(self.board, self.current_turn)
            if game_over:
                self.render()
                if winner is None:
                    print(f"{game_over.capitalize()}! No legal moves remain.")
                else:
                    print(f"{game_over.capitalize()}! {winner.capitalize()} wins.")
                return

            self.current_turn = "black" if self.current_turn == "white" else "white"


if __name__ == "__main__":
    ChessGame().play()
