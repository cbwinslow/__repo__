import random
from typing import List, Tuple
from advanced_blackjack_ai import BlackjackAI, Hand, Card, Deck

class PlayerSimulator:
    def __init__(self, skill_level: float, bankroll: float, bet_size: float):
        self.ai = BlackjackAI()
        self.skill_level = skill_level  # 0.0 to 1.0, where 1.0 is perfect basic strategy
        self.bankroll = bankroll
        self.bet_size = bet_size

    def make_decision(self, hand: Hand, dealer_up_card: Card) -> str:
        optimal_decision = self.ai.recommend_action(hand, dealer_up_card)
        if random.random() < self.skill_level:
            return optimal_decision
        else:
            return random.choice(["Hit", "Stand"])

def simulate_game(players: List[PlayerSimulator], num_rounds: int) -> List[Tuple[float, float]]:
    deck = Deck(6)  # Use 6 decks
    results = []

    for _ in range(num_rounds):
        if len(deck.cards) < 52:  # Reshuffle when less than 1 deck remains
            deck = Deck(6)

        dealer_hand = Hand([deck.draw()])
        for player in players:
            player_hand = Hand([deck.draw(), deck.draw()])
            
            # Player's turn
            while player.make_decision(player_hand, dealer_hand.cards[0]) == "Hit":
                player_hand.add_card(deck.draw())
                if player_hand.value() > 21:
                    break

            # Dealer's turn
            while dealer_hand.value() < 17:
                dealer_hand.add_card(deck.draw())

            # Determine outcome
            if player_hand.value() > 21:
                player.bankroll -= player.bet_size
            elif dealer_hand.value() > 21 or player_hand.value() > dealer_hand.value():
                player.bankroll += player.bet_size
            elif player_hand.value() < dealer_hand.value():
                player.bankroll -= player.bet_size
            # If equal, it's a push (no change in bankroll)

        results.append(tuple(player.bankroll for player in players))

    return results

# Run simulation
players = [
    PlayerSimulator(0.2, 1000, 10),  # Novice player
    PlayerSimulator(0.5, 1000, 10),  # Intermediate player
    PlayerSimulator(0.8, 1000, 10),  # Advanced player
    PlayerSimulator(1.0, 1000, 10)   # Perfect basic strategy player
]

simulation_results = simulate_game(players, 1000)

# Analyze results
for i, player in enumerate(players):
    final_bankroll = simulation_results[-1][i]
    profit_loss = final_bankroll - 1000
    print(f"Player {i+1} (Skill {player.skill_level:.1f}): Final bankroll ${final_bankroll:.2f}, Profit/Loss ${profit_loss:.2f}")
