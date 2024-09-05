from collections import deque

def findApproach(matrix):
    rows, cols = len(matrix), len(matrix[0])
    start = None
    target = None

    # Find the positions of "B" and "X"
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == "B":
                start = (i, j, "V")  # Start with the cuboid in a vertical position
            elif matrix[i][j] == "X":
                target = (i, j)

    # Initialize BFS queue and visited dictionary
    queue = deque([(start, [])])  # Each element in the queue is (position, path)
    visited = set()

    # Define possible moves
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        (x, y, cuboid_state), path = queue.popleft()

        if (x, y) == target:
            return ''.join(path)  # Combine the moves to form the approach

        visited.add((x, y, cuboid_state))

        # Try all possible moves
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy

            if 0 <= new_x < rows and 0 <= new_y < cols and 0 <= new_y < cols and 0 <= new_y < cols and 0 <= new_y < cols and 0 <= new_y < cols:
                new_state = cuboid_state  # Cuboid state remains the same by default

                # Check if cuboid needs to change its orientation
                if matrix[new_x][new_y] == "1":
                    if cuboid_state == "H":
                        new_state = "V"
                    else:
                        new_state = "H"

                new_position = (new_x, new_y, new_state)

                if new_position not in visited:
                    new_path = path + ["R"] if new_state == "H" else path + ["D"]
                    queue.append((new_position, new_path))

    return ""  # No valid approach found

# Example usage:
matrix = ["1110000000", "1B11110000", "1111111110", "00000011x11", "0000001110"]
if __name__ =="__main__":
    approach = findApproach(matrix)
    print(approach)  # Output: "RRDRRRD" or similar approaches

# for dx, dy in moves:
#     if state == "S":
#         if dx == 1:
#             new_x1, new_x2 = x1 + 2 * dx, x2 + dx
#             new_y1, new_y2 = y1 + dy, y2 + dy
#         elif dx == -1:
#             new_x1, new_x2 = x1 + dx, x2 + 2 * dx  # If dx==0,no change
#             new_y1, new_y2 = y1 + dy, y2 + dy
#
#         if dy == 1:
#             new_y1, new_y2 = y1 + dy, y2 + 2 * dy  # If dy==0,no change
#         elif dy == -1:
#             new_y1, new_y2 = y1 + 2 * dy, y2 + dy
#
#         if dy > 0:
#             new_y1, new_y2 = y1 + 2 * dy, y2 + dy
#         else:
#             new_y1, new_y2 = y1 + dy, y2 + 2 * dy  # If dy==0,no change
#         new_state = "HH" if dx != 0 else
#     if state == "VV":
#         new_x1, new_x2 = x1 + dx, x2 + dx
#         if dy > 0:
#             new_y1, new_y2 = y1 + 2 * dy, y2 + dy
#         else:
#             new_y1, new_y2 = y1 + dy, y2 + 2 * dy  # If dy==0,no change
#         if dx == 0:
#             new_state = "S"
#         else:
#             new_state = state
#     if state == "HH":
#         if dx > 0:
#             new_x1, new_x2 = x1 + 2 * dx, x2 + dx
#         else:
#             new_x1, new_x2 = x1 + dx, x2 + 2 * dx  # If dx==0,no change
#         new_y1, new_y2 = y1 + dy, y2 + dy
#         if dx == 0:
#             new_state = "S"
#         else:
#             new_state = state