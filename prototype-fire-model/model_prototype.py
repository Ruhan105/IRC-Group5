"""A prototype cellular automata fire spread model."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import deque
import matplotlib.animation as animation
from copy import deepcopy
from typing import List


class FireModel:
    """
    A class for a simple fire simulation model.

    0 = river (blue)
    1 = flammable land (white)
    2 = fire (red)
    """

    def __init__(self, grid: List[List[int]]):
        """Initialise the fire model given a grid."""
        self.grid = np.array(grid)
        self.directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        self.grid_states = []

    def model_spread(self) -> int:
        """
        Simulate fire spread using BFS.

        Saves snapshots of grid state.
        """
        queue = deque()
        rows, cols = len(self.grid), len(self.grid[0])
        land = 0
        self.grid_states = []

        for i in range(rows):
            for j in range(cols):
                if self.grid[i][j] == 1:
                    land += 1
                if self.grid[i][j] == 2:
                    queue.append([i, j])

        while queue and land > 0:

            self.grid_states.append(deepcopy(self.grid))

            for _ in range(len(queue)):
                row, col = queue.popleft()

                for direction in self.directions:

                    next_i = row + direction[0]
                    next_j = col + direction[1]

                    if (next_i >= 0 and next_i < rows) and (
                         next_j >= 0 and
                         next_j < cols) and self.grid[next_i][next_j] == 1:

                        queue.append([next_i, next_j])
                        self.grid[next_i][next_j] = 2
                        land -= 1

        self.grid_states.append(deepcopy(self.grid))

    def animate_spread(self, grid_states: List[np.ndarray], save_file: bool):
        """Animate fire spread based on grid snapshots."""
        cmap = mpl.colors.ListedColormap(['blue', 'white', 'red'])

        fig, ax = plt.subplots()

        image = ax.imshow(self.grid, cmap=cmap, vmin=0, vmax=2)

        ax.set_xticks([])
        ax.set_yticks([])

        def animate(frame):
            image.set_array(grid_states[frame])
            return image,

        ani = animation.FuncAnimation(fig, animate, frames=len(grid_states),
                                      interval=500, blit=True)

        plt.show()

        if save_file:
            ani.save('test.gif', writer='pillow', fps=1)


if __name__ == "__main__":
    test = FireModel([[2, 1, 1, 1], [1, 1, 1, 1],
                     [0, 0, 0, 1], [1, 1, 1, 1]])

    test.model_spread()
    test.animate_spread(test.grid_states, False)
