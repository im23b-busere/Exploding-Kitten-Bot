import random
from typing import List, Optional

from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class Enzo(Bot):
    def play(self, state: GameState) -> Optional[Card]:
        # Calculate the probability of drawing an Exploding Kitten
        exploding_kitten_probability = self.calculate_exploding_kitten_probability(state)
        game_phase = self.get_game_phase(state)

        # Use SEE THE FUTURE proactively, especially in the early and mid game
        if exploding_kitten_probability > 0.2:
            see_the_future_cards = self.get_cards_by_type(CardType.SEE_THE_FUTURE)
            if see_the_future_cards:
                return see_the_future_cards[0]

        # Use SKIP more aggressively in late game or when the risk is higher
        if exploding_kitten_probability > self.get_skip_threshold(game_phase):
            skip_cards = self.get_cards_by_type(CardType.SKIP)
            if skip_cards:
                return random.choice(skip_cards)

        # Play NORMAL cards when no immediate risk is detected
        normal_cards = self.get_cards_by_type(CardType.NORMAL)
        if normal_cards:
            return random.choice(normal_cards)

        # Default fallback: play any card except DEFUSE
        playable_cards = [card for card in self.hand if card.card_type != CardType.DEFUSE]
        if playable_cards:
            return random.choice(playable_cards)

        # No card to play
        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        # Use DEFUSE card if available
        defuse_cards = self.get_cards_by_type(CardType.DEFUSE)
        if defuse_cards:
            self.hand.remove(defuse_cards[0])

            # Strategically place the Exploding Kitten based on game phase
            if state.cards_left > 10:
                # Place deeper in early game
                return random.randint(state.cards_left // 2, state.cards_left - 1)
            else:
                # In late game, place near the top to trap opponents if there are few cards left
                return random.randint(1, 2)  # Less than 3 cards left: high risk, high reward

        # No DEFUSE means the bot loses
        return -1

    def see_the_future(self, state: GameState, top_three: List[Card]):
        # Analyze the top three cards and adjust strategy
        if any(card.card_type == CardType.EXPLODING_KITTEN for card in top_three):
            print("Exploding Kitten detected in the top three cards!")
            skip_cards = self.get_cards_by_type(CardType.SKIP)
            if skip_cards:
                return skip_cards[0]

        # If no immediate risk, conserve important cards
        print("No immediate threats detected in the top three cards.")
        return None

    def calculate_exploding_kitten_probability(self, state: GameState) -> float:
        """Probability calculation: Exploding Kittens left vs total cards."""
        total_kitten_cards = state.total_cards_in_deck.EXPLODING_KITTEN
        remaining_cards = state.cards_left
        return total_kitten_cards / remaining_cards if remaining_cards > 0 else 0

    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        """Helper method to filter cards by type."""
        return [card for card in self.hand if card.card_type == card_type]

    def get_game_phase(self, state: GameState) -> str:
        """Determine the current phase of the game."""
        if state.cards_left > 20:
            return "early"
        elif state.cards_left > 10:
            return "mid"
        else:
            return "late"

    def get_skip_threshold(self, game_phase: str) -> float:
        """Set the probability threshold for using a SKIP card more conservatively."""
        if game_phase == "early":
            return 0.4  # Higher tolerance for risk in early game
        elif game_phase == "mid":
            return 0.3  # Slightly higher risk in mid game
        else:  # Late game, use SKIP only when risk is high
            return 0.15  # Play very conservatively, fewer cards left