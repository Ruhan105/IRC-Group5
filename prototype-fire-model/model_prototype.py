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
    3 = burnt (orange)
    """

    def __init__(self, grid: np.array,
                 temperatures: np.array, params=[0, [0, 0]]):
        """Initialise the fire model given a grid and wind parameters."""
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
        self.params = params
        self.steps = 0
        self.normalised_wind = 1/(1+np.exp(-self.params[0]))
        self.temperatures = temperatures

    def wind_affect(self, direction):
        """
        Calculate wind affect on probabilities.

        s
        """
        # wind_coeff = np.exp(0.1783*velocity)
        # find weighted mean over each neighbouring pixel
        a = np.array(direction) / np.linalg.norm(self.params[1])
        b = np.array(self.params[1]) / np.linalg.norm(self.params[1])

        res = self.normalised_wind * np.dot(a, b)

        return 0 if self.params[1] == [0, 0] else res

    def model_spread(self) -> int:
        """
        Simulate fire spread using BFS.

        Saves snapshots of grid state.
        params - [windSpeed, direction]

        """
        queue = deque()
        rows, cols = len(self.grid), len(self.grid[0])
        land = 0
        self.grid_states = []
        self.steps = 0

        for i in range(rows):
            for j in range(cols):
                if self.grid[i][j] in [1, 4]:
                    land += 1
                if self.grid[i][j] == 2:
                    queue.append([i, j])

        while queue and land > 0:

            self.grid_states.append(deepcopy(self.grid))

            for _ in range(len(queue)):
                row, col = queue.popleft()
                self.grid[row][col] = 3

                for direction in self.directions:
                    # randomly chooses whether or not
                    # to spread in this direction
                    next_i = row + direction[0]
                    next_j = col + direction[1]

                    if (next_i >= 0 and
                        next_i < rows) and (
                        next_j >= 0 and
                            next_j < cols) and self.grid[
                            next_i][next_j] == 1:

                        initial = 0.25
                        temp = self.temperatures[next_i][next_j]

                        p = min(initial*(1 + self.wind_affect(
                                    direction)
                                    )*np.exp(0.3*(temp - 0.4)), 0.9)

                        # if self.grid[next_i][next_j] == 4:
                        #     p = min(1, 1.5*p)

                        num = np.random.choice([0, 1], 1,
                                               p=[1 - p, p])

                        if self.grid[next_i][next_j] == 4:
                            num = 1

                        if num > 0:

                            queue.append([next_i, next_j])
                            self.grid[next_i][next_j] = 2
                            land -= 1

                            self.steps += 1

        self.grid_states.append(deepcopy(self.grid))

    def animate_spread(self, grid_states: List[np.ndarray], save_file: bool):
        """Animate fire spread based on grid snapshots."""
        cmap = mpl.colors.ListedColormap(['blue',
                                          'white', 'red', 'orange', 'brown'])

        fig, ax = plt.subplots()

        image = ax.imshow(self.grid, cmap=cmap, vmin=0, vmax=4)

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

    def get_final_state(self):
        """Getter method."""
        return self.grid_states[-1]


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
    cell_area = (10 / n) ** 2  # Area of each grid cell
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


def fire_heatmap(states):
    """
    Generate probability heatmap based on final states.

    takes an List of np arrays
    """
    sum_array = np.sum(states, axis=0)

    normalised_arr = sum_array/np.max(sum_array)

    fig, ax = plt.subplots()

    fig.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(0, 1), cmap='coolwarm'),
             ax=ax, orientation='vertical', label='Fire Spread Probability')

    plt.imshow(normalised_arr, cmap="coolwarm", interpolation="nearest")

    plt.show()


def temperature_map(n):
    """Generate temperature grid."""
    xgrid = np.linspace(-5, 5, n)
    ygrid = np.linspace(-5, 5, n)
    x, y = np.meshgrid(xgrid, ygrid)  # Create mesh grid

    # z = np.abs(np.sin(0.5* np.pi*x)*np.sin(0.5* np.pi*y) + 2*np.cos(1/6 * np.pi*y*x))
    z = 1/2*np.exp(-(1/2)*(x**2 + y**2)/2)
    normz = z / np.max(z)
    plt.imshow(normz, cmap="coolwarm", interpolation="nearest")

    return normz


def generate_boundary(n, grid):
    """Generate spread boundary."""
    x_c, y_c = n // 2, n // 2
    radius = 60

    y, x = np.ogrid[:n, :n]
    u = x - x_c
    v = y - y_c
    mask = (u/1.2) ** 2 + (v) ** 2 > (radius)**2
    mask2 = (u/1.2) ** 2 + (v) ** 2 < (radius)**2 + 300
    grid[mask == mask2] = 0


if __name__ == "__main__":

    n = 200

    grid = np.ones((n, n))

    temperatures = temperature_map(n)

    for i in sample_objects(n):
        grid[i[0]][i[1]] = 4

    generate_boundary(n, grid)

    grid[n//2][n//2] = 2
    test = FireModel(grid, temperatures, [0, [1, 1]])

    test.model_spread()
    test.animate_spread(test.grid_states, False)

    states = []
    for i in range(20):
        test = FireModel(grid, temperatures, [20, [1, 1]])
        test.model_spread()

        states.append(test.get_final_state())

    fire_heatmap(states)
# Also need to add temperature, fuel, accurate locations for trees/ rivers.
