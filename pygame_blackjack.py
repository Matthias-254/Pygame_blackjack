import pygame, copy, random, sys, sqlite3	# Import van noodzakelijke bibliotheken

# Initialisatie van de pygame en basisinstellingen
pygame.init()
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']  # Waarden van kaarten
one_deck = 4 * cards  # Een deck bestaat uit 4 van elke kaart
decks = 4  # Aantal decks in het spel
game_deck = copy.deepcopy(decks * one_deck)  # Diepe kopie om te werken met het speldeck
WIDTH = 1280  # Breedte van het scherm
HEIGHT = 720  # Hoogte van het scherm
BG = pygame.image.load("assets/Background.jpg")  # Achtergrondafbeelding
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Instellen van het scherm met de gegeven afmetingen
pygame.display.set_caption("Pygame Blackjack")  # Titel van het venster
timer = pygame.time.Clock()  # Voor framebeheer
font = pygame.font.Font('freesansbold.ttf', 44)  # Grotere lettertype-instelling
smaller_font = pygame.font.Font('freesansbold.ttf', 36)  # Kleinere lettertype-instelling
active = False  # Indicator of het spel actief is
connection = sqlite3.connect("blackjack.db")  # Verbindt met de database
cursor = connection.cursor()  # Cursor voor databaseacties
records = [0, 0, 0]  # Record van winst/verlies/gelijkspel
player_score = 0  # Score van de speler
dealer_score = 0  # Score van de dealer
initial_deal = False  # Status voor eerste deling van kaarten
my_hand = []  # Hand van de speler
dealer_hand = []  # Hand van de dealer
outcome = 0  # Huidige uitkomststatus
reveal_dealer = False  # Bepaalt of de dealerhand wordt onthuld
hand_active = False  # Of de huidige hand actief is
add_score = False  # Of de score moet worden bijgewerkt
results = ['', 'PLAYER BUSTED o_O', 'Player WINS! :)', 'DEALER WINS :(', 'PUSH...']  # Mogelijke uitkomsten
logged_in = False  # Inlogstatus van de gebruiker
logged_in_user = None  # Naam van ingelogde gebruiker

def get_font(size):
	"""Return een font-object met de gegeven grootte."""
	return pygame.font.Font("assets/font.ttf", size)

# Database tabel maken als deze nog niet bestaat
cursor.execute("""
	CREATE TABLE IF NOT EXISTS players (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL,
		wins INTEGER DEFAULT 0,
		losses INTEGER DEFAULT 0,
		draws INTEGER DEFAULT 0
		)
	""")
connection.commit()	# Wijzigingen toepassen op de database

class Button:
	"""Knopklasse voor het weergeven van knoppen in het spel."""
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
		"""Render de knop op het scherm."""
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def check_for_input(self, position):
		"""Controleer of de knop is aangeklikt."""
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def change_color(self, position):
		"""Verander de knopkleur wanneer de muis eroverheen beweegt."""
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

class TextInput:
	"""Inputveld voor tekstinvoer van gebruikers."""
	def __init__(self, pos, width, font, placeholder=""):
		self.rect = pygame.Rect(pos[0], pos[1], width, font.get_height() + 10)
		self.font = font
		self.placeholder = placeholder
		self.text = ""
		self.active = False
		self.color_inactive = pygame.Color('gray')
		self.color_active = pygame.Color('black')
		self.color = self.color_inactive

	def handle_event(self, event):
		"""Handel gebeurtenissen af voor tekstinvoer."""
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				self.active = not self.active
			else:
				self.active = False
			self.color = self.color_active if self.active else self.color_inactive

		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					return self.text
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
		return None

	def draw(self, screen):
		"""Toon het tekstinvoerveld op het scherm."""
		txt_surface = self.font.render(self.text if self.text else self.placeholder, True, self.color)
		screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
		pygame.draw.rect(screen, self.color, self.rect, 2)

def login_menu():
	"""Weergave van het loginmenu met velden voor gebruikersnaam en wachtwoord."""
	# Maak invoervelden voor gebruikersnaam en wachtwoord
	username_input = TextInput((500, 300), 300, font, placeholder="Username")
	password_input = TextInput((500, 400), 300, font, placeholder="Password")

	# Maak knoppen voor login en registratie
	login_button = Button(image=None, pos=(640, 500), text_input="LOGIN", font=get_font(45), base_color="Green",
						  hovering_color="Lightgreen")
	register_button = Button(image=None, pos=(640, 600), text_input="REGISTER", font=get_font(35), base_color="Blue",
							 hovering_color="Lightblue")

	error_message = ""  # Foutmelding initialiseren, leeg bij start

	# Maak een 'terug' knop om terug te keren naar het hoofdmenu
	back_button = Button(
		image=None,
		pos=(1200, 660),
		text_input="BACK",
		font=get_font(35),
		base_color="Darkred",
		hovering_color="Red"
	)

	# Loop voor het weergave van het loginmenu
	while True:
		screen.blit(BG, (0, 0))  # Achtergrondafbeelding tonen
		login_mouse_pos = pygame.mouse.get_pos()  # Verkrijg de muispositie voor hover effect

		# Weergave van de tekst "LOGIN" bovenaan het scherm
		login_text = get_font(80).render("LOGIN", True, "#008fff")
		login_rect = login_text.get_rect(center=(640, 100))
		screen.blit(login_text, login_rect)

		# Teken de invoervelden op het scherm
		username_input.draw(screen)
		password_input.draw(screen)

		# Verander de knopkleur bij hover
		login_button.change_color(login_mouse_pos)
		login_button.update(screen)
		register_button.change_color(login_mouse_pos)
		register_button.update(screen)

		# Verander de kleur van de 'terug' knop bij hover
		back_button.change_color(pygame.mouse.get_pos())
		back_button.update(screen)

		# Als er een foutmelding is (bijv. ongeldige inloggegevens), toon deze op het scherm
		if error_message:
			pygame.draw.rect(screen, "lightgray", (400, 200, 690, 50))  # Achtergrond voor de foutmelding
			error_text = smaller_font.render(error_message, True, "red")  # Render de foutmelding in rood
			error_text_rect = error_text.get_rect(center=(740, 225))  # Plaats de foutmelding in het midden
			screen.blit(error_text, error_text_rect)

		# Event handling: kijkt naar gebruikersinput en voert actie uit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			# Kijkt of er op een knop geklikt is
			if event.type == pygame.MOUSEBUTTONDOWN:
				if back_button.check_for_input(pygame.mouse.get_pos()):  # Als de 'terug' knop wordt aangeklikt
					main_menu()  # Ga terug naar het hoofdmenu
					return

				if login_button.check_for_input(login_mouse_pos):  # Als de login knop wordt aangeklikt
					username = username_input.text  # Verkrijg de tekst uit de gebruikersnaam invoerveld
					password = password_input.text  # Verkrijg de tekst uit het wachtwoord invoerveld
					cursor.execute("SELECT * FROM players WHERE username = ? AND password = ?",
								   (username, password))  # Zoeken naar de gebruiker in de database
					user = cursor.fetchone()  # Verkrijg de eerste overeenkomstige rij uit de database
					if user:  # Als de gebruiker bestaat (inloggegevens zijn correct)
						global logged_in, logged_in_user
						logged_in = True  # Zet de status van de gebruiker als ingelogd
						logged_in_user = username  # Bewaar de ingelogde gebruikersnaam
						blackjack_game()  # Start het Blackjack-spel
					else:  # Als de inloggegevens incorrect zijn
						error_message = "Invalid credentials! Please try again."  # Toon foutmelding voor ongeldige inloggegevens

				if register_button.check_for_input(login_mouse_pos):  # Als de registratie knop wordt aangeklikt
					register_menu()  # Ga naar het registratie menu

			# Verwerk events voor de tekstvelden (bijv. typen in de velden)
			username_input.handle_event(event)
			password_input.handle_event(event)

		# Werk het scherm bij zodat de wijzigingen zichtbaar zijn
		pygame.display.update()

def register_menu():
	"""Weergave van het registratiemenu."""
	# Maak invoervelden voor gebruikersnaam en wachtwoord
	username_input = TextInput((470, 300), 350, font, placeholder="New Username")
	password_input = TextInput((470, 400), 350, font, placeholder="New Password")

	# Maak de knoppen voor registratie en teruggaan
	register_button = Button(image=None, pos=(640, 500), text_input="REGISTER", font=get_font(45), base_color="Green",
							 hovering_color="Lightgreen")
	back_button = Button(image=None, pos=(640, 600), text_input="BACK", font=get_font(35), base_color="Red",
						 hovering_color="Darkred")

	error_message = ""  # Foutmelding initialiseren, leeg bij start

	# Loop voor het weergave van het registratiemenu
	while True:
		screen.blit(BG, (0, 0))  # Achtergrondafbeelding tonen
		register_mouse_pos = pygame.mouse.get_pos()  # Verkrijg de muispositie voor hover effect

		# Weergave van de tekst "REGISTER" bovenaan het scherm
		register_text = get_font(80).render("REGISTER", True, "#008fff")
		register_rect = register_text.get_rect(center=(640, 100))
		screen.blit(register_text, register_rect)

		# Teken de invoervelden op het scherm
		username_input.draw(screen)
		password_input.draw(screen)

		# Verander de knopkleur bij hover
		register_button.change_color(register_mouse_pos)
		register_button.update(screen)
		back_button.change_color(register_mouse_pos)
		back_button.update(screen)

		# Als er een foutmelding is (bijv. bestaande gebruikersnaam), toon deze op het scherm
		if error_message:
			pygame.draw.rect(screen, "lightgray", (330, 200, 820, 50))  # Achtergrond voor de foutmelding
			error_text = smaller_font.render(error_message, True, "red")  # Render de foutmelding in rood
			error_text_rect = error_text.get_rect(center=(740, 225))  # Plaats de foutmelding in het midden
			screen.blit(error_text, error_text_rect)

		# Event handling: kijkt naar gebruikersinput en voert actie uit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			# Kijkt of er op een knop geklikt is
			if event.type == pygame.MOUSEBUTTONDOWN:
				if register_button.check_for_input(register_mouse_pos):  # Als de registreren knop wordt aangeklikt
					username = username_input.text  # Verkrijg de tekst uit de gebruikersnaam invoerveld
					password = password_input.text  # Verkrijg de tekst uit het wachtwoord invoerveld
					try:
						# Probeer de nieuwe gebruiker in de database in te voegen
						cursor.execute("INSERT INTO players (username, password) VALUES (?, ?)", (username, password))
						connection.commit()  # Bevestig de wijziging in de database
						login_menu()  # Ga naar het loginmenu na succesvolle registratie
					except sqlite3.IntegrityError:  # Als de gebruikersnaam al bestaat, geef een foutmelding
						error_message = "Username already taken! Try a different one."

				if back_button.check_for_input(register_mouse_pos):  # Als de terug-knop wordt aangeklikt
					login_menu()  # Ga terug naar het loginmenu

			# Verwerk events voor de tekstvelden (bijv. typen in de velden)
			username_input.handle_event(event)
			password_input.handle_event(event)

		# Werk het scherm bij zodat de wijzigingen zichtbaar zijn
		pygame.display.update()

def main_menu():
	"""Toon het hoofdmenu van het spel."""
	# Begin een oneindige lus om het menu weer te geven totdat de gebruiker een keuze maakt of het programma afsluit.
	while True:
		# Teken de achtergrondafbeelding op het scherm
		screen.blit(BG, (0, 0))
		# Verkrijg de huidige positie van de muis
		menu_mouse_pos = pygame.mouse.get_pos()

		# Stel de titeltekst "MAIN MENU" in en positioneer deze bovenaan het scherm
		menu_text = get_font(100).render("MAIN MENU", True, "#008fff")
		menu_rect = menu_text.get_rect(center=(640, 100))

		# Drie knoppen in het hoofdmenu:
		play_button = Button(
			image=pygame.image.load("assets/Play Rect.png"),
			pos=(640, 250),
			text_input="PLAY",
			font=get_font(75),
			base_color="#0c7708",
			hovering_color="Green"
		)

		leaderboard_button = Button(
			image=pygame.image.load("assets/Leaderboard Rect.png"),
			pos=(640, 400),
			text_input="LEADERBOARD",
			font=get_font(75),
			base_color="#775608",
			hovering_color="Orange"
		)

		quit_button = Button(
			image=pygame.image.load("assets/Quit Rect.png"),
			pos=(640, 550),
			text_input="QUIT",
			font=get_font(75),
			base_color="#770808",
			hovering_color="Red"
		)

		# Plaats de titeltekst op het scherm
		screen.blit(menu_text, menu_rect)

		# Voor elk van de drie knoppen, verander de kleur als de muis erover beweegt en teken ze op het scherm
		for button in [play_button, leaderboard_button, quit_button]:
			button.change_color(menu_mouse_pos)
			button.update(screen)

		# Gebeurtenissen verwerken op basis van gebruikersinvoer
		for event in pygame.event.get():
			# Sluit het spel als het afsluitevenement wordt gedetecteerd
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			# Detecteer muiskliks en voer acties uit afhankelijk van de knop waarop wordt geklikt
			if event.type == pygame.MOUSEBUTTONDOWN:
				# Check of de 'PLAY' knop is aangeklikt om naar het inlogmenu te gaan
				if play_button.check_for_input(menu_mouse_pos):
					login_menu()
				# Check of de 'LEADERBOARD' knop is aangeklikt om het leaderboard te tonen
				if leaderboard_button.check_for_input(menu_mouse_pos):
					leaderboard()
				# Check of de 'QUIT' knop is aangeklikt om het spel te sluiten
				if quit_button.check_for_input(menu_mouse_pos):
					pygame.quit()
					sys.exit()

		# Update het scherm om alle wijzigingen door te voeren
		pygame.display.update()

def connect_db():
    conn = sqlite3.connect('blackjack.db')	#verbind met de database
    return conn	#retourneeren van verbidingsobject

def update_score(username, outcome):
	"""Update de score van een gebruiker in de database."""
	# Controleer of er een geldige gebruikersnaam is opgegeven
	if username is None:
		return

	# Maak verbinding met de database en initialiseer de cursor voor SQL-bewerkingen
	conn = connect_db()
	cursor = conn.cursor()

	# Voer een update uit afhankelijk van de uitkomst van het spel
	if outcome == 1:  # Winst
		cursor.execute("UPDATE players SET wins = wins + 1 WHERE username = ?", (username,))
	elif outcome == -1:  # Verlies
		cursor.execute("UPDATE players SET losses = losses + 1 WHERE username = ?", (username,))
	elif outcome == 0:  # Gelijkspel
		cursor.execute("UPDATE players SET draws = draws + 1 WHERE username = ?", (username,))

	# Commit de wijzigingen en sluit de verbinding
	conn.commit()
	conn.close()

def get_user_record(username):
	# Maak verbinding met de database en initialiseer de cursor voor SQL-bewerkingen
	conn = connect_db()
	cursor = conn.cursor()

	# Voer een query uit om de statistieken van de gebruiker op te halen
	cursor.execute("SELECT wins, losses, draws FROM players WHERE username = ?", (username,))
	record = cursor.fetchone()  # Haal het resultaat van de query op

	# Sluit de verbinding en retourneer de statistieken
	conn.close()
	return record if record else (0, 0, 0)  # Retourneer (0, 0, 0) als er geen resultaten zijn gevonden

def leaderboard():
	"""Toon het leaderboard met de top 10 spelers op basis van overwinningen."""
	while True:
		# Haal de huidige muispositie op voor interactie met de terugknop
		leaderboard_mouse_pos = pygame.mouse.get_pos()

		# Laadt en toont de achtergrondafbeelding
		screen.blit(pygame.image.load("assets/LeaderboardBG.jpg"), (0, 0))

		# Creëer en toon de leaderboard-titel
		leaderboard_text = get_font(45).render("Most Wins Leaderboard:", True, "Gold")
		leaderboard_rect = leaderboard_text.get_rect(center=(640, 50))
		screen.blit(leaderboard_text, leaderboard_rect)

		# Haal de top 10 spelersgegevens op gesorteerd op aantal overwinningen
		cursor.execute("SELECT username, wins FROM players ORDER BY wins DESC LIMIT 10")
		players_data = cursor.fetchall()

		# Begin Y-positie voor het weergeven van spelersgegevens
		start_y = 150

		# Loop door elke speler en toon de rang, gebruikersnaam en aantal overwinningen
		for index, (username, wins) in enumerate(players_data):
			player_text = get_font(30).render(f"{index + 1}. {username} - Wins: {wins}", True, "White")
			player_rect = player_text.get_rect(center=(640, start_y))
			screen.blit(player_text, player_rect)
			start_y += 50  # Verplaats de Y-positie naar beneden voor de volgende speler

		# Maak en toon de 'BACK'-knop onderaan het scherm
		leaderboard_back = Button(
			image=None, pos=(640, 660),
			text_input="BACK", font=get_font(75),
			base_color="Darkred", hovering_color="Red"
		)

		# Verander kleur van de 'BACK'-knop op basis van hover status en toon de knop
		leaderboard_back.change_color(leaderboard_mouse_pos)
		leaderboard_back.update(screen)

		# Verwerk events voor sluiting of knopinteractie
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				# Check of de 'BACK'-knop is ingedrukt en ga terug naar het hoofdmenu als dat het geval is
				if leaderboard_back.check_for_input(leaderboard_mouse_pos):
					main_menu()

		# Update het scherm om de veranderingen zichtbaar te maken
		pygame.display.update()

def deal_cards(current_hand, current_deck):
	"""Deel een kaart aan de huidige hand van de speler/dealer en verwijder deze uit het deck."""
	card = random.randint(0, len(current_deck) - 1)  # Kies willekeurige kaart
	current_hand.append(current_deck[card])  # Voeg kaart toe aan huidige hand
	current_deck.pop(card)  # Verwijder kaart uit deck
	return current_hand, current_deck

def draw_scores(player, dealer):
	"""Toon de scores van de speler en de dealer op het scherm."""
	screen.blit(font.render(f'Score[{player}]', True, 'white'), (350, 400))  # Toon spelerscore
	if reveal_dealer:
		screen.blit(font.render(f'Score[{dealer}]', True, 'white'), (350, 100))  # Toon dealerscore indien toegestaan

def draw_cards(player, dealer, reveal):
	"""Toon de kaarten van zowel speler als dealer op het scherm."""
	# Teken de kaarten van de speler
	for i in range(len(player)):
		pygame.draw.rect(screen, 'white', [70 + (70 * i), 330 + (5 * i), 120, 220], 0, 5)  # Kaart achtergrond
		screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 335 + 5 * i))  # Kaartsymbool
		screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 505 + 5 * i)) # Kaartsymbool
		pygame.draw.rect(screen, 'red', [70 + (70 * i), 330 + (5 * i), 120, 220], 5, 5)  # Kaartomranding

	# Teken de kaarten van de dealer
	for i in range(len(dealer)):
		pygame.draw.rect(screen, 'white', [70 + (70 * i), 60 + (5 * i), 120, 220], 0, 5)
		if i != 0 or reveal:  # Open de kaart of toon ??? indien niet open
			screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 65 + 5 * i))
			screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 235 + 5 * i))
		else:
			screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 65 + 5 * i))  # Verborgen kaart
			screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 235 + 5 * i)) #Verborgen kaart
		pygame.draw.rect(screen, 'blue', [70 + (70 * i), 60 + (5 * i), 120, 220], 5, 5)  # Kaartomranding

def calculate_score(hand):
	"""Bereken de score van een gegeven hand met Aas als 1 of 11, afhankelijk van de score."""
	hand_score = 0
	aces_count = hand.count('A')  # Tel het aantal azen in de hand

	# Bereken basisscore
	for card in hand:
		if card in ['J', 'Q', 'K']:
			hand_score += 10  # Plaatjeskaarten zijn 10 punten waard
		elif card == 'A':
			hand_score += 11  # Azen worden eerst als 11 geteld
		else:
			hand_score += int(card)  # Andere kaarten worden hun cijferwaarde

	# Pas score aan indien boven 21 en Azen aanwezig zijn
	while hand_score > 21 and aces_count > 0:
		hand_score -= 10  # Aas telt nu als 1 in plaats van 11
		aces_count -= 1  # Verminder aantal Azen dat als 11 werd geteld

	return hand_score


def draw_game(act, result):
	"""Toon de spelinterface op basis van de actieve status en de uitkomst."""
	button_list = []

	# Controleer of het spel inactief is
	if not act:
		# Teken de "DEAL HAND"-knop wanneer het spel nog niet is gestart.
		deal = pygame.draw.rect(screen, 'white', [500, 20, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [500, 20, 300, 100], 3, 5)
		deal_text = font.render('DEAL HAND', True, 'black')
		screen.blit(deal_text, (515, 50))
		button_list.append(deal)  # Voeg de knop toe aan de lijst
	else:
		# Als het spel actief is, haal dan de statistieken van de gebruiker op
		record = get_user_record(logged_in_user)
		score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
		screen.blit(score_text, (15, 675))  # Toon de statistieken op het scherm

		# Teken de "HIT ME"-knop voor de speler om een kaart te trekken
		hit = pygame.draw.rect(screen, 'white', [0, 560, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [0, 560, 300, 100], 3, 5)
		hit_text = font.render('HIT ME', True, 'black')
		screen.blit(hit_text, (55, 595))
		button_list.append(hit)  # Voeg de "HIT ME"-knop toe aan de lijst

		# Teken de "STAND"-knop voor de speler om te passen
		stand = pygame.draw.rect(screen, 'white', [300, 560, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [300, 560, 300, 100], 3, 5)
		stand_text = font.render('STAND', True, 'black')
		screen.blit(stand_text, (355, 595))
		button_list.append(stand)  # Voeg de "STAND"-knop toe aan de lijst

	# Controleer of er een resultaat is van de huidige ronde
	if result != 0:
		# Toon het resultaatbericht op het scherm
		screen.blit(font.render(results[result], True, 'white'), (15, 10))

		# Teken de "NEW HAND"-knop om een nieuwe ronde te starten na een spelresultaat
		deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
		pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
		pygame.draw.rect(screen, 'black', [153, 223, 294, 94], 3, 5)
		deal_text = font.render('NEW HAND', True, 'black')
		screen.blit(deal_text, (165, 250))
		button_list.append(deal)  # Voeg de "NEW HAND"-knop toe aan de lijst

	# Retourneer de lijst met knoppen voor verdere interactiecontrole
	return button_list

def check_endgame(hand_act, deal_score, play_score, result, totals, add):
	"""Controleer of het spel is afgelopen en bepaal de uitkomst."""
	if not hand_act and deal_score >= 17:
		if play_score > 21:
			result = 1  # Verlies als speler boven 21 punten zit
		elif deal_score < play_score <= 21 or deal_score > 21:
			result = 2  # Winst als speler hoger scoort dan dealer of dealer > 21
		elif play_score < deal_score <= 21:
			result = 3  # Verlies als dealer hoger scoort
		else:
			result = 4  # Gelijkspel

		if add:
			if result == 1 or result == 3:
				totals[1] += 1
				update_score(logged_in_user, -1)  # Verlies
			elif result == 2:
				totals[0] += 1
				update_score(logged_in_user, 1)  # Winst
			elif result == 4:
				totals[2] += 1
				update_score(logged_in_user, 0)  # Gelijkspel
			add = False  # Score eenmaal bijgewerkt

	return result, totals, add

def blackjack_game():
	"""Spelmodus voor Blackjack met de belangrijkste spelmechanismen."""
	# Globale variabelen die worden gebruikt in het spel
	global player_score, dealer_score, my_hand, dealer_hand, initial_deal, reveal_dealer, active, hand_active, add_score, outcome, records, game_deck

	# Stel het venster in met de titel 'Pygame Blackjack!'
	pygame.display.set_caption('Pygame Blackjack!')

	# Initialiseer de terugknop voor het navigeren naar het hoofdmenu
	back_button = Button(
		image=None,
		pos=(1200, 660),
		text_input="BACK",
		font=get_font(35),
		base_color="Darkred",
		hovering_color="Red"
	)

	# Zet de run-loop aan
	run = True
	while run:
		# Stel de frames per seconde in op 60
		timer.tick(60)
		# Plaats de achtergrondafbeelding
		screen.blit(pygame.image.load('assets/TopViewBjTable.jpg'), (0, 0))

		# Controleer of een nieuwe hand moet worden gedeeld
		if initial_deal:
			for i in range(2):
				my_hand, game_deck = deal_cards(my_hand, game_deck)
				dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
			initial_deal = False

		# Controleer of het spel actief is
		if active:
			# Bereken de score van de speler
			player_score = calculate_score(my_hand)
			# Teken de kaarten van de speler en de dealer
			draw_cards(my_hand, dealer_hand, reveal_dealer)
			# Als de dealerkaarten zichtbaar zijn, bereken de dealerscore
			if reveal_dealer:
				dealer_score = calculate_score(dealer_hand)
				if dealer_score < 17:
					dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
			# Toon de scores op het scherm
			draw_scores(player_score, dealer_score)

		# Tekent de knoppen voor het spel, afhankelijk van de status
		buttons = draw_game(active, outcome)

		# Verander de kleur van de terugknop wanneer de muis eroverheen gaat
		back_button.change_color(pygame.mouse.get_pos())
		back_button.update(screen)

		# Haal de huidige gebeurtenissen op en verwerk gebruikersinput
		for event in pygame.event.get():
			# Controleer of het spel moet worden afgesloten
			if event.type == pygame.QUIT:
				run = False
			# Controleer muiskliks
			if event.type == pygame.MOUSEBUTTONUP:
				# Controleer of de terugknop is aangeklikt
				if back_button.check_for_input(pygame.mouse.get_pos()):
					main_menu()  # Ga terug naar het hoofdmenu
					return

				# Controleer of de 'DEAL HAND'-knop is aangeklikt wanneer het spel niet actief is
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
					# Controleer of de 'HIT ME'-knop is aangeklikt
					if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
						my_hand, game_deck = deal_cards(my_hand, game_deck)
					# Controleer of de 'STAND'-knop is aangeklikt
					elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
						reveal_dealer = True
						hand_active = False
					# Controleer of de 'NEW HAND'-knop is aangeklikt (wanneer een spelresultaat beschikbaar is)
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

		# Controleer automatisch of de speler een natuurlijke Blackjack of bust heeft
		if hand_active and player_score >= 21:
			hand_active = False
			reveal_dealer = True

		# Controleer het einde van de ronde en werk het spelresultaat en de records bij
		outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records,
													add_score)

		# Werk het scherm bij met nieuwe frames
		pygame.display.flip()

	# Sluit Pygame af wanneer de run-loop eindigt
	pygame.quit()


# Start het spel door terug te keren naar het hoofdmenu
main_menu()