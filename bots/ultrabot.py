import random
from typing import List, Optional
from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class CombinedBot(Bot):
    def __init__(self, name: str):
        super().__init__(name)
        self.last_see_the_future_turn = -3
        self.top_three = []
        self.current_turn = 0
        self.cards_played_this_turn = 0

    def play(self, state: GameState) -> Optional[Card]:
        """
        Decide which card to play based on a combination of strategies.
        """
        # Update turn tracking
        self.current_turn += 1 if self.cards_played_this_turn == 0 else 0
        self.cards_played_this_turn = 0

        # Step 1: Use SEE_THE_FUTURE strategically
        see_the_future_cards = self.get_cards_by_type(CardType.SEE_THE_FUTURE)
        if see_the_future_cards and self.current_turn - self.last_see_the_future_turn > 2:
            self.last_see_the_future_turn = self.current_turn
            self.cards_played_this_turn += 1
            return see_the_future_cards[0]

        # Step 2: Use SKIP if danger is imminent
        if self._is_dangerous(state):
            skip_cards = self.get_cards_by_type(CardType.SKIP)
            if skip_cards:
                self.cards_played_this_turn += 1
                return random.choice(skip_cards)

        # Step 3: Play NORMAL cards to delay drawing
        normal_cards = self.get_cards_by_type(CardType.NORMAL)
        if normal_cards:
            self.cards_played_this_turn += 1
            return random.choice(normal_cards)

        # Step 4: Use results from SEE_THE_FUTURE
        if self.top_three:
            next_card = self.top_three.pop(0)
            if next_card.card_type == CardType.EXPLODING_KITTEN:
                skip_cards = self.get_cards_by_type(CardType.SKIP)
                if skip_cards:
                    self.cards_played_this_turn += 1
                    return skip_cards[0]

        # No cards to play, must draw
        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        """
        Place the Exploding Kitten strategically in the deck.
        """
        if self.top_three:
            safe_positions = [i for i, card in enumerate(self.top_three) if card.card_type != CardType.EXPLODING_KITTEN]
            if safe_positions:
                return safe_positions[0]
        return random.randint(0, state.cards_left)

    def see_the_future(self, state: GameState, top_three: List[Card]):
        """
        Analyze SEE_THE_FUTURE results and adjust strategy.
        """
        self.top_three = top_three
        if any(card.card_type == CardType.EXPLODING_KITTEN for card in top_three):
            print("Danger detected in top three cards!")

    def _is_dangerous(self, state: GameState) -> bool:
        """
        Assess if the current situation is dangerous.
        """
        probability = self.calculate_exploding_kitten_probability(state)
        if probability > 0.2 or state.was_last_card_exploding_kitten:
            return True
        return state.cards_left <= max(3, state.alive_bots)

    def calculate_exploding_kitten_probability(self, state: GameState) -> float:
        """Probability calculation: Exploding Kittens left vs total cards."""
        total_kitten_cards = state.total_cards_in_deck.EXPLODING_KITTEN
        remaining_cards = state.cards_left
        return total_kitten_cards / remaining_cards if remaining_cards > 0 else 0

    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        """
        Helper method to filter cards by type.
        """
        return [card for card in self.hand if card.card_type == card_type]
