"""Simple sum function for kata practice."""


def sum_numbers(a: int | float, b: int | float) -> int | float:
    """
    Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of a and b

    Examples:
        >>> sum_numbers(2, 3)
        5
        >>> sum_numbers(-1, 1)
        0
        >>> sum_numbers(1.5, 2.5)
        4.0
    """
    return a + b


def sum_list(numbers: list[int | float]) -> int | float:
    """
    Calculate the sum of a list of numbers.

    Args:
        numbers: List of numbers to sum

    Returns:
        The sum of all numbers in the list

    Raises:
        ValueError: If the list is empty

    Examples:
        >>> sum_list([1, 2, 3, 4, 5])
        15
        >>> sum_list([10, -5, 3])
        8
        >>> sum_list([1.5, 2.5, 3.0])
        7.0
    """
    if not numbers:
        raise ValueError("Cannot sum an empty list")

    return sum(numbers)


def sum_positive(numbers: list[int | float]) -> int | float:
    """
    Calculate the sum of only positive numbers in a list.

    Args:
        numbers: List of numbers

    Returns:
        The sum of all positive numbers (> 0) in the list

    Examples:
        >>> sum_positive([1, -2, 3, -4, 5])
        9
        >>> sum_positive([-1, -2, -3])
        0
        >>> sum_positive([1.5, -2.5, 3.5])
        5.0
    """
    return sum(n for n in numbers if n > 0)
