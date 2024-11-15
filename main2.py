import pygame
import random
import serial
import os
import csv
from datetime import datetime

# Initialisation de la connexion série avec l'Arduino
ser = serial.Serial('COM4', 115200, timeout=1)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Font setup
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 36)

# Colors
BEIGE = (210,180,140)
GRAY = (169,169,169)
RED = (255,0,0)
BLUE = (0,0,255)
BLACK = (0,0,0)

# File for saving scores
SCORES_FILE = "scores.txt"

class Don: #les Don sont les cibles qui défilent
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
    
    def move_left(self):
        self.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Game: #c'est ici que se déroule la partie
    def __init__(self, player_name):
        self.dons = []
        self.time_counter = 0
        self.score = 0
        self.streak = 0
        self.beststreak = 0
        self.target_x = 200
        self.target_y = 360
        self.target_radius = 60
        self.control_color = GRAY
        self.paused = False
        self.game_over = False
        self.player_name = player_name
        self.error_count = 0  # Compteur d'erreurs
        self.max_errors = 3  # Nombre d'erreurs avant la fin du jeu
        self.cumul_error=0 #nombre total erreurs faites
        self.click_count = 0  # Compteur de clics
        self.min_spawn_time = 15  # Temps minimum entre deux apparitions (en frames)
        self.max_spawn_time = 50  # Temps maximum entre deux apparitions (en frames)
        self.current_spawn_time = random.randint(self.min_spawn_time, self.max_spawn_time)
        
        # Paramètres de la vitesse
        self.global_speed = 10  # Vitesse initiale de tous les dons
        self.speed_increment = 0.3  # Incrément de vitesse 
        self.max_speed = 40  # Vitesse maximale que les dons peuvent atteindre
        self.spawn_timer = 0  # Timer pour la gestion du spawn des dons
        self.speed_increment_timer = 0  # Timer pour limiter la fréquence d'augmentation de la vitesse

        # Le rect du contrôle (zone où le joueur peut interagir)
        self.control_rect = pygame.Rect(self.target_x - self.target_radius, self.target_y - self.target_radius,
                                        self.target_radius * 2, self.target_radius * 2)
        
        # Temps de jeu
        self.start_time = pygame.time.get_ticks()  # Temps de départ du jeu
    
    def save_score(self, score, best_streak, game_time, click_count, cumul_error): #cette fonction enregistre les fichiers csv
        # Créer un fichier CSV pour chaque joueur
        filename = f"{self.player_name}.csv"
        
        # Vérifier si le fichier existe déjà
        file_exists = os.path.exists(filename)
        
        # Ouvrir le fichier en mode ajout (append)
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Si le fichier n'existe pas, ajouter l'en-tête
            if not file_exists:
                writer.writerow(['Date', 'Score', 'Best Streak', 'Game Time (seconds)', 'Click Count', 'Error Count'])
            # Ajouter la ligne avec la date, le score, le meilleur streak, le temps de jeu, les clics et les erreurs
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), score, best_streak, game_time, click_count, cumul_error])

    def save_score_txt(self, name, score): #ce fichier txt permet d'avoir tous les scores au meme endroit pour le leaderboard
        with open(SCORES_FILE, "a") as file:
            file.write(f"{name},{score}\n")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over:
                        game_time = (pygame.time.get_ticks() - self.start_time) / 1000  # Temps en secondes
                        self.save_score(self.score, self.beststreak, game_time, self.click_count, self.cumul_error)  # Sauvegarde du score avant de quitter
                        return "menu"
                    self.paused = not self.paused
                elif event.key == pygame.K_p:           #ICI se trouve la pause en appuyant sur P
                    self.paused = not self.paused
                elif event.key == pygame.K_RETURN and self.game_over:
                    game_time = (pygame.time.get_ticks() - self.start_time) / 1000  # Temps en secondes
                    self.save_score(self.score, self.beststreak, game_time, self.click_count, self.cumul_error)  # Sauvegarde du score avant de quitter
                    self.save_score_txt(self.player_name, self.score)  # Enregistrer aussi dans scores.txt
                    return "menu"
                elif event.key == pygame.K_UP:
                    self.control_color = BLUE
                    self.click_count += 1  # Incrémenter le nombre de clics
                elif event.key == pygame.K_DOWN:
                    self.control_color = RED
                    self.click_count += 1  # Incrémenter le nombre de clics
            else:
                self.control_color = GRAY
        return "game"

    def update(self, screen):
        if self.paused:
            paused_text = font_large.render("PAUSED", True, RED)
            screen.blit(paused_text, (screen.get_width() // 2 - paused_text.get_width() // 2, 150))
            return

        if self.game_over:
            game_over_text = font_large.render(f"Game Over! Score: {self.score}", True, RED)
            continue_text = font_medium.render("Press ENTER to continue", True, RED)
            screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 150))
            screen.blit(continue_text, (screen.get_width() // 2 - continue_text.get_width() // 2, 220))
            return

        screen.fill(BEIGE)
        pygame.draw.circle(screen, self.control_color, (self.target_x, self.target_y), self.target_radius)

        # Instructions de contrôle
        controls_text = font_small.render("Controls: Up = Blue, Down = Red", True, (0, 0, 0))
        screen.blit(controls_text, (10, 680))

        # Gestion des dons
        for don in self.dons[:]:
            don.move_left()
            don.draw(screen)

            don_rect = don.get_rect()

            # Vérification des collisions
            if don_rect.colliderect(self.control_rect):
                if don.color == self.control_color:
                    self.score += 1
                    self.streak += 1
                    if self.streak > self.beststreak:
                        self.beststreak = self.streak
                    self.dons.remove(don)
                    self.error_count = 0

            elif don_rect.right < 0:  # Si le don quitte l'écran
                self.dons.remove(don)
                self.error_count += 1  # Incrémenter le nombre d'erreurs
                self.streak = 0
                self.cumul_error+=1

        # Fin du jeu si trop d'erreurs
        if self.error_count >= self.max_errors:
            self.game_over = True

        # Gestion du spawn des dons
        self.spawn_timer += 1
        if self.spawn_timer >= self.current_spawn_time:
            new_color = random.choice([RED, BLUE])
            new_don = Don(1280, 360, 40, new_color, self.global_speed)
            self.dons.append(new_don)
            self.spawn_timer = 0
            self.current_spawn_time = random.randint(self.min_spawn_time, self.max_spawn_time)

        # Augmentation de la vitesse
        self.speed_increment_timer += 1
        if self.speed_increment_timer >= 120:  # Toutes les 2.5 secondes (300 frames à 60 FPS)
            self.global_speed += self.speed_increment
            if self.global_speed > self.max_speed:
                self.global_speed = self.max_speed
            self.speed_increment_timer = 0

        # Affichage du score
        score_text = font_large.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        streak_text = font_medium.render(f"Best Streak: {self.beststreak}", True, (0, 0, 0))
        screen.blit(streak_text, (10, 50))
        steak_text = font_small.render(f"Streak: {self.streak}", True, (0, 0, 0))
        screen.blit(steak_text, (10, 80))


    def handle_input(self):
        # Lecture des entrées Arduino
        if ser.in_waiting > 0:
            try:
                button_input = ser.readline().decode('utf-8').strip()
                if button_input == "blue":
                    self.control_color = BLUE
                    self.key_pressed = True
                    self.click_count+=1
                elif button_input == "red":
                    self.control_color = RED 
                    self.key_pressed = True
                    self.click_count+=1
                elif button_input == "gray":
                    self.control_color = GRAY
                    self.key_pressed = False
            except:
                pass

class Menu: 
    def __init__(self):
        self.selected_option = 0
        self.options = ["Play", "Leaderboard", "Quit"] 

    def handle_events(self): #on peut defiler dans le menu avec les fleches
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:
                        return "name_input"
                    elif self.selected_option == 1:
                        return "leaderboard"
                    elif self.selected_option == 2:
                        return "quit"
        return "menu"

    def draw(self, screen):
        screen.fill(BEIGE)
        title = font_large.render("Main Menu", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        for i, option in enumerate(self.options):
            color = (0, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 250 + i * 100))
            screen.blit(text, text_rect)

class Leaderboard: #le leaderboard classe les joueurs avec leur score du meilleur au pire
    def __init__(self):
        self.leaderboard_data = self.load_leaderboard()

    def load_leaderboard(self):
        if not os.path.exists(SCORES_FILE): 
            return []
        with open(SCORES_FILE, "r") as file: #on recupère les scores dans scores.txt
            data = [line.strip().split(",") for line in file.readlines()]
        return [(name, score) for name, score in data]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return "menu"
        return "leaderboard"

    def draw(self, screen):
        screen.fill((50, 50, 50))
        title = font_large.render("Leaderboard", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title, title_rect)

        sorted_scores = sorted(self.leaderboard_data, key=lambda x: int(x[1]), reverse=True)[:10]
        
        for i, (name, score) in enumerate(sorted_scores):
            entry = font_medium.render(f"{i + 1}. {name} - {score}", True, (255, 255, 255))
            entry_rect = entry.get_rect(center=(screen.get_width() // 2, 150 + i * 60))
            screen.blit(entry, entry_rect)

        back_text = font_medium.render("Press ENTER or ESC to return", True, (255, 0, 0))
        back_rect = back_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        screen.blit(back_text, back_rect)

class NameInput: #cette classe est la page qui permet d'inscrire le nom du joueur
    def __init__(self):
        self.name = ""
        self.active = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.name:
                        return self.name
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
                else:
                    self.name += event.unicode
        return ""

    def draw(self, screen):
        screen.fill(BEIGE)
        input_text = font_large.render(f"Enter your name: {self.name}", True, (0, 0, 0))
        screen.blit(input_text, (10, screen.get_height() // 2))


def main():
    menu = Menu()
    leaderboard = Leaderboard()
    name_input = NameInput()
    game_state = "menu"
    running = True
    player_name = ""

    while running:
        if game_state == "menu":
            game_state = menu.handle_events()
            menu.draw(screen)
        elif game_state == "name_input":
            player_name = name_input.handle_events()
            if player_name:
                game = Game(player_name)  
                game_state = "game"
            name_input.draw(screen)
        elif game_state == "game":
            game_state = game.handle_events()
            game.handle_input()
            game.update(screen)
        elif game_state == "leaderboard":
            leaderboard.leaderboard_data = leaderboard.load_leaderboard()
            game_state = leaderboard.handle_events()
            leaderboard.draw(screen)
        elif game_state == "quit":
            running = False

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    ser.close()

if __name__ == "__main__":
    main()
