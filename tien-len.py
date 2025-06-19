import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple, Optional

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tien Len Mien Nam - Vietnamese Poker")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
DARK_GREEN = (0, 100, 0)

font_small = pygame.font.SysFont('arial', 20)
font_medium = pygame.font.SysFont('arial', 28)
font_large = pygame.font.SysFont('arial', 40)

class Suit(Enum):
    SPADES = 0
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3

class Card:
    def __init__(self, suit: Suit, value: int):
        self.suit = suit
        self.value = value
        
    def get_display_value(self):
        if self.value <= 10:
            return str(self.value)
        elif self.value == 11:
            return "J"
        elif self.value == 12:
            return "Q"
        elif self.value == 13:
            return "K"
        elif self.value == 14:
            return "A"
        elif self.value == 15:
            return "2"
    
    def get_suit_symbol(self):
        symbols = {Suit.SPADES: "♠", Suit.CLUBS: "♣", Suit.DIAMONDS: "♦", Suit.HEARTS: "♥"}
        return symbols[self.suit]
    
    def get_sort_value(self):
        if self.value == 3 and self.suit == Suit.SPADES:
            return 0
        elif self.value == 3:
            return self.value * 10 + self.suit.value
        else:
            return self.value * 10 + self.suit.value
    
    def __lt__(self, other):
        return self.get_sort_value() < other.get_sort_value()
    
    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value

class HandType(Enum):
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    QUAD = 4
    STRAIGHT = 5

class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards)
        self.hand_type = self._determine_type()
        self.rank = self._get_rank()
    
    def _determine_type(self) -> HandType:
        if len(self.cards) == 1:
            return HandType.SINGLE
        elif len(self.cards) == 2 and self.cards[0].value == self.cards[1].value:
            return HandType.PAIR
        elif len(self.cards) == 3 and all(c.value == self.cards[0].value for c in self.cards):
            return HandType.TRIPLE
        elif len(self.cards) == 4 and all(c.value == self.cards[0].value for c in self.cards):
            return HandType.QUAD
        elif len(self.cards) == 5 and self._is_straight():
            return HandType.STRAIGHT
        else:
            return None
    
    def _is_straight(self) -> bool:
        if len(self.cards) != 5:
            return False
        values = [c.value for c in self.cards]
        values.sort()
        for i in range(1, 5):
            if values[i] != values[i-1] + 1:
                return False
        return True
    
    def _get_rank(self) -> int:
        if self.hand_type == HandType.SINGLE:
            return self.cards[0].get_sort_value()
        elif self.hand_type == HandType.PAIR:
            return self.cards[0].value * 100 + max(c.suit.value for c in self.cards)
        elif self.hand_type == HandType.TRIPLE:
            return self.cards[0].value * 1000
        elif self.hand_type == HandType.QUAD:
            return self.cards[0].value * 10000
        elif self.hand_type == HandType.STRAIGHT:
            return max(c.value for c in self.cards) * 100
        return 0
    
    def can_beat(self, other_hand) -> bool:
        if not other_hand:
            return True
        if self.hand_type != other_hand.hand_type:
            return False
        if len(self.cards) != len(other_hand.cards):
            return False
        return self.rank > other_hand.rank

class Player:
    def __init__(self, name: str, is_human: bool = False):
        self.name = name
        self.cards = []
        self.is_human = is_human
        self.selected_cards = []
    
    def add_card(self, card: Card):
        self.cards.append(card)
        self.cards.sort()
    
    def remove_cards(self, cards: List[Card]):
        for card in cards:
            if card in self.cards:
                self.cards.remove(card)
    
    def has_3_spades(self) -> bool:
        return any(card.value == 3 and card.suit == Suit.SPADES for card in self.cards)

class Game:
    def __init__(self):
        self.players = [
            Player("You", is_human=True),
            Player("Player 1"),
            Player("Player 2"), 
            Player("Player 3")
        ]
        
        self.current_player = 0
        self.last_hand = None
        self.last_player = None
        self.game_started = False
        self.winner = None
        self.passes = 0
        self.ai_played_time = 0
        self.last_played_info = None
        
    def create_deck(self) -> List[Card]:
        deck = []
        for suit in Suit:
            for value in range(3, 16):
                deck.append(Card(suit, value))
        return deck
    
    def deal_cards(self):
        deck = self.create_deck()
        random.shuffle(deck)
        
        for i, card in enumerate(deck):
            self.players[i % 4].add_card(card)
        
        for i, player in enumerate(self.players):
            if player.has_3_spades():
                self.current_player = i
                break
        
        self.game_started = True
    
    def get_valid_moves(self, player: Player) -> List[List[Card]]:
        if not self.last_hand:
            valid_moves = []
            for card in player.cards:
                if card.value == 3 and card.suit == Suit.SPADES:
                    valid_moves.append([card])
            return valid_moves
        
        valid_moves = []
        cards = player.cards
        
        if self.last_hand.hand_type == HandType.SINGLE:
            for card in cards:
                hand = Hand([card])
                if hand.can_beat(self.last_hand):
                    valid_moves.append([card])
        
        elif self.last_hand.hand_type == HandType.PAIR:
            for i in range(len(cards)-1):
                if cards[i].value == cards[i+1].value:
                    hand = Hand([cards[i], cards[i+1]])
                    if hand.can_beat(self.last_hand):
                        valid_moves.append([cards[i], cards[i+1]])
        
        elif self.last_hand.hand_type == HandType.TRIPLE:
            for i in range(len(cards)-2):
                if (cards[i].value == cards[i+1].value == cards[i+2].value):
                    hand = Hand([cards[i], cards[i+1], cards[i+2]])
                    if hand.can_beat(self.last_hand):
                        valid_moves.append([cards[i], cards[i+1], cards[i+2]])
        
        elif self.last_hand.hand_type == HandType.QUAD:
            for i in range(len(cards)-3):
                if (cards[i].value == cards[i+1].value == cards[i+2].value == cards[i+3].value):
                    hand = Hand([cards[i], cards[i+1], cards[i+2], cards[i+3]])
                    if hand.can_beat(self.last_hand):
                        valid_moves.append([cards[i], cards[i+1], cards[i+2], cards[i+3]])
        
        elif self.last_hand.hand_type == HandType.STRAIGHT:
            for i in range(len(cards)-4):
                straight_cards = cards[i:i+5]
                if len(set(c.value for c in straight_cards)) == 5:
                    values = sorted([c.value for c in straight_cards])
                    if all(values[j] == values[j-1] + 1 for j in range(1, 5)):
                        hand = Hand(straight_cards)
                        if hand.can_beat(self.last_hand):
                            valid_moves.append(straight_cards)
        
        return valid_moves
    
    def ai_play(self, player: Player):
        valid_moves = self.get_valid_moves(player)
        
        if not valid_moves:
            self.passes += 1
            self.next_turn()
            return
        
        chosen_move = valid_moves[0]
        self.play_cards(player, chosen_move)
    
    def play_cards(self, player: Player, cards: List[Card]):
        hand = Hand(cards)
        
        if not self.last_hand or hand.can_beat(self.last_hand):
            player.remove_cards(cards)
            self.last_hand = hand
            self.last_player = self.current_player
            self.last_played_info = (player.name, cards)
            self.passes = 0
            
            if len(player.cards) == 0:
                self.winner = player
                return
            
            self.next_turn()
    
    def next_turn(self):
        self.current_player = (self.current_player - 1) % 4
        
        if self.passes >= 3:
            self.last_hand = None
            self.last_played_info = None
            self.passes = 0
    
    def is_current_player_human(self):
        return self.players[self.current_player].is_human

def draw_card_back(surface, x: int, y: int, width: int, height: int):
    pygame.draw.rect(surface, BLUE, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)
    
    for i in range(3):
        for j in range(4):
            dot_x = x + 10 + i * 15
            dot_y = y + 10 + j * 15
            pygame.draw.circle(surface, WHITE, (dot_x, dot_y), 2)

def draw_card(surface, card: Card, x: int, y: int, width: int, height: int, selected: bool = False, face_up: bool = True):
    if not face_up:
        draw_card_back(surface, x, y, width, height)
        return
        
    color = YELLOW if selected else WHITE
    
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)
    
    text_color = RED if card.suit in [Suit.HEARTS, Suit.DIAMONDS] else BLACK
    
    value_text = font_small.render(card.get_display_value(), True, text_color)
    surface.blit(value_text, (x + 3, y + 3))
    
    suit_text = font_small.render(card.get_suit_symbol(), True, text_color)
    surface.blit(suit_text, (x + width - 18, y + height - 25))

def draw_player_cards(surface, player: Player, x: int, y: int, clickable: bool = False, show_cards: bool = True, horizontal: bool = True):
    card_width = 50
    card_height = 70
    overlap = 40
    
    if horizontal:
        for i, card in enumerate(player.cards):
            card_x = x + i * overlap
            card_y = y
            selected = clickable and card in player.selected_cards
            draw_card(surface, card, card_x, card_y, card_width, card_height, selected, show_cards)
    else:
        for i, card in enumerate(player.cards):
            card_x = x
            card_y = y + i * (overlap // 2)
            selected = clickable and card in player.selected_cards
            draw_card(surface, card, card_x, card_y, card_width, card_height, selected, show_cards)
    
    name_color = YELLOW if clickable else WHITE
    name_text = font_small.render(player.name, True, name_color)
    if horizontal:
        surface.blit(name_text, (x, y - 25))
        count_text = font_small.render(f"Cards: {len(player.cards)}", True, WHITE)
        surface.blit(count_text, (x, y + card_height + 3))
    else:
        surface.blit(name_text, (x + card_width + 5, y))
        count_text = font_small.render(f"Cards: {len(player.cards)}", True, WHITE)
        surface.blit(count_text, (x + card_width + 5, y + 20))

def handle_card_click(player: Player, mouse_pos: Tuple[int, int], cards_x: int, cards_y: int, horizontal: bool = True):
    card_width = 50
    card_height = 70
    overlap = 40
    
    for i, card in enumerate(player.cards):
        if horizontal:
            card_x = cards_x + i * overlap
            card_y = cards_y
        else:
            card_x = cards_x
            card_y = cards_y + i * (overlap // 2)
            
        if (card_x <= mouse_pos[0] <= card_x + card_width and 
            card_y <= mouse_pos[1] <= card_y + card_height):
            
            if card in player.selected_cards:
                player.selected_cards.remove(card)
            else:
                player.selected_cards.append(card)
            break

def get_card_description(cards: List[Card]) -> str:
    if len(cards) == 1:
        card = cards[0]
        suit_names = {
            Suit.SPADES: "spades", Suit.CLUBS: "clubs", 
            Suit.DIAMONDS: "diamonds", Suit.HEARTS: "hearts"
        }
        return f"{card.get_display_value()} of {suit_names[card.suit]}"
    elif len(cards) == 2:
        return f"pair of {cards[0].get_display_value()}s"
    elif len(cards) == 3:
        return f"triple {cards[0].get_display_value()}s"
    elif len(cards) == 4:
        return f"quad {cards[0].get_display_value()}s"
    elif len(cards) == 5:
        return f"straight {cards[0].get_display_value()}-{cards[-1].get_display_value()}"
    else:
        return f"{len(cards)} cards"

def draw_start_screen(surface):
    surface.fill(DARK_GREEN)
    
    title_text = font_large.render("TIEN LEN - VIETNAMESE POKER", True, YELLOW)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 200))
    surface.blit(title_text, title_rect)
    
    subtitle_text = font_medium.render("Click to start game:", True, WHITE)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 300))
    surface.blit(subtitle_text, subtitle_rect)
    
    button_width = 200
    button_height = 60
    button_x = SCREEN_WIDTH//2 - button_width//2
    button_y = 400
    
    start_button = pygame.Rect(button_x, button_y, button_width, button_height)
    
    pygame.draw.rect(surface, LIGHT_GRAY, start_button)
    pygame.draw.rect(surface, BLACK, start_button, 2)
    
    button_text = font_medium.render("Start Game", True, BLACK)
    text_rect = button_text.get_rect(center=start_button.center)
    surface.blit(button_text, text_rect)
    
    return start_button

def main():
    clock = pygame.time.Clock()
    game = None
    start_mode = True
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if start_mode:
                    start_button = draw_start_screen(screen)
                    if start_button.collidepoint(mouse_pos):
                        game = Game()
                        game.deal_cards()
                        start_mode = False
                
                elif game and game.game_started:
                    play_button = pygame.Rect(50, 550, 80, 40)
                    pass_button = pygame.Rect(140, 550, 80, 40)
                    restart_button = pygame.Rect(230, 550, 80, 40)
                    
                    if restart_button.collidepoint(mouse_pos):
                        start_mode = True
                        game = None
                    
                    elif game.winner and mouse_pos:
                        start_mode = True
                        game = None
                    
                    elif play_button.collidepoint(mouse_pos) and game.is_current_player_human():
                        current_player = game.players[game.current_player]
                        if current_player.selected_cards:
                            hand = Hand(current_player.selected_cards)
                            if not game.last_hand or hand.can_beat(game.last_hand):
                                game.play_cards(current_player, current_player.selected_cards.copy())
                                current_player.selected_cards.clear()
                    
                    elif pass_button.collidepoint(mouse_pos) and game.is_current_player_human():
                        game.passes += 1
                        game.next_turn()
                    
                    elif game.is_current_player_human():
                        player_positions = [
                            (300, 680, True),   
                            (50, 200, False),  
                            (300, 50, True),    
                            (1050, 200, False)  
                        ]
                        
                        for i, player in enumerate(game.players):
                            if player.is_human and i == game.current_player:
                                pos_x, pos_y, is_horizontal = player_positions[i]
                                handle_card_click(player, mouse_pos, pos_x, pos_y, is_horizontal)
        
        if start_mode:
            draw_start_screen(screen)
        
        elif game and game.game_started:
            current_time = pygame.time.get_ticks()
            
            if not game.winner and not game.is_current_player_human():
                if game.ai_played_time == 0:
                    game.ai_played_time = current_time
                elif current_time - game.ai_played_time >= 5000:
                    game.ai_play(game.players[game.current_player])
                    game.ai_played_time = 0
            
            screen.fill(GREEN)
            
            play_button = pygame.Rect(50, 550, 80, 40)
            pass_button = pygame.Rect(140, 550, 80, 40)
            restart_button = pygame.Rect(230, 550, 80, 40)
            
            pygame.draw.rect(screen, LIGHT_GRAY, play_button)
            pygame.draw.rect(screen, LIGHT_GRAY, pass_button) 
            pygame.draw.rect(screen, LIGHT_GRAY, restart_button)
            pygame.draw.rect(screen, BLACK, play_button, 2)
            pygame.draw.rect(screen, BLACK, pass_button, 2)
            pygame.draw.rect(screen, BLACK, restart_button, 2)
            
            play_text = font_medium.render("Play", True, BLACK)
            pass_text = font_medium.render("Pass", True, BLACK)
            restart_text = font_small.render("Menu", True, BLACK)
            
            play_rect = play_text.get_rect(center=play_button.center)
            pass_rect = pass_text.get_rect(center=pass_button.center)
            restart_rect = restart_text.get_rect(center=restart_button.center)
            
            screen.blit(play_text, play_rect)
            screen.blit(pass_text, pass_rect)
            screen.blit(restart_text, restart_rect)
            
            player_positions = [
                (300, 680, True),   
                (50, 200, False),   
                (300, 50, True),    
                (1050, 200, False) 
            ]
            
            for i, player in enumerate(game.players):
                pos_x, pos_y, is_horizontal = player_positions[i]
                clickable = player.is_human and i == game.current_player
                show_cards = player.is_human
                draw_player_cards(screen, player, pos_x, pos_y, clickable, show_cards, is_horizontal)
            
            current_text = font_medium.render(f"Turn: {game.players[game.current_player].name}", True, YELLOW)
            screen.blit(current_text, (400, 300))
            
            if game.last_played_info:
                player_name, played_cards = game.last_played_info
                description = get_card_description(played_cards)
                
                info_text = font_small.render(f"{player_name} played: {description}", True, WHITE)
                screen.blit(info_text, (400, 340))
                
                for i, card in enumerate(played_cards):
                    draw_card(screen, card, 400 + i * 60, 360, 50, 70)
            
            elif game.last_hand:
                last_hand_text = font_small.render("Last played:", True, WHITE)
                screen.blit(last_hand_text, (400, 340))
                
                for i, card in enumerate(game.last_hand.cards):
                    draw_card(screen, card, 400 + i * 60, 360, 50, 70)
            
            if game.winner:
                winner_text = font_large.render(f"{game.winner.name} WINS!", True, YELLOW)
                winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(winner_text, winner_rect)
                
                restart_text = font_small.render("Click to return to start screen", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
                screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()