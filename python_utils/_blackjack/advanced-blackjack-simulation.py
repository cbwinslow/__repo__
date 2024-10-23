"""
Advanced Blackjack Simulation System

This module provides a comprehensive simulation of blackjack games,
including advanced playing options, multiple card counting systems,
a graphical user interface, and a simple machine learning component.

Author: Claude
Date: October 20, 2024
Version: 3.0
"""

import random
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Dict
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from sklearn.neural_network import MLPClassifier

class Card:
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    SUITS = ['♠', '♥', '♦', '♣']

    def __init__(self, rank: str, suit: str):
        if rank not in self.RANKS or suit not in self.SUITS:
            raise ValueError(f"Invalid card: {rank}{suit}")
        self.rank = rank
        self.suit = suit

    def value(self) -> int:
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self, num_decks: int = 6):
        self.cards = [Card(rank, suit) for _ in range(num_decks) for rank in Card.RANKS for suit in Card.SUITS]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()

class Hand:
    def __init__(self, cards: List[Card] = None):
        self.cards = cards or []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def value(self) -> int:
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value() == 21

    def can_split(self) -> bool:
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def __str__(self) -> str:
        return ", ".join(str(card) for card in self.cards)

class CardCounter:
    def __init__(self, system: str = "Hi-Lo"):
        self.system = system
        self.count = 0
        self.true_count = 0
        self.decks_remaining = 6

    def update(self, card: Card) -> None:
        if self.system == "Hi-Lo":
            if card.value() in [10, 11]:
                self.count -= 1
            elif 2 <= card.value() <= 6:
                self.count += 1
        elif self.system == "KO":
            if card.value() in [10, 11]:
                self.count -= 1
            elif 2 <= card.value() <= 7:
                self.count += 1
        elif self.system == "Omega II":
            if card.value() in [10, 11]:
                self.count -= 2
            elif card.value() in [2, 3, 7]:
                self.count += 1
            elif card.value() in [4, 5, 6]:
                self.count += 2
            elif card.value() == 9:
                self.count -= 1
        
        self.decks_remaining = max(1, self.decks_remaining - 1/52)
        self.true_count = self.count / self.decks_remaining

class BlackjackAI:
    def __init__(self, num_decks: int = 6, card_counting_system: str = "Hi-Lo"):
        self.deck = Deck(num_decks)
        self.card_counter = CardCounter(card_counting_system)

    def calculate_bust_probability(self, player_hand: Hand) -> float:
        remaining_cards = defaultdict(int)
        for card in self.deck.cards:
            remaining_cards[card.value()] += 1

        total_cards = sum(remaining_cards.values())
        bust_cards = sum(remaining_cards[i] for i in range(22 - player_hand.value(), 11))
        return bust_cards / total_cards if total_cards > 0 else 0

    def simulate_dealer_hand(self, up_card: Card, num_simulations: int = 10000) -> float:
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
        player_value = player_hand.value()
        dealer_value = dealer_up_card.value()

        if player_hand.can_split():
            if player_value in [16, 18]:  # Always split 8s and Aces
                return "Split"
            elif player_value == 20:  # Never split 10s
                return "Stand"
            elif player_value in [4, 6]:
                return "Split" if dealer_value in [2, 3, 4, 5, 6] else "Hit"
            elif player_value == 12:
                return "Split" if dealer_value in [2, 3, 4, 5, 6] else "Hit"
            elif player_value == 14:
                return "Split" if dealer_value in [2, 3, 4, 5, 6, 7] else "Hit"
        
        if len(player_hand.cards) == 2:  # Consider doubling down
            if player_value == 11:
                return "Double" if dealer_value != 11 else "Hit"
            elif player_value == 10:
                return "Double" if dealer_value < 10 else "Hit"
            elif player_value == 9:
                return "Double" if 3 <= dealer_value <= 6 else "Hit"

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
        basic_recommendation = self.basic_strategy(player_hand, dealer_up_card)
        
        # Adjust based on card counting
        if self.card_counter.true_count > 2:
            if player_hand.value() == 16 and dealer_up_card.value() == 10:
                return "Stand"  # Deviate from basic strategy when count is high
            elif basic_recommendation == "Hit" and player_hand.value() == 12:
                return "Stand"  # Stand on 12 vs dealer 2 or 3 when count is high
        
        return basic_recommendation

class PlayerSimulator:
    def __init__(self, skill_level: float, bankroll: float, bet_size: float, ai: BlackjackAI, ml_model: MLPClassifier = None):
        self.ai = ai
        self.skill_level = skill_level
        self.bankroll = bankroll
        self.bet_size = bet_size
        self.ml_model = ml_model

    def make_decision(self, hand: Hand, dealer_up_card: Card) -> str:
        optimal_decision = self.ai.recommend_action(hand, dealer_up_card)
        
        if self.ml_model:
            features = [hand.value(), dealer_up_card.value(), self.ai.card_counter.true_count]
            ml_decision = self.ml_model.predict([features])[0]
            
            # Blend AI and ML decisions based on skill level
            if random.random() < self.skill_level:
                return ml_decision if random.random() < 0.5 else optimal_decision
        
        if random.random() < self.skill_level:
            return optimal_decision
        else:
            return random.choice(["Hit", "Stand", "Double", "Split"])

def simulate_game(players: List[PlayerSimulator], num_rounds: int, european_rules: bool = False) -> List[Tuple[float, float]]:
    results = []

    for _ in range(num_rounds):
        if len(players[0].ai.deck.cards) < 52:  # Reshuffle when less than 1 deck remains
            players[0].ai.deck = Deck(6)
            players[0].ai.card_counter.decks_remaining = 6

        dealer_hand = Hand([players[0].ai.deck.draw()])
        if not european_rules:
            dealer_hand.add_card(players[0].ai.deck.draw())  # Draw hole card for American rules

        for player in players:
            player_hands = [Hand([player.ai.deck.draw(), player.ai.deck.draw()])]
            
            for hand in player_hands:
                while True:
                    decision = player.make_decision(hand, dealer_hand.cards[0])
                    if decision == "Hit":
                        hand.add_card(player.ai.deck.draw())
                        if hand.value() > 21:
                            break
                    elif decision == "Stand":
                        break
                    elif decision == "Double":
                        if len(hand.cards) == 2:
                            player.bet_size *= 2
                            hand.add_card(player.ai.deck.draw())
                            break
                    elif decision == "Split":
                        if hand.can_split() and len(player_hands) < 4:  # Limit to 4 splits
                            new_hand = Hand([hand.cards.pop()])
                            hand.add_card(player.ai.deck.draw())
                            new_hand.add_card(player.ai.deck.draw())
                            player_hands.append(new_hand)
                        else:
                            continue  # If split not possible, continue with next decision

            # Dealer's turn
            if european_rules:
                dealer_hand.add_card(player.ai.deck.draw())  # Draw second card now for European rules

            while dealer_hand.value() < 17:
                dealer_hand.add_card(player.ai.deck.draw())

            # Determine outcome for each hand
            for hand in player_hands:
                if hand.value() > 21:
                    player.bankroll -= player.bet_size
                elif dealer_hand.value() > 21 or hand.value() > dealer_hand.value():
                    player.bankroll += player.bet_size
                elif hand.value() < dealer_hand.value():
                    player.bankroll -= player.bet_size
                # If equal, it's a push (no change in bankroll)

            # Reset bet size (in case of doubling)
            player.bet_size = 10

            # Update card counter
            for card in dealer_hand.cards + [card for hand in player_hands for card in hand.cards]:
                player.ai.card_counter.update(card)

        results.append(tuple(player.bankroll for player in players))

    return results

class BlackjackGUI:
    def __init__(self, master):
        self.master = master
        master.title("Blackjack Simulation")

        self.players = []
        self.results = []

        # Create input fields
        ttk.Label(master, text="Number of rounds:").grid(row=0, column=0)
        self.num_rounds = ttk.Entry(master)
        self.num_rounds.grid(row=0, column=1)
        self.num_rounds.insert(0, "1000")

        ttk.Label(master, text="Card counting system:").grid(row=1, column=0)
        self.counting_system = ttk.Combobox(master, values=["Hi-Lo", "KO", "Omega II"])
        self.counting_system.grid(row=1, column=1)
        self.counting_system.set("Hi-Lo")

        ttk.Label(master, text="European rules:").grid(row=2, column=0)
        self.european_var = tk.BooleanVar()
        ttk.Checkbutton(master, variable=self.european_var).grid(row=2, column=1)

        # Player setup
        self.player_frames = []
        for i in range(4):
            frame = ttk.Frame(master)
            frame.grid(row=3+i, column=0, columnspan=2)
            ttk.Label(frame, text=f"Player {i+1} Skill Level (0-1):").pack(side=tk.LEFT)
            skill = ttk.Entry(frame, width=5)
            skill.pack(side=tk.LEFT)
            skill.insert(0, str(0.2 + 0.2*i))
            self.player_frames.append((frame, skill))

        # Run button
        self.run_button = ttk.Button(master, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=7, column=0, columnspan=2)

        # Results graph
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=8)

    def run_simulation(self):
        num_rounds = int(self.num_rounds.get())
        counting_system = self.counting_system.get()
        european_rules = self.european_var.get()

        self.players = [
            PlayerSimulator(
                float(skill.get()),
                1000,
                10,
                BlackjackAI(card_counting_system=counting_system)
            ) for _, skill in self.player_frames
        ]

        self.results = simulate_game(self.players, num_rounds, european_rules)
        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        for i, player in enumerate(self.players):
            self.ax.plot([r[i] for r in self.results], label=f"Player {i+1} (Skill: {player.skill_level:.1f})")