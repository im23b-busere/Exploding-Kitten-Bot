import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class SandroBot(Bot):
    def __init__(self, name: str):
        super().__init__(name)
        self.last_see_the_future = -3
        self.top_three = []
        self.current_turn = 0
        self.cards_played_this_turn = 0
        self.card_played_this_turn = False

    def play(self, state: GameState) -> Optional[Card]:
        if self.card_played_this_turn:

            self.current_turn += 1
            self.cards_played_this_turn = 0

        see_the_future_available = [card for card in self.hand if card.card_type == CardType.SEE_THE_FUTURE]
        skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
        normal_cards = [card for card in self.hand if
                        card.card_type not in [CardType.DEFUSE, CardType.SEE_THE_FUTURE, CardType.SKIP]]
        defuse_card_available = [card for card in self.hand if card.card_type == CardType.DEFUSE]

        if see_the_future_available and self.current_turn - self.last_see_the_future > 2:
            self.last_see_the_future = self.current_turn
            self.cards_played_this_turn += 1
            self.card_played_this_turn = True
            return see_the_future_available[0]

        if self.top_three:
            next_card = self.top_three[0]

            if next_card.card_type == CardType.EXPLODING_KITTEN:
                if skip_cards:
                    self.cards_played_this_turn += 1
                    self.card_played_this_turn = True
                    return skip_cards[0]
                elif defuse_card_available:
                    return None
                else:
                    if normal_cards:
                        played_card = random.choice(normal_cards)
                        self.cards_played_this_turn += 1
                        self.card_played_this_turn = True
                        return played_card

            else:
                self.top_three.pop(0)
                return None

        if state.was_last_card_exploding_kitten and normal_cards:
            played_card = random.choice(normal_cards)
            normal_cards.remove(played_card)
            self.cards_played_this_turn += 1
            self.card_played_this_turn = True
            return played_card

        if skip_cards:
            self.cards_played_this_turn += 1
            self.card_played_this_turn = True
            return skip_cards[0]

        if defuse_card_available:
            return None

        if normal_cards:
            played_card = random.choice(normal_cards)
            normal_cards.remove(played_card)
            self.cards_played_this_turn += 1
            self.card_played_this_turn = True
            return played_card

        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        if self.top_three:
            safe_positions = [i for i, card in enumerate(self.top_three) if card.card_type != CardType.EXPLODING_KITTEN]
            if safe_positions:
                return safe_positions[0]
        return random.randint(0, state.cards_left)

    def see_the_future(self, state: GameState, top_three: List[Card]):
        self.top_three = top_three
        self.card_played_this_turn = False