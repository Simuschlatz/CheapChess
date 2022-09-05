from core.Engine.move_generator import Legal_move_generator
from core.Engine.AI.move_ordering import order_moves, order_moves_pst
from core.Engine.AI.eval_utility import Evaluation

class Dfs:
    checkmate_value = 9999
    
    @classmethod
    def init(cls, board) -> None:
        cls.board = board
        cls.evaluated_positions = 0
        cls.cutoffs = 0

    @classmethod
    def traverse_tree(cls, depth):
        """
        Starts traversal of board's possible configurations
        :return: best move possible
        """
        cls.searched_nodes = 0
        best_move = None
        alpha = float("inf")
        beta = float("-inf")
        best_eval = beta
        current_pos_moves = order_moves(Legal_move_generator.load_moves(), cls.board)
        for move in current_pos_moves:
            cls.searched_nodes += 1
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta_opt(depth - 1, beta, alpha)
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = move
            cls.board.reverse_move()
        print("BEST EVAL: ", best_eval)
        return best_move

    @classmethod
    def alpha_beta_opt(cls, depth, alpha, beta):
        if not depth:
        #     cls.evaluated_positions += 1
        #     return Evaluation.pst_shef()
            return cls.quiescene(alpha, beta)

        moves = order_moves(Legal_move_generator.load_moves(), cls.board)
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            # Return checkmated value instead of negative infinity so the ai still chooses a move even if it only detects
            # checkmates, as the checkmate value still is better than the initial beta of -infinity
            return -cls.checkmate_value

        for move in moves:
            # traversing down the tree
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta_opt(depth - 1, -beta, -alpha)
            cls.board.reverse_move()

            # Move is even better than best eval before,
            # opponent won't choose this move anyway so PRUNE YESSIR
            if evaluation >= beta:
                cls.cutoffs += 1
                return beta # Return -alpha of opponent, which will be turned to alpha in depth + 1
            # Keep track of best move for moving color
            alpha = max(evaluation, alpha)

        return alpha

        
    @classmethod
    def quiescene(cls, alpha, beta):
        """
        A dfs-like algorithm used for chess searches, only considering captureing moves, thus helping the conventional
        search with misjudgment of situations when significant captures could take place in a depth below the search depth.
        :return: the best evaluation of a particular game state, only considering captures
        """ 
        # Evaluate current position before doing any moves, so a potentially good state for non-capture moves
        # isn't ruined by bad captures
        cls.evaluated_positions += 1
        eval = Evaluation.pst_shef()
        # Typical alpha beta operations
        if eval >= beta:
            return beta
        alpha = max(eval, alpha)

        moves = order_moves_pst(Legal_move_generator.load_moves(generate_quiets=False), cls.board)
        for move in moves:
            cls.board.make_move(move)
            evaluation = -cls.quiescene(-beta, -alpha)
            cls.board.reverse_move()
            # Move is even better than best eval before,
            # opponent won't choose move anyway so PRUNE YESSIR
            if evaluation >= beta:
                return beta
            # Keep track of best move for moving color
            alpha = max(evaluation, alpha)
        # If there are no captures to be done anymore, return the best evaluation
        return alpha


    @classmethod
    def minimax(cls, depth):
        """
        A brute force dfs-like algorithm traversing every node of the game's 
        possible-outcome-tree of given depth
        with branching factor b and depth d time-complexity is O(b^d)
        :return: best move possible
        """
        # leaf node, return the static evaluation of current board
        if not depth:
            return cls.board.shef()

        moves = Legal_move_generator.load_moves()
        
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        best_evaluation = float("-inf")
        for move in moves:
            cls.searched_nodes += 1
            cls.board.make_move(move)
            evaluation = -cls.minimax(depth - 1)
            best_evaluation = max(evaluation, best_evaluation)
            cls.board.reverse_move()

        return best_evaluation
    
    @classmethod
    def alpha_beta(cls, depth, alpha, beta):
        if not depth:
            return cls.board.shef()

        moves = Legal_move_generator.load_moves()
        # Check- or Stalemate, meaning game is lost
        # NOTE: Unlike international chess, Xiangqi sees stalemate as equivalent to losing the game
        if not len(moves):
            return float("-inf")

        for move in moves:
            cls.searched_nodes += 1
            cls.board.make_move(move)
            evaluation = -cls.alpha_beta(depth - 1, -beta, -alpha)
            cls.board.reverse_move()
            # Move is even better than best eval before,
            # opponent won't choose move anyway so PRUNE YESSIR
            if evaluation >= beta:
                return beta
            alpha = max(evaluation, alpha)
        return alpha

