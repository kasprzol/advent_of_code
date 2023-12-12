import re
import dataclasses
import functools
import itertools
from collections.abc import Iterable, Sequence
from enum import StrEnum
from typing import NamedTuple

import tqdm


class Type(StrEnum):
    FIVE = "FIVE"
    FOUR = "FOUR"
    FULL = "FULL"
    THREE = "THREE"
    TWO_PAIR = "TWO_PAIR"
    PAIR = "PAIR"
    HIGH_CARD = "HIGH_CARD"

type_to_value = {
    Type.FIVE: 1,
    Type.FOUR: 2,
    Type.FULL: 3,
    Type.THREE: 4,
    Type.TWO_PAIR: 5,
    Type.PAIR: 6,
    Type.HIGH_CARD: 7,
}

strength_to_value = {card: idx for idx, card in enumerate("AKQJT98765432")}

@dataclasses.dataclass
class Hand:
    cards: str
    _type:Type = dataclasses.field(init=False)

    @functools.cached_property
    def type_(self)->Type:
        different_cards = set(self.cards)

        match len(different_cards):
            case 1:
                t = Type.FIVE
            case 2:
                max_same = max(self.cards.count(card) for card in different_cards)
                if max_same == 4:
                    t = Type.FOUR
                else:
                    t = Type.FULL
            case 3:
                counts = {card: self.cards.count(card) for card in different_cards}
                three = any(counts[card] == 3 for card in counts)
                if three:
                    t = Type.THREE
                else:
                    t = Type.TWO_PAIR
            case 4:
                t = Type.PAIR
            case 5:
                t = Type.HIGH_CARD
        self._type = t
        return t
    
    def __lt__(self, other):
        if not isinstance(other, Hand):
            return NotImplemented
        if other is self:
            return False
        other_t = other.type_
        my_t = self.type_

        if other_t != my_t:
            return type_to_value[my_t] > type_to_value[other_t]
        for my_card, other_card in zip(self.cards, other.cards):
            if my_card != other_card:
                return strength_to_value[my_card] > strength_to_value[other_card]
        return False
    

def part1():
    value = 0
    hands_and_bids = []
    
    for line in open("input.txt").readlines():
        line = line.strip()
        hand, bid = line.split()
        bid = int(bid)
        hands_and_bids.append((Hand(hand), bid))

    hands_and_bids.sort(key=lambda x: x[0])
    for rank, (hand, bid) in enumerate(hands_and_bids, 1):
        value += rank * bid
    print(hands_and_bids)

    print(f"The value is {value}")

################################################################################

strength_to_value2 = {card: idx for idx, card in enumerate("AKQT98765432J")}

@dataclasses.dataclass
class Hand2(Hand):

    @functools.cached_property
    def type_(self)->Type:
        different_cards = set(self.cards) - {"J"}
        jokers = self.cards.count("J")

        if not jokers:
            return super().type_

        match len(different_cards):
            case 0:
                t = Type.FIVE
            case 1:
                t = Type.FIVE
            case 2:
                max_same = max(self.cards.count(card) for card in different_cards)
                if max_same + jokers == 4:
                    t = Type.FOUR
                else:
                    t = Type.FULL
            case 3:
                # two possible scenarios: (X, Y, Z are random cards)
                # X, Y, Z, J, J
                # X, Y, Z, Z, J
                t = Type.THREE
            case 4:
                assert jokers == 1, self.cards
                t = Type.PAIR
        self._type = t
        return t
    
    def __lt__(self, other):
        if not isinstance(other, Hand2):
            return NotImplemented
        if other is self:
            return False
        other_t = other.type_
        my_t = self.type_

        if other_t != my_t:
            return type_to_value[my_t] > type_to_value[other_t]
        for my_card, other_card in zip(self.cards, other.cards):
            if my_card != other_card:
                return strength_to_value2[my_card] > strength_to_value2[other_card]
        return False
    

def part2():
    value = 0
    hands_and_bids = []
    
    for line in open("input.txt").readlines():
        line = line.strip()
        hand, bid = line.split()
        bid = int(bid)
        hands_and_bids.append((Hand2(hand), bid))

    hands_and_bids.sort(key=lambda x: x[0])
    for rank, (hand, bid) in enumerate(hands_and_bids, 1):
        value += rank * bid
    print(hands_and_bids)

    print(f"The value is {value}")

if __name__ == '__main__':
    part2()
