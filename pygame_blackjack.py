import pygame, copy, random, sys

pygame.init()
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards
decks = 4
game_deck = copy.deepcopy(decks * one_deck)
WIDTH = 1280
HEIGHT = 720
BG = pygame.image.load("assets/Background.png")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Blackjack with Menu")
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 44)
smaller_font = pygame.font.Font('freesansbold.ttf', 36)
active = False
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
hand_active = False
add_score = False
results = ['', 'PLAYER BUSTED o_O', 'Player WINS! :)', 'DEALER WINS :(', 'PUSH...']

def get_font(size):
	return pygame.font.Font("assets/font.ttf", size)

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

def main_menu():
	while True:
		screen.blit(BG, (0, 0))

		MENU_MOUSE_POS = pygame.mouse.get_pos()

		MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
		MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

		PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
							text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
		OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
							text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
		QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
							text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

		screen.blit(MENU_TEXT, MENU_RECT)

		for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
			button.changeColor(MENU_MOUSE_POS)
			button.update(screen)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
					blackjack_game()
				if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
					options()
				if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
					pygame.quit()
					sys.exit()

		pygame.display.update()

def options():
	while True:
		OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

		screen.fill("white")

		OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
		OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
		screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

		OPTIONS_BACK = Button(image=None, pos=(640, 460),
							text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

		OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
		OPTIONS_BACK.update(screen)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
					main_menu()

		pygame.display.update()

def deal_cards(current_hand, current_deck):
	card = random.randint(0, len(current_deck) - 1)
	current_hand.append(current_deck[card])
	current_deck.pop(card)
	return current_hand, current_deck

def draw_scores(player, dealer):
	screen.blit(font.render(f'Score[{player}]', True, 'white'), (350, 400))
	if reveal_dealer:
		screen.blit(font.render(f'Score[{dealer}]', True, 'white'), (350, 100))


def draw_cards(player, dealer, reveal):
	for i in range(len(player)):
		pygame.draw.rect(screen, 'white', [70 + (70 * i), 330 + (5 * i), 120, 220], 0, 5)
		screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 335 + 5 * i))
		screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 505 + 5 * i))
		pygame.draw.rect(screen, 'red', [70 + (70 * i), 330 + (5 * i), 120, 220], 5, 5)

	for i in range(len(dealer)):
		pygame.draw.rect(screen, 'white', [70 + (70 * i), 60 + (5 * i), 120, 220], 0, 5)
		if i != 0 or reveal:
			screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 65 + 5 * i))
			screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 235 + 5 * i))
		else:
			screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 65 + 5 * i))
			screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 235 + 5 * i))
		pygame.draw.rect(screen, 'blue', [70 + (70 * i), 60 + (5 * i), 120, 220], 5, 5)

def calculate_score(hand):
	hand_score = 0
	aces_count = hand.count('A')
	for card in hand:
		if card in ['J', 'Q', 'K']:
			hand_score += 10
		elif card == 'A':
			hand_score += 11
		else:
			hand_score += int(card)
	while hand_score > 21 and aces_count > 0:
		hand_score -= 10
		aces_count -= 1
	return hand_score

def draw_game(act, record, result):
	button_list = []
	if not act:
		deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [150, 20, 300, 100], 3, 5)
		deal_text = font.render('DEAL HAND', True, 'black')
		screen.blit(deal_text, (165, 50))
		button_list.append(deal)
	else:
		hit = pygame.draw.rect(screen, 'white', [0, 600, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [0, 600, 300, 100], 3, 5)
		hit_text = font.render('HIT ME', True, 'black')
		screen.blit(hit_text, (55, 635))
		button_list.append(hit)
		stand = pygame.draw.rect(screen, 'white', [300, 600, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [300, 600, 300, 100], 3, 5)
		stand_text = font.render('STAND', True, 'black')
		screen.blit(stand_text, (355, 635))
		button_list.append(stand)
		score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
		screen.blit(score_text, (15, 840))
	if result != 0:
		screen.blit(font.render(results[result], True, 'white'), (15, 10))
		deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
		pygame.draw.rect(screen, 'black', [153, 223, 294, 94], 3, 5)
		deal_text = font.render('NEW HAND', True, 'black')
		screen.blit(deal_text, (165, 250))
		button_list.append(deal)
	return button_list

def check_endgame(hand_act, deal_score, play_score, result, totals, add):
	if not hand_act and deal_score >= 17:
		if play_score > 21:
			result = 1
		elif deal_score < play_score <= 21 or deal_score > 21:
			result = 2
		elif play_score < deal_score <= 21:
			result = 3
		else:
			result = 4
		if add:
			if result == 1 or result == 3:
				totals[1] += 1
			elif result == 2:
				totals[0] += 1
			else:
				totals[2] += 1
			add = False
	return result, totals, add


def blackjack_game():
	global player_score, dealer_score, my_hand, dealer_hand, initial_deal, reveal_dealer, active, hand_active, add_score, outcome, records, game_deck

	screen = pygame.display.set_mode([WIDTH, HEIGHT])
	pygame.display.set_caption('Pygame Blackjack!')

	timer = pygame.time.Clock()

	run = True
	while run:
		timer.tick(60)
		screen.fill('black')

		if initial_deal:
			for i in range(2):
				my_hand, game_deck = deal_cards(my_hand, game_deck)
				dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
			initial_deal = False

		if active:
			player_score = calculate_score(my_hand)
			draw_cards(my_hand, dealer_hand, reveal_dealer)
			if reveal_dealer:
				dealer_score = calculate_score(dealer_hand)
				if dealer_score < 17:
					dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
			draw_scores(player_score, dealer_score)

		buttons = draw_game(active, records, outcome)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONUP:
				if not active:
					if buttons[0].collidepoint(event.pos):
						active = True
						initial_deal = True
						my_hand = []
						dealer_hand = []
						outcome = 0
						hand_active = True
						reveal_dealer = False
						add_score = True
				else:
					if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
						my_hand, game_deck = deal_cards(my_hand, game_deck)
					elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
						reveal_dealer = True
						hand_active = False
					elif len(buttons) == 3:
						if buttons[2].collidepoint(event.pos):
							active = True
							initial_deal = True
							my_hand = []
							dealer_hand = []
							outcome = 0
							hand_active = True
							reveal_dealer = False
							add_score = True
							dealer_score = 0
							player_score = 0

		if hand_active and player_score >= 21:
			hand_active = False
			reveal_dealer = True

		outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)

		pygame.display.flip()
	pygame.quit()

main_menu()