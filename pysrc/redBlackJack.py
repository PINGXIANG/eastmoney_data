from fractions import Fraction


class Solution:
    def __init__(self):
        self.Es = None

    def E(self, black: int, red: int, b: int, r: int, Es: list) -> float:
        if b == 13:
            Es[b][r] = 0
        elif r == 13:
            Es[b][r] = r - b

        if Es[b][r] is None:
            Eb = Fraction(black - b, black + red - b - r) * self.E(black, red, b + 1, r, Es) if b < black else 0
            Er = Fraction(red - r, black + red - b - r) * self.E(black, red, b, r + 1, Es) if r < red else 0
            Es[b][r] = Eb + Er

        return Es[b][r]

    def redBlackJack(self, black: int, red: int):
        Es = [[None for _ in range(black + 1)] for _ in range(red + 1)]
        Es[black][red] = 0
        res = self.E(black, red, 0, 0, Es)
        self.Es = Es
        return res


s = Solution()
s.redBlackJack(13, 13)
print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in s.Es]))
