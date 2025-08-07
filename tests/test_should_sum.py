"""Tests for the sum kata functions."""

import pytest

from src.sum import sum_list, sum_numbers, sum_positive


class TestShouldSumNumbers:
    """Test suite for the sum_numbers function."""

    def test_sum_positive_integers(self):
        """Test adding two positive integers."""
        assert sum_numbers(2, 3) == 5
        assert sum_numbers(10, 20) == 30
        assert sum_numbers(100, 200) == 300

    def test_sum_negative_integers(self):
        """Test adding negative integers."""
        assert sum_numbers(-1, -1) == -2
        assert sum_numbers(-5, -10) == -15
        assert sum_numbers(-100, -200) == -300

    def test_sum_mixed_sign_integers(self):
        """Test adding integers with different signs."""
        assert sum_numbers(-5, 10) == 5
        assert sum_numbers(10, -5) == 5
        assert sum_numbers(-10, 10) == 0

    def test_sum_with_zero(self):
        """Test adding with zero."""
        assert sum_numbers(0, 0) == 0
        assert sum_numbers(5, 0) == 5
        assert sum_numbers(0, -5) == -5

    def test_sum_floats(self):
        """Test adding floating point numbers."""
        assert sum_numbers(1.5, 2.5) == 4.0
        assert sum_numbers(0.1, 0.2) == pytest.approx(0.3)
        assert sum_numbers(-1.5, 1.5) == 0.0

    def test_sum_mixed_types(self):
        """Test adding integers and floats."""
        assert sum_numbers(1, 2.5) == 3.5
        assert sum_numbers(2.5, 1) == 3.5
        assert sum_numbers(-1, 2.5) == 1.5


class TestShouldSumList:
    """Test suite for the sum_list function."""

    def test_sum_list_positive_integers(self):
        """Test summing a list of positive integers."""
        assert sum_list([1, 2, 3, 4, 5]) == 15
        assert sum_list([10, 20, 30]) == 60
        assert sum_list([1]) == 1

    def test_sum_list_negative_integers(self):
        """Test summing a list of negative integers."""
        assert sum_list([-1, -2, -3]) == -6
        assert sum_list([-10, -20, -30]) == -60
        assert sum_list([-1]) == -1

    def test_sum_list_mixed_integers(self):
        """Test summing a list with mixed positive and negative integers."""
        assert sum_list([1, -2, 3, -4, 5]) == 3
        assert sum_list([10, -5, 3]) == 8
        assert sum_list([-10, 10]) == 0

    def test_sum_list_with_floats(self):
        """Test summing a list containing floats."""
        assert sum_list([1.5, 2.5, 3.0]) == 7.0
        assert sum_list([0.1, 0.2, 0.3]) == pytest.approx(0.6)
        assert sum_list([1, 2.5, 3]) == 6.5

    def test_sum_list_empty_raises_error(self):
        """Test that summing an empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot sum an empty list"):
            sum_list([])

    def test_sum_list_single_element(self):
        """Test summing a list with a single element."""
        assert sum_list([42]) == 42
        assert sum_list([-42]) == -42
        assert sum_list([3.14]) == 3.14

    def test_sum_list_with_zeros(self):
        """Test summing a list containing zeros."""
        assert sum_list([0, 0, 0]) == 0
        assert sum_list([1, 0, 2, 0, 3]) == 6
        assert sum_list([0, -1, 0, 1]) == 0


class TestShouldSumPositive:
    """Test suite for the sum_positive function."""

    def test_sum_positive_all_positive(self):
        """Test summing when all numbers are positive."""
        assert sum_positive([1, 2, 3, 4, 5]) == 15
        assert sum_positive([10, 20, 30]) == 60
        assert sum_positive([0.5, 1.5, 2.5]) == 4.5

    def test_sum_positive_all_negative(self):
        """Test summing when all numbers are negative."""
        assert sum_positive([-1, -2, -3]) == 0
        assert sum_positive([-10, -20, -30]) == 0
        assert sum_positive([-0.5, -1.5, -2.5]) == 0

    def test_sum_positive_mixed_values(self):
        """Test summing with mixed positive and negative values."""
        assert sum_positive([1, -2, 3, -4, 5]) == 9
        assert sum_positive([-1, 2, -3, 4, -5, 6]) == 12
        assert sum_positive([1.5, -2.5, 3.5]) == 5.0

    def test_sum_positive_with_zeros(self):
        """Test that zeros are not included in the sum."""
        assert sum_positive([0, 0, 0]) == 0
        assert sum_positive([0, 1, 0, 2]) == 3
        assert sum_positive([-1, 0, 1]) == 1

    def test_sum_positive_empty_list(self):
        """Test summing an empty list returns 0."""
        assert sum_positive([]) == 0

    def test_sum_positive_single_element(self):
        """Test with single element lists."""
        assert sum_positive([5]) == 5
        assert sum_positive([-5]) == 0
        assert sum_positive([0]) == 0

    def test_sum_positive_large_numbers(self):
        """Test with large numbers."""
        assert sum_positive([1000000, -500000, 2000000]) == 3000000
        assert sum_positive([1e6, -5e5, 2e6]) == 3e6


class TestShouldSumEdgeCases:
    """Test suite for edge cases and special scenarios."""

    def test_sum_numbers_large_values(self):
        """Test sum_numbers with very large values."""
        assert sum_numbers(1e10, 2e10) == 3e10
        assert sum_numbers(999999999, 1) == 1000000000

    def test_sum_list_many_elements(self):
        """Test sum_list with many elements."""
        large_list = list(range(1, 101))  # 1 to 100
        assert sum_list(large_list) == 5050  # Sum of 1 to 100

        large_negative_list = list(range(-50, 51))  # -50 to 50
        assert sum_list(large_negative_list) == 0

    def test_floating_point_precision(self):
        """Test handling of floating point precision issues."""
        # Using pytest.approx for floating point comparisons
        result = sum_numbers(0.1, 0.2)
        assert result == pytest.approx(0.3)

        result = sum_list([0.1] * 10)
        assert result == pytest.approx(1.0)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 1, 2),
        (0, 0, 0),
        (-1, 1, 0),
        (1.5, 2.5, 4.0),
        (100, -50, 50),
    ],
)
def test_sum_numbers_parametrised(a, b, expected):
    """Parametrised test for sum_numbers function."""
    assert sum_numbers(a, b) == expected


@pytest.mark.parametrize(
    "numbers,expected",
    [
        ([1, 2, 3], 6),
        ([-1, -2, -3], -6),
        ([1, -1], 0),
        ([1.5, 2.5], 4.0),
        ([0, 0, 0], 0),
    ],
)
def test_sum_list_parametrised(numbers, expected):
    """Parametrised test for sum_list function."""
    assert sum_list(numbers) == expected
