import pygame
import random
from entities import Player, Enemy, TankEnemy, DoubleShotEnemy, RapidFireEnemy, Bullet, Barrier

class Game:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height

        self.bg = (10, 10, 20)

        # player
        self.player = Player(x=width // 2, y=height - 60)
        self.bullets = []
        self.enemy_bullets = []

        # wave system
        self.wave = 1
        self.enemy_speed = 1
        self.enemy_direction = 1

        # enemies and barriers
        self.enemies = []
        self.barriers = []
        self.create_enemy_grid()
        self.create_barriers()

        # lives + respawn
        self.lives = 3
        self.player_respawn_time = 0
        self.game_over = False

        # score
        self.score = 0
        self.high_score = 0

        #title screen
        self.show_title_screen = True

    # create enemy grid
    def create_enemy_grid(self):
        self.enemies = []
        rows = 5
        cols = 10
        x_offset = 55
        y_offset = 40 

        for row in range(rows):
            for col in range(cols):
                x = x_offset + col * 60
                y = y_offset + row * 50

                # chance for special enemies increases each wave
                roll = random.random()
                special_chance = min(0.05 + self.wave * 0.02, 0.3)

                if roll < special_chance / 3:
                    self.enemies.append(TankEnemy(x, y))
                elif roll < special_chance * 2 / 3:
                    self.enemies.append(DoubleShotEnemy(x, y))
                elif roll < special_chance:
                    self.enemies.append(RapidFireEnemy(x, y))
                else:
                    self.enemies.append(Enemy(x, y))

    # barriers
    def create_barriers(self):
        self.barriers = []
        gap = self.width // 5
        y = self.height - 150

        for i in range(4):
            x = gap * (i + 1) - 30
            self.barriers.append(Barrier(x, y))

    # main update loop
    def update(self):

        # title screen
        if self.show_title_screen:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.show_title_screen = False  # Start the game
            return

        # game over
        if self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.restart_game()
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.bullets)

        if self.lives <= 0:
            if self.score > self.high_score:
                self.high_score = self.score
            self.game_over = True

        # player bullet    
        for bullet in self.bullets[:]:
            bullet.update()

            bullet_rect = pygame.Rect(
                bullet.x - bullet.radius,
                bullet.y - bullet.radius,
                bullet.radius * 2,
                bullet.radius * 2
            )

            #bullet hits enemy
            for enemy in self.enemies[:]:
                if bullet_rect.colliderect(enemy.get_rect()):
                    if enemy.take_damage():  # enemy HP decreases
                        self.enemies.remove(enemy)
                        self.score += 100  # normal kill reward
                    # Remove bullet after hit
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

            #bullet hits barrier
            if bullet in self.bullets:
                for barrier in self.barriers:
                    if barrier.health > 0 and bullet_rect.colliderect(barrier.rect):
                        barrier.take_damage()
                        self.bullets.remove(bullet)
                        break

        # remove bullets off-screen
        self.bullets = [b for b in self.bullets if b.y > 0]

        # enemy movement
        move_down = False

        for enemy in self.enemies:
            enemy.x += self.enemy_direction * self.enemy_speed

            
            if enemy.x <= 10 or enemy.x + enemy.width >= self.width - 10:
                move_down = True

        if move_down:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                enemy.y += 5

        # enemies shooting
        if len(self.enemies) > 0:
            shooter = random.choice(self.enemies)
            fire_chance = 0.02 + (self.wave * 0.01)

            if random.random() < fire_chance:

                #double shot
                if isinstance(shooter, DoubleShotEnemy):
                    for (bx, by) in shooter.shoot():
                        self.enemy_bullets.append(Bullet(bx, by, +1))

                #rapid fire
                elif isinstance(shooter, RapidFireEnemy):
                    cx = shooter.x + shooter.width // 2
                    cy = shooter.y + shooter.height
                    self.enemy_bullets.append(Bullet(cx, cy, +1))
                    if random.random() < 0.4:
                        self.enemy_bullets.append(Bullet(cx, cy, +1))

                #normal + tank enemies
                else:
                    cx = shooter.x + shooter.width // 2
                    cy = shooter.y + shooter.height
                    self.enemy_bullets.append(Bullet(cx, cy, +1))

        # enemy bullet
        for bullet in self.enemy_bullets[:]:
            bullet.update()

            bullet_rect = pygame.Rect(
                bullet.x - bullet.radius,
                bullet.y - bullet.radius,
                bullet.radius * 2,
                bullet.radius * 2
            )

            #hit player
            if self.player_respawn_time == 0 and bullet_rect.colliderect(self.player.get_rect()):
                self.enemy_bullets.remove(bullet)
                self.lives -= 1
                self.player_respawn_time = 120
                self.player.x = self.width // 2
                continue

            #hit barrier
            for barrier in self.barriers:
                if barrier.health > 0 and bullet_rect.colliderect(barrier.rect):
                    barrier.take_damage()
                    self.enemy_bullets.remove(bullet)
                    break

        self.enemy_bullets = [b for b in self.enemy_bullets if b.y < self.height]

        # player respawn timer
        if self.player_respawn_time > 0:
            self.player_respawn_time -= 1


       #wave clear check
        if len(self.enemies) == 0:
            self.wave += 1
            self.score += 500
            self.enemy_direction = 1
            self.enemy_speed = 1 + (self.wave * 0.2)
            self.create_enemy_grid()  # spawn next wave
            return  

    # draw loop
    def draw(self):
        self.window.fill(self.bg)
        #title screen
        if self.show_title_screen:
            font_big = pygame.font.SysFont(None, 70)
            font_small = pygame.font.SysFont(None, 40)

            title_text = font_big.render("SPACE INVADERS", True, (0, 255, 0))
            start_text = font_small.render("Press SPACE to Start", True, (255, 255, 255))
            control_text = font_small.render("Controls: Arrow Keys to Move, SPACE to Shoot", True, (200, 200, 200))

            #center everything
            self.window.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 180))
            self.window.blit(start_text, (self.width // 2 - start_text.get_width() // 2, 280))
            self.window.blit(control_text, (self.width // 2 - control_text.get_width() // 2, 350))

            return

        #game screen over
        if self.game_over:
            font_big = pygame.font.SysFont(None, 60)
            font_small = pygame.font.SysFont(None, 40)

            game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
            score_text = font_small.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = font_small.render("Press SPACE to Restart", True, (255, 255, 255))
            highscore_text = font_small.render(f"High Score: {self.high_score}", True, (255, 255, 255))
            self.window.blit(highscore_text, (self.width // 2 - highscore_text.get_width() // 2, 340))


            self.window.blit(game_over_text, (
                self.width // 2 - game_over_text.get_width() // 2, 200
            ))
            self.window.blit(score_text, (
                self.width // 2 - score_text.get_width() // 2, 300
            ))
            self.window.blit(restart_text, (
                self.width // 2 - restart_text.get_width() // 2, 380
            ))
            return  #stop drawing game


        font = pygame.font.SysFont(None, 30)

        #lives + score + wave
        self.window.blit(font.render(f"Lives: {self.lives}", True, (255, 255, 255)), (10, 10))
        self.window.blit(font.render(f"Score: {self.score}", True, (255, 255, 255)), (10, 40))
        self.window.blit(font.render(f"Wave: {self.wave}", True, (255, 255, 255)), (10, 70))
        self.window.blit(font.render(f"High Score: {self.high_score}", True, (255, 255, 255)), (10, 100))

        #draw barriers
        for barrier in self.barriers:
            barrier.draw(self.window)

        #draw player
        self.player.draw(self.window)

        #draw enemies
        for enemy in self.enemies:
            enemy.draw(self.window)

        #draw bullets
        for bullet in self.bullets:
            bullet.draw(self.window)
        for bullet in self.enemy_bullets:
            bullet.draw(self.window)

    # restart function
    def restart_game(self):

        self.player = Player(x=self.width // 2, y=self.height - 60)
        self.bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.player_respawn_time = 0

        self.enemy_speed = 1
        self.enemy_direction = 1

        self.create_enemy_grid()
        self.create_barriers()

        self.game_over = False
        self.show_title_screen =True
