import numpy as np

from game_of_life.domain.grid import Grid


def assert_raises(expected_error, action) -> None:
    try:
        action()
    except expected_error:
        return

    raise AssertionError(f"Expected {expected_error.__name__} to be raised.")


def test_grid_starts_empty_with_height_by_width_shape() -> None:
    grid = Grid(width=5, height=4)

    assert grid.cells.shape == (4, 5)
    assert grid.width == 5
    assert grid.height == 4
    assert grid.cells.sum() == 0


def test_toggle_cell_switches_between_dead_and_alive() -> None:
    grid = Grid(width=5, height=4)

    grid.toggle_cell(2, 1)

    assert grid.is_alive(2, 1)
    assert grid.cells[1, 2] == 1

    grid.toggle_cell(2, 1)

    assert not grid.is_alive(2, 1)
    assert grid.cells[1, 2] == 0


def test_grid_copies_initial_cells() -> None:
    cells = np.array(
        [
            [0, 1],
            [1, 0],
        ]
    )

    grid = Grid(width=2, height=2, cells=cells)
    cells[0, 1] = 0

    assert grid.is_alive(1, 0)


def test_replace_cells_rejects_wrong_shape() -> None:
    grid = Grid(width=5, height=4)

    assert_raises(
        ValueError,
        lambda: grid.replace_cells(np.zeros((5, 4))),
    )


def test_clear_and_randomize_update_all_cells() -> None:
    grid = Grid(width=3, height=2)

    grid.randomize(alive_probability=1)
    assert grid.cells.sum() == 6

    grid.clear()
    assert grid.cells.sum() == 0
