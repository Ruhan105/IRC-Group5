"""A prototype cellular automata fire spread model."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import deque
import matplotlib.animation as animation
from copy import deepcopy
from typing import List
import pandas as pd
# import random


class FireModel:
    """
    A class for a simple fire simulation model.

    0 = river (blue)
    1 = flammable land (white)
    2 = fire (red)
    """

    def __init__(self, grid: np.array):
        """Initialise the fire model given a grid."""
        self.grid = np.array(grid)
        self.directions = [
            [0, 0],
            [0, 1],
            [1, 1],
            [1, 0],
            [0, -1],
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [1, -1]
            ]
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
                    # randomly chooses whether or not
                    # to spread in this direction

                    num = np.random.randint(0, 2)

                    if num > 0:
                        next_i = row + direction[0]
                        next_j = col + direction[1]

                        if (next_i >= 0 and
                            next_i < rows) and (
                            next_j >= 0 and
                                next_j < cols) and self.grid[
                                next_i][next_j] == 1:

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
                                      interval=50, blit=True)

        plt.show()

        if save_file:
            ani.save('test.gif', writer='pillow', fps=15)


def sample_objects(n):
    """
    Generate 2-d homogeneous Poisson process realisations.

    Utilises a simple Gaussian intensity function.
    """
    x_vals = np.linspace(-1, 1, n)
    y_vals = np.linspace(-1, 1, n)
    x_grid, y_grid = np.meshgrid(x_vals, y_vals)

    # Flatten the grid and create DataFrame
    grid_df = pd.DataFrame({
        'x': x_grid.ravel(),
        'y': y_grid.ravel()
    })

    # Compute the intensity function
    grid_df['r'] = np.exp(-(grid_df['x']**2 + grid_df['y']**2)/2)
    grid_df['lambda'] = grid_df['r']  # Intensity function

    # Compute expectation
    cell_area = (6 / n) ** 2  # Area of each grid cell
    expected_total = np.sum(grid_df['lambda'] * cell_area)

    # Sample the actual number of points from a Poisson distribution
    n_sampled = np.random.poisson(expected_total)
    print(n_sampled)

    func = np.exp(-(x_grid**2 + y_grid**2)/2)

    weights = func.flatten() / sum(func.flatten())

    sampled_points = np.random.choice(n*n, size=n_sampled,
                                      p=weights, replace=False)

    sampled_rows, sampled_cols = np.unravel_index(sampled_points, (n, n))

    positions = np.array(list(zip(sampled_rows, sampled_cols)))

    return positions


if __name__ == "__main__":

    arr = np.ones((100, 100))

    for i in sample_objects(100):
        arr[i[0]][i[1]] = 0

    arr[50][50] = 2
    test = FireModel(arr)

    test.model_spread()
    test.animate_spread(test.grid_states, False)
