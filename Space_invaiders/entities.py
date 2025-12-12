import pygame

PLAYER_SPEED = 5
BULLET_SPEED = 7


#player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 25
        self.color = (0, 255, 0)

        self.cooldown = 0
        self.cooldown_time = 10  #frames between shots

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, keys, bullets):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < 760:
            self.x += PLAYER_SPEED

        #shooting
        if keys[pygame.K_SPACE] and self.cooldown == 0:
            bullets.append(Bullet(self.x + self.width // 2, self.y, -1))
            self.cooldown = self.cooldown_time

        #cooldown counter
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

#bullet class
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.radius = 4
        self.color = (255, 255, 0)
        self.direction = direction 

    def update(self):
        self.y += self.direction * BULLET_SPEED

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

#enemy class
class Enemy:
    def __init__(self, x, y, width=35, height=25, color=(255, 0, 0), health=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.health = health

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def take_damage(self):
        """Returns True if enemy dies, False if still alive."""
        self.health -= 1
        return self.health <= 0

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

#special enemy list
#tank enemy (large, 3 HP)
class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, width=60, height=40, color=(200, 50, 50), health=3)


#double-shot enemy (shoots two bullets)
class DoubleShotEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, width=45, height=30, color=(50, 200, 50), health=1)

    def shoot(self):
        """Returns two bullet spawn positions."""
        return [
            (self.x + 5, self.y + self.height),
            (self.x + self.width - 5, self.y + self.height)
        ]


#rapid fire enemy (shoots twice quickly)
class RapidFireEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, width=35, height=25, color=(50, 50, 200), health=1)
        self.fire_cooldown = 0

#barrier class
class Barrier:
    def __init__(self, x, y):
        self.width = 60
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 8 

    def take_damage(self):
        self.health -= 1
        shrink_amount = 5
        self.rect.width = max(0, self.rect.width - shrink_amount)
        self.rect.height = max(0, self.rect.height - shrink_amount)

    def draw(self, window):
        if self.health > 0:
            pygame.draw.rect(window, (0, 255, 0), self.rect)
