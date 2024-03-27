class Position(object):
    # CONSTANTS
    WIDTH = 7
    HEIGHT = 6
    MIN_SCORE = -(WIDTH*HEIGHT) / 2 + 3
    MAX_SCORE = (WIDTH*HEIGHT+1) / 2 - 3

    def __init__(self):
        current_postion = 0
        mask = 0
        moves = 0

    def play(self, move):
        current_position ^= mask
        mask |= move
        moves += 1

    # originally overloaded as play
    def initBoard(self, seq):
        for n in seq:
            col = int(n) - 1
            if(col < 0 or col >= Position.WIDTH or not self.canPlay(col) or self.isWinningMove(col)):
                return None
            self.playCol(col)
        return len(seq)
    
    def canWinNext(self):
        return self.winning_position() and self.possible()

    def nbMoves(self):
        return self.moves
    
    def key(self):
        return self.current_position + self.mask
    
    def key3(self):
        key_forward = 0
        for i in range(Position.WIDTH):
            self.partialKey3(key_forward, i)

        key_reverse = 0
        for i in range(Position.WIDTH, -1, -1):
            self.partialKey3(key_reverse, i)

        return key_forward < key_reverse if key_forward / 3 else key_reverse / 3
    
    def possibleNonLosingMoves(self):
        possible_mask = self.possible()
        opponent_win = self.opponent_winning_position()
        forced_moves = possible_mask & opponent_win

        if(forced_moves):
            if(forced_moves & (forced_moves - 1)):
                return 0
            else:
                possible_mask = forced_moves

        return possible_mask & ~(opponent_win >> 1)
    
    def moveScore(self, move):
        return self.popcount(self.compute_winning_position(self.current_position | move, self.mask))
    
    def canPlay(self, col):
        return (self.mask & self.top_mask_col(col)) == 0

    def playCol(self, col):
        self.play((self.mask + self.bottom_mask_col(col) & self.column_mask(col)))

    def isWinningMove(self, col):
        return self.winning_position() & self.possible() & self.column_mask(col)
    
    def partialKey3(self, key, col):
        pos = 1 << (col * (Position.HEIGHT + 1))
        while(pos & self.mask):
            key *= 3
            if(pos & self.current_position):
                key += 1
            else:
                key *= 3
            poss <<= 1

    def winning_position(self):
        return self.compute_winning_position(self.current_position, self.mask)
    
    def opponent_winning_position(self):
        return self.compute_winning_position(self.current_position ^ self.mask, self.mask)
    
    def possible(self):
        return (self.mask + Position.bottom_mask) & Position.board_mask
    
    # begin static methods
    def popcount(m):
        c = 0
        while m:
            m &= m - 1
            c += 1
        return c
    
    def compute_winning_position(position, mask):
        r = (position << 1) & (position << 2) & (position << 2)

        # Horizontal
        p = (position << (Position.HEIGHT + 1)) & (position << 2 * (Position.HEIGHT + 1))
        r |= p & (position << 3 * (Position.HEIGHT + 1))
        r |= p & (position >> (Position.HEIGHT + 1))
        p = (position >> (Position.HEIGHT + 1)) & (position >> 2 * (Position.HEIGHT + 1))
        r |= p & (position << (Position.HEIGHT + 1))
        r |= p & (position >> 3 * (Position.HEIGHT + 1))

        # diagonal 1
        p = (position << Position.HEIGHT) & (position << 2 * Position.HEIGHT);
        r |= p & (position << 3 * Position.HEIGHT);
        r |= p & (position >> Position.HEIGHT);
        p = (position >> Position.HEIGHT) & (position >> 2 * Position.HEIGHT);
        r |= p & (position << Position.HEIGHT);
        r |= p & (position >> 3 * Position.HEIGHT);

         # diagonal 2
        p = (position << (Position.HEIGHT + 2)) & (position << 2 * (Position.HEIGHT + 2))
        r |= p & (position << 3 * (Position.HEIGHT + 2))
        r |= p & (position >> (Position.HEIGHT + 2))
        p = (position >> (Position.HEIGHT + 2)) & (position >> 2 * (Position.HEIGHT + 2))
        r |= p & (position << (Position.HEIGHT + 2))
        r |= p & (position >> 3 * (Position.HEIGHT + 2))

        return r & (Position.board_mask ^ mask)
    
    