import math

from rich import print
from tqdm.rich import tqdm

VERBOSE = 1
TEST_DATA = False


def load_input():
    with open("sample.txt" if TEST_DATA else "input.txt") as indata:
        return [int(line) for line in indata]


def part_1():
    indata = load_input()
    numbers_with_original_indexes = [(num, idx) for idx, num in enumerate(indata)]
    orig_index_to_num = {idx: num for (num, idx) in numbers_with_original_indexes}
    numbers = numbers_with_original_indexes.copy()
    # print(f"Starting buffer: {numbers}")
    for i in tqdm(range(len(numbers_with_original_indexes))):
        # find the new index of the number with original index i
        current_index = numbers.index((orig_index_to_num[i], i))
        number_and_idx = numbers[current_index]
        new_index = current_index + number_and_idx[0]
        # if the last element is going forward then need to move it one more
        # step, as it's also the first item (right before the 1st item in a
        # circular buffer).
        if current_index == len(numbers) - 1 and number_and_idx[0] > 0:
            new_index += 1
        while new_index < 0:
            # -1 because the 1st item (index 0) is already the last item
            # (i.e. it's after the last item because it's a circular buffer)
            new_index += len(numbers) - 1
        new_index %= len(numbers) - 1
        if VERBOSE > 0:
            print(f"Moving number {number_and_idx[0]} from index {current_index} to {new_index}")
        del numbers[current_index]
        numbers.insert(new_index, number_and_idx)
        if VERBOSE > 1:
            print(f"Current buffer: {numbers}")

    zero = [num for num in numbers if num[0] == 0]
    assert len(zero) == 1
    zero_idx = numbers.index(zero[0])
    if VERBOSE > 0:
        print(f"Found zero at index x")
    coordinates_idx = (
        (zero_idx + 1000) % len(numbers),
        (zero_idx + 2000) % len(numbers),
        (zero_idx + 3000) % len(numbers),
    )
    coordinates = numbers[coordinates_idx[0]][0] + numbers[coordinates_idx[1]][0] + numbers[coordinates_idx[2]][0]
    print(coordinates)


def part_2():
    decryption_key = 811589153
    number_of_rounds = 10
    indata = load_input()
    numbers_with_original_indexes = [(num * decryption_key, idx) for idx, num in enumerate(indata)]
    orig_index_to_num = {idx: num for (num, idx) in numbers_with_original_indexes}
    numbers = numbers_with_original_indexes.copy()
    # print(f"Starting buffer: {numbers}")
    len_numbers_1 = len(numbers) - 1
    if VERBOSE > 1:
        print(f"Starting buffer: {numbers}")
    for round_num in range(number_of_rounds):
        for i in range(len(numbers_with_original_indexes)):
            # find the new index of the number with original index i
            current_index = numbers.index((orig_index_to_num[i], i))
            number_and_orig_idx = numbers[current_index]
            shift = number_and_orig_idx[0]
            new_index = current_index + shift
            new_index %= len_numbers_1
            if VERBOSE > 2:
                print(f"Moving number {number_and_orig_idx[0]} from index {current_index} to {new_index}")
            del numbers[current_index]
            numbers.insert(new_index, number_and_orig_idx)
            if VERBOSE > 1:
                print(f"Current buffer: {numbers}")
        if VERBOSE > 0:
            print(f"Buffer after round {round_num+1}: {numbers}")

    zero = [num for num in numbers if num[0] == 0]
    assert len(zero) == 1
    zero_idx = numbers.index(zero[0])
    if VERBOSE > 0:
        print(f"Found zero at index x")
    coordinates_idx = (
        (zero_idx + 1000) % len(numbers),
        (zero_idx + 2000) % len(numbers),
        (zero_idx + 3000) % len(numbers),
    )
    coordinates = numbers[coordinates_idx[0]][0] + numbers[coordinates_idx[1]][0] + numbers[coordinates_idx[2]][0]
    print(coordinates)


if __name__ == "__main__":
    part_2()
