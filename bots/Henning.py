import random
from typing import List, Optional
from bot import Bot
from card import Card, CardType
from game_handling.game_state import GameState


class Henning(Bot):
    def play(self, state: GameState) -> Optional[Card]:
        """
        Decide which card to play based on game state and card priorities.
        """
        # Step 1: Use SEE THE FUTURE to assess danger and plan ahead
        see_the_future_cards = [card for card in self.hand if card.card_type == CardType.SEE_THE_FUTURE]
        if see_the_future_cards:
            return see_the_future_cards[0]

        # Step 2: Avoid Exploding Kittens using SKIP
        if self._is_dangerous(state):
            skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
            if skip_cards:
                return random.choice(skip_cards)

        # Step 3: Use NORMAL cards to delay drawing if nothing critical is needed
        normal_cards = [card for card in self.hand if card.card_type == CardType.NORMAL]
        if normal_cards:
            return random.choice(normal_cards)

        # Step 4: If no cards to play, draw and hope for the best
        return None

    def handle_exploding_kitten(self, state: GameState) -> int:
        """
        Decide where to place the Exploding Kitten in the deck.
        """
        # Place it strategically to target opponents, not yourself
        if state.cards_left > state.alive_bots:
            # Spread the danger among all players
            position = state.cards_left // state.alive_bots
        else:
            # Randomize placement in smaller decks
            position = random.randint(0, state.cards_left - 1)

        print(f"Placing Exploding Kitten back into position {position} of the deck.")
        return position

    def see_the_future(self, state: GameState, top_three: List[Card]):
        """
        Analyze the top three cards revealed by SEE THE FUTURE and adjust strategy.
        """
        if not top_three:
            return None

        # Check for immediate danger in the top three cards
        danger_positions = [i for i, card in enumerate(top_three) if card.card_type == CardType.EXPLODING_KITTEN]

        if danger_positions:
            print(f"Exploding Kitten spotted at positions {danger_positions}!")

            # If immediate danger, play SKIP to avoid
            skip_cards = [card for card in self.hand if card.card_type == CardType.SKIP]
            if danger_positions[0] == 0 and skip_cards:
                print("Using SKIP to avoid imminent Exploding Kitten.")
                return skip_cards[0]

            # Prepare for future danger by conserving DEFUSE cards
            if danger_positions[0] <= 2:
                print("Danger is near, preparing to avoid it in the next turns.")

        # If safe, prioritize safe actions
        return None

    def _is_dangerous(self, state: GameState) -> bool:
        """
        Assess if the current situation is dangerous based on game state.
        """
        # Danger if an Exploding Kitten was just defused and returned
        if state.was_last_card_exploding_kitten:
            return True

        # Danger if deck is small, and drawing is likely to hit a bad card
        if state.cards_left <= max(3, state.alive_bots):
            return True

        return False

    def _should_play_skip(self, state: GameState, danger_positions: List[int]) -> bool:
        """
        Determine if SKIP should be played based on danger analysis.
        """
        # Play SKIP if Exploding Kitten is imminent
        if danger_positions and danger_positions[0] == 0:
            return True

        # Play SKIP if the deck size makes danger unavoidable
        if state.cards_left <= state.alive_bots:
            return True

        return False

    def track_history(self, state: GameState):
        """
        Use the game's history to gain insights and adjust gameplay.
        """
        # Track how many Exploding Kittens have been played
        exploding_kittens_played = [
            card for card in state.history_of_played_cards if card.card_type == CardType.EXPLODING_KITTEN
        ]
        print(f"Exploding Kittens removed from the game: {len(exploding_kittens_played)}")

        # Track SKIP cards played by opponents
        skips_played = [
            card for card in state.history_of_played_cards if card.card_type == CardType.SKIP
        ]
        print(f"SKIP cards played so far: {len(skips_played)}")

        # Adjust strategy if most DEFUSE cards are gone
        defuses_played = [
            card for card in state.history_of_played_cards if card.card_type == CardType.DEFUSE
        ]
        if len(defuses_played) >= state.alive_bots:
            print("Most players are out of DEFUSE cards. Play cautiously!")
