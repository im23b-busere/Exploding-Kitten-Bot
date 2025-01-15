import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class Enzo(Bot):
    def play(self, state: GameState) -> Optional[Card]:
        # Get the number of alive bots
        alive_bots = state.alive_bots

        # Track the probability of drawing an Exploding Kitten
        exploding_kitten_probability = self.calculate_exploding_kitten_probability(state)

        # Defensive strategy when more bots are alive
        if alive_bots > 2:
            # Prioritize SEE THE FUTURE
            see_the_future_cards = [card for card in self.hand if card.card_type == CardType.SEE_THE_FUTURE]
            if see_the_future_cards:
                return see_the_future_cards[0]

            # Second priority is to play SKIP if the probability of drawing an Exploding Kitten is high
            if exploding_kitten_probability > 0.3:
                skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
                if skip_cards:
                    return random.choice(skip_cards)

        # Aggressive strategy when fewer bots are alive
        else:
            # Play any card except DEFUSE
            playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
            if playable_cards:
                return random.choice(playable_cards)

        # Default to playing any card except DEFUSE if no specific strategy applies
        playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
        if playable_cards:
            return random.choice(playable_cards)

        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        # Use DEFUSE card if available
        defuse_cards = [card for card in self.hand if card.card_type == CardType.DEFUSE]
        if defuse_cards:
            self.hand.remove(defuse_cards[0])
            # Place the Exploding Kitten back in a strategic position
            return random.randint(1, state.cards_left - 1)

        # If no DEFUSE card, the bot loses
        return -1

    def see_the_future(self, state: GameState, top_three: List[Card]):
        # Implement a strategy for SEE_THE_FUTURE card
        if top_three[0].card_type == CardType.EXPLODING_KITTEN:
            print("I see an Exploding Kitten on the top!")
            skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
            if skip_cards:
                return skip_cards[0]
        return None

    def calculate_exploding_kitten_probability(self, state: GameState) -> float:
        # Calculate the probability of drawing an Exploding Kitten
        total_kitten_cards = state.total_cards_in_deck.EXPLODING_KITTEN
        remaining_cards = state.cards_left
        return total_kitten_cards / remaining_cards if remaining_cards > 0 else 0