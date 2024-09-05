from typing import List
from collections import deque


class Solution:
    def bfs(self, i, j, t, heights):
        m, n = len(heights), len(heights[0])

        is_edge = i == 0 or j == 0 or i == m - 1 or j == n - 1
        if is_edge:
            t[i][j] = ((i == 0 or j == 0), (i == m - 1 or j == n - 1))

        if t[i][j][0] is not None and t[i][j][1] is not None:
            return t[i][j]  # searched

        print(t)

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        pacific, atlantic = False, False
        for di, dj in directions:
            if 0 <= i + di < m and 0 <= j + dj < n:
                pacific = pacific or (heights[i][j] >= heights[i + di][j + dj] and self.bfs(i + di, j + dj, t, heights)[0])
                atlantic = atlantic or (heights[i][j] >= heights[i + di][j + dj] and self.bfs(i + di, j + dj, t, heights)[1])
        t[i][j] = (pacific, atlantic)

    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        m, n = len(heights), len(heights[0])
        t = [[(None, None) for _ in range(n)] for _ in range(m)]
        res = []
        for i in range(m):
            for j in range(n):
                if all(self.bfs(i, j, t, heights)):
                    res.append([i,j])

        return res


question = Solution()
answer = question.pacificAtlantic([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]])
print(answer)
