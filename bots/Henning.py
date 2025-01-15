import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class Henning(Bot):
    def play(self, state: GameState) -> Optional[Card]:
        # Prioritize SEE THE FUTURE
        see_the_future_cards = [card for card in self.hand if card.card_type == CardType.SEE_THE_FUTURE]
        if see_the_future_cards:
            return see_the_future_cards[0]

        # Second priority is to play SKIP
        skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
        if skip_cards:
            return random.choice(skip_cards)

        # Play other cards except DEFUSE
        playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
        if playable_cards:
            return random.choice(playable_cards)

        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        # Insert the Exploding Kitten card back into a random position in the deck
        return random.randint(0, state.cards_left)


    def see_the_future(self, state: GameState, top_three: List[Card]):
        # Implement a strategy for SEE_THE_FUTURE card
        if top_three and top_three[0].card_type == CardType.EXPLODING_KITTEN:
            print("I see an Exploding Kitten at the top!")
            skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
            if skip_cards:
                return skip_cards[0]
        # If no Exploding Kitten at the top or no SKIP cards, do nothing
        return None