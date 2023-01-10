import logging
import math
import numpy as np
from core.Engine import Board, LegalMoveGenerator, PrecomputingMoves
from core.Engine.AI.AlphaZero import PlayConfig, CNN
from core.Utils import time_benchmark

log = logging.getLogger(__name__)

'''
- statically evaluate node, if terminal node: return -value
- if leaf node:
    1. get p & v from NN
    2. mask illegal moves in p, normalize masked values
    3. update Ns and legal Moves
- else:
    1. select move with highest Qsa + Usa
    2. make move
    3. MCTS for next position
    4. get the value v of leaf node (when recursion base case is met)
    5. update Qsa and Nsa
        - if a was taken from s before:
            1. N ++
            2. Qsa = ((Nsa - 1) * Qsa + v) / Nsa)
        - else:
            1. Qsa = v
            2. Nsa = 1]
    
    return - v
'''


class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, nnet: CNN, config=PlayConfig):
        self.nnet = nnet
        self.config = config
        # W Values aren't stored because they are only of temporary use in each interation
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores each state s where the terminal code has been evaluated
        self.Vs = {}  # stores legal moves for board s

    def search(self, board: Board, is_root=False, bitboards=None, moves=None):
        """
        This function performs one iteration of MCTS. It recursively calls itself until a leaf node 
        is found. The move chosen at each point maximizes the upper confidence bound (Q(s|a) + U(s|a))

        Once a leaf node is found, the neural network is called to return an initial policy P and a 
        value v for the state. In case the leaf node is a terminal state, the outcome is returned.
        The values are then backpropagated up the search path and the values of Ns, Nsa, Qsa of each node
        are updated.

        The board states are represented as a 64-bit zobrist-hashed number of that board. Actions are 
        determined by finding the move in the action space vector corresponding to the policy vector index

        :param is_root: True if current state is the root state
        :param bitboards: bitboards of current state. If None, they're generated
        """

        # NOTE: the term 'action' is synonymous with 'move' in this method for congruence with the paper
        s = board.zobrist_key
        moves = moves or LegalMoveGenerator.load_moves(board)

        # Check if position was already statically evaluated
        if s not in self.Es:
            status = board.get_terminal_status(len(moves))
            self.Es[s] = status

        if self.Es[s] != -1:
            return -self.Es[s]

        if board.moving_side: moves = board.flip_moves(moves)

        # Check if position was expanded
        if s not in self.Ps:
            state_planes = bitboards or board.piecelist_to_bitboard(adjust_perspective=True)
            # leaf node
            p, v = self.nnet.predict(state_planes)
            self.Ps[s] = p[0] # CNN output is two-dimensional

            valids = LegalMoveGenerator.bitvector_legal_moves(legal_moves=moves) # make this binary maybe?
            # masking invalid moves
            self.Ps[s] = self.Ps[s] * valids
            sum_Ps = np.sum(self.Ps[s])
            
            if sum_Ps:
                self.Ps[s] /= sum_Ps  # renormalize
            else:
                # if all valid moves were masked, make all valid moves equally probable
                log.error("All valid moves were masked, doing a workaround. Please check your NN training process.")
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        num_moves = len(moves)
        if is_root:
            # dirichlet noise for exploration
            eps = self.config.noise_eps
            noise = np.random.dirichlet([self.config.dirichlet_alpha] * num_moves)
        else:
            eps = 0
            noise = np.zeros(num_moves) # [0] * num_moves (inconsistent with above)

        # No leaf node, traverse tree
        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound by running one bubble sort iteration
        for i, move in enumerate(moves):
            a = PrecomputingMoves.move_index_hash[move]
            if (s, a) in self.Qsa:
                q = self.Qsa[(s, a)]
                u = self.config.cpuct * \
                    ((1-eps) * self.Ps[s][a] + eps * noise[i]) * \
                    math.sqrt(self.Ns[s]) / (1 + self.Nsa[(s, a)])
            else:
                q = 0
                u = self.config.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + self.config.noise_eps)  # Q = 0

            if q + u > cur_best:
                cur_best = u
                best_act = a

        a = best_act
        move = PrecomputingMoves.action_space_vector[a]
        # Flipping the move back around. Much more efficient than using bigger architecture, 
        # more labels, masking those labels...
        if board.moving_side: move = board.flip_move(move)
        board.make_move(move)
        v = self.search(board)
        board.reverse_move()

        # Update Qsa, Nsa and Ns
        if (s, a) in self.Qsa:
            self.Nsa[(s, a)] += 1
            self.Qsa[(s, a)] = ((self.Nsa[(s, a)] - 1) * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)])
        else:
            self.Nsa[(s, a)] = 1
            self.Qsa[(s, a)] = v

        self.Ns[s] += 1
        return -v

    @time_benchmark
    def get_probability_distribution(self, board: Board, bitboards: list, moves=None, tau=1):
        """
        This function performs numMCTSSims simulations of MCTS on ```board```.
        :return: probs: a policy vector where the probability of the ith action is proportional to 
        Nsa[(s,a)]**(1./temp)
        :param tau: parameter controlling exploration
        :param bitboards: bitboards of current state
        """
        for i in range(self.config.simulations_per_move):
            # print(f"starting simulation n. {i}")
            self.search(board, is_root=True, bitboards=bitboards, moves=moves)

        s = board.zobrist_key
        # Selcting valid moves from current board position
        visit_counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(PrecomputingMoves.action_space)]

        # Choose best move ...
        # ... deterministically for competition
        if not tau:
            best_a = np.random.choice(np.argmax(visit_counts).flatten())
            probs = [0] * len(visit_counts)
            probs[best_a] = 1
            return probs
        # ... stochastically for exploration
        visit_counts = [c ** round(1. / tau, 2) for c in visit_counts]
        counts_sum = float(sum(visit_counts))
        probs = [c / counts_sum for c in visit_counts]# renormalize
        return probs

    @staticmethod
    def best_action_from_pi(board: Board, pi):
        """
        :return: the move corresponding to the maximum value in the probability distribution of search
        NOTE: the perspective-dependent move is readjusted to the absolute squares
        """
        a = np.random.choice(np.argmax(pi).flatten())
        move = PrecomputingMoves.action_space_vector[a]
        return board.flip_move(move) if board.moving_side else move