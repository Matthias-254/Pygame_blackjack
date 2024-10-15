import pygame
import random
import copy

cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
cards_deck = 4 * cards
for x in range(10):
    print(random.choice(cards), end=" ")
    print("test")