"""
Advanced Blackjack AI and Probability Calculator

This module provides a comprehensive tool for analyzing Blackjack games,
calculating probabilities, and recommending optimal plays. It includes
features such as card counting, multiple deck handling, and advanced
strategy recommendations.

Author: Claude
Date: October 20, 2024
Version: 2.0
"""

import random
from typing import List, Tuple, Dict
from collections import defaultdict

class Card:
    """Represents a playing card."""
    
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    SUITS = ['♠', '♥', '♦', '♣']

    def __init__(self, rank: str, suit: str):
        if rank not in self.RANKS or suit not in self.SUITS:
            raise ValueError(f"Invalid card: {rank}{suit}")
        self.rank = rank
        self.suit = suit

    def value(self) -> int:
        """Return the numerical value of the card."""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

class Deck:
    """Represents a deck of playing cards."""

    def __init__(self, num_decks: int = 1):
        self.cards = [Card(rank, suit) for _ in range(num_decks) for rank in Card.RANKS for suit in Card.SUITS]
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Card:
        """Draw a card from the deck."""
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()

class Hand:
    """Represents a hand of cards in Blackjack."""

    def __init__(self, cards: List[Card] = None):
        self.cards = cards or []

    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        self.cards.append(card)

    def value(self) -> int:
        """Calculate the value of the hand, handling Aces optimally."""
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    def is_blackjack(self) -> bool:
        """Check if the hand is a Blackjack."""
        return len(self.cards) == 2 and self.value() == 21

    def __str__(self) -> str:
        return ", ".join(str(card) for card in self.cards)

class BlackjackAI:
    """Advanced Blackjack AI and Probability Calculator."""

    def __init__(self, num_decks: int = 6):
        self.deck = Deck(num_decks)
        self.card_count = 0
        self.true_count = 0
        self.hands_played = 0

    def reset_count(self) -> None:
        """Reset the card count and true count."""
        self.card_count = 0
        self.true_count = 0
        self.hands_played = 0

    def update_count(self, card: Card) -> None:
        """Update the running count based on the card drawn."""
        if card.value() in [10, 11]:
            self.card_count -= 1
        elif 2 <= card.value() <= 6:
            self.card_count += 1
        self.true_count = self.card_count / (len(self.deck.cards) // 52)

    def calculate_bust_probability(self, player_hand: Hand) -> float:
        """Calculate the probability of busting if hitting."""
        remaining_cards = defaultdict(int)
        for card in self.deck.cards:
            remaining_cards[card.value()] += 1

        total_cards = sum(remaining_cards.values())
        bust_cards = sum(remaining_cards[i] for i in range(22 - player_hand.value(), 11))
        return bust_cards / total_cards if total_cards > 0 else 0

    def simulate_dealer_hand(self, up_card: Card, num_simulations: int = 10000) -> float:
        """Simulate dealer hands to estimate probability of dealer busting."""
        dealer_busts = 0
        for _ in range(num_simulations):
            dealer_hand = Hand([up_card])
            while dealer_hand.value() < 17:
                dealer_hand.add_card(self.deck.draw())
                self.deck.cards.append(dealer_hand.cards[-1])  # Put the card back for next simulation
            if dealer_hand.value() > 21:
                dealer_busts += 1
        return dealer_busts / num_simulations

    def basic_strategy(self, player_hand: Hand, dealer_up_card: Card) -> str:
        """Recommend action based on basic strategy."""
        player_value = player_hand.value()
        dealer_value = dealer_up_card.value()

        if player_value >= 17:
            return "Stand"
        elif player_value <= 11:
            return "Hit"
        elif player_value == 12:
            return "Stand" if 4 <= dealer_value <= 6 else "Hit"
        elif 13 <= player_value <= 16:
            return "Stand" if 2 <= dealer_value <= 6 else "Hit"
        else:
            return "Stand"

    def recommend_action(self, player_hand: Hand, dealer_up_card: Card) -> str:
        """Recommend an action based on probabilities and basic strategy."""
        basic_recommendation = self.basic_strategy(player_hand, dealer_up_card)
        bust_prob = self.calculate_bust_probability(player_hand)
        dealer_bust_prob = self.simulate_dealer_hand(dealer_up_card)

        if self.true_count > 2 and player_hand.value() == 16 and dealer_up_card.value() == 10:
            return "Stand"  # Deviate from basic strategy when count is high
        elif bust_prob > 0.6:
            return "Stand"
        elif dealer_bust_prob > 0.5 and player_hand.value() >= 12:
            return "Stand"
        else:
            return basic_recommendation

    def play_hand(self, player_hand: Hand, dealer_up_card: Card) -> Tuple[str, Dict[str, float]]:
        """Play a hand and return the recommended action and probabilities."""
        action = self.recommend_action(player_hand, dealer_up_card)
        probabilities = {
            "Bust Probability": self.calculate_bust_probability(player_hand),
            "Dealer Bust Probability": self.simulate_dealer_hand(dealer_up_card)
        }
        self.hands_played += 1
        return action, probabilities

    def get_card_counting_info(self) -> Dict[str, float]:
        """Get current card counting information."""
        return {
            "Running Count": self.card_count,
            "True Count": self.true_count,
            "Hands Played": self.hands_played
        }

# Example usage
if __name__ == "__main__":
    try:
        ai = BlackjackAI(num_decks=6)
        player_hand = Hand([Card('10', '♠'), Card('5', '♥')])
        dealer_up_card = Card('A', '♦')

        for card in player_hand.cards + [dealer_up_card]:
            ai.update_count(card)

        action, probabilities = ai.play_hand(player_hand, dealer_up_card)

        print(f"Player Hand: {player_hand}")
        print(f"Dealer Up Card: {dealer_up_card}")
        print(f"Recommended Action: {action}")
        print("Probabilities:")
        for key, value in probabilities.items():
            print(f"  {key}: {value:.2f}")
        print("Card Counting Info:")
        for key, value in ai.get_card_counting_info().items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
