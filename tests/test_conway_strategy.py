import numpy as np

from game_of_life.domain.grid import Grid
from game_of_life.strategies import ConwayEvolutionStrategy, HighLifeEvolutionStrategy


def test_conway_rotates_blinker_pattern() -> None:
    grid = Grid(
        width=5,
        height=5,
        cells=np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0],
            ]
        ),
    )

    next_cells = ConwayEvolutionStrategy().calculate_next_state(grid)

    assert np.array_equal(
        next_cells,
        np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ]
        ),
    )


def test_conway_keeps_stable_block_pattern() -> None:
    cells = np.array(
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ]
    )
    grid = Grid(width=4, height=4, cells=cells)

    next_cells = ConwayEvolutionStrategy().calculate_next_state(grid)

    assert np.array_equal(next_cells, cells)


def test_highlife_births_dead_cell_with_six_neighbors() -> None:
    grid = Grid(
        width=3,
        height=3,
        cells=np.array(
            [
                [1, 1, 1],
                [1, 0, 1],
                [1, 0, 0],
            ]
        ),
    )

    conway_center = ConwayEvolutionStrategy().calculate_next_state(grid)[1, 1]
    highlife_center = HighLifeEvolutionStrategy().calculate_next_state(grid)[1, 1]

    assert conway_center == 0
    assert highlife_center == 1
