import pytest

from gemini import exchange


class TestExchange:
    """
    Rewrite tests to pytest
    """

    def test_errors(self):
        a = exchange.Account(1000)
        with pytest.raises(ValueError):
            a.enter_position('Long', -500, 10)
            a.enter_position('Long', 500, -10)
            a.enter_position('Long', 2000, 10)
        # Enter valid position
        a.enter_position('Long', 250, 10)
        a.enter_position('Short', 250, 10)
        long = a.positions[0]
        short = a.positions[1]
        with pytest.raises(ValueError):
            a.close_position(long, 0.5, -20)
            a.close_position(long, 1.01, -20)
            a.close_position(long, -0.5, 20)
            a.close_position(short, 0.5, -20)
            a.close_position(short, -0.5, 20)
