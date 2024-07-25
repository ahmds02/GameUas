import pygame
import random

# Inisialisasi Pygame
pygame.init()

# Ukuran layar
screen_width = 1920
screen_height = 1080

# Membuat layar full screen
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders")

# Warna
black = (0, 0, 0)
white = (255, 255, 255)

#size
PLAYER_SIZE = (128, 128)
ENEMY_SIZE = (132, 132)
BULLET = (12, 12)

# Load images
player_img = pygame.transform.scale(pygame.image.load('Assets/Image/player.png'), PLAYER_SIZE)
enemy_img = pygame.transform.scale(pygame.image.load('Assets/Image/enemy.png'), ENEMY_SIZE)
enemy_fast_img = pygame.transform.scale(pygame.image.load('Assets/Image/enemy_fast.png'), ENEMY_SIZE)
enemy_strong_img = pygame.transform.scale(pygame.image.load('Assets/Image/enemy_strong.png'), ENEMY_SIZE)
bullet_img = pygame.transform.scale(pygame.image.load('Assets/Image/bullet.png'), BULLET)
bullet_enemy_img = pygame.transform.scale(pygame.image.load('Assets/Image/bullet_enemy.png'), BULLET)
explosion_img = pygame.image.load('Assets/Image/explosion.png')

# Load and play background music
pygame.mixer.music.load('Assets/Sound/background.wav')
pygame.mixer.music.play(-1)

# Load sound effects
bullet_sound = pygame.mixer.Sound('Assets/Sound/bullet.wav')
explosion_sound = pygame.mixer.Sound('Assets/Sound/explosion.wav')

# Player
player_rect = player_img.get_rect()
player_rect.center = (screen_width // 2, screen_height - 70)

# Menggambar bintang-bintang
def draw_stars(screen):
    for _ in range(10):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        pygame.draw.circle(screen, white, (x, y), 2)


# Enemies
enemies = []
enemy_count = 6
for _ in range(enemy_count):
    enemy_rect = enemy_img.get_rect()
    enemy_rect.x = random.randint(0, screen_width - enemy_rect.width)
    enemy_rect.y = random.randint(-100, -40)
    enemies.append(enemy_rect)

# Fast Enemies
fast_enemies = []
fast_enemy_count = 3
for _ in range(fast_enemy_count):
    enemy_fast_rect = enemy_fast_img.get_rect()
    enemy_fast_rect.x = random.randint(0, screen_width - enemy_fast_rect.width)
    enemy_fast_rect.y = random.randint(-100, -40)
    fast_enemies.append(enemy_fast_rect)

# Strong Enemies
strong_enemies = []
strong_enemy_count = 3
for _ in range(strong_enemy_count):
    enemy_strong_rect = enemy_strong_img.get_rect()
    enemy_strong_rect.x = random.randint(0, screen_width - enemy_strong_rect.width)
    enemy_strong_rect.y = random.randint(-100, -40)
    strong_enemies.append(enemy_strong_rect)


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.y += 5
        if self.rect.top > screen_height:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.images = []
        for i in range(9):  # Assuming there are 9 frames in the explosion animation
            EXPLOSION = (128, 128)
            image = pygame.transform.scale(pygame.image.load(f'Assets/Image/explosion.png'), EXPLOSION)  # Load each frame
            self.images.append(image)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 8  # ms between frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame]


# Groups for bullets
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Timing for enemy bullets
enemy_shoot_time = pygame.time.get_ticks()

# Hit counts for enemies
enemy_hits = [0] * enemy_count
fast_enemy_hits = [0] * fast_enemy_count
strong_enemy_hits = [0] * strong_enemy_count
player_hits = 0
player_lives = 3

# score
score = 0

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(player_rect.centerx, player_rect.top, bullet_img)
                player_bullets.add(bullet)
                bullet_sound.play()

    # Mengisi layar dengan warna hitam
    screen.fill(black)
    
    # Menggambar bintang-bintang
    draw_stars(screen)

    # Player mengikuti mouse
    player_rect.centerx = pygame.mouse.get_pos()[0]
    screen.blit(player_img, player_rect)

    # Menggambar enemies
    for enemy_rect in enemies:
        enemy_rect.y += 1
        if enemy_rect.y > screen_height:
            enemy_rect.y = random.randint(-100, -40)
            enemy_rect.x = random.randint(0, screen_width - enemy_rect.width)
        screen.blit(enemy_img, enemy_rect)
        if pygame.time.get_ticks() - enemy_shoot_time > 500:
            bullet = EnemyBullet(enemy_rect.centerx, enemy_rect.bottom, bullet_enemy_img)
            enemy_bullets.add(bullet)
            enemy_shoot_time = pygame.time.get_ticks()

    # Menggambar fast enemies
    for fast_enemy_rect in fast_enemies:
        fast_enemy_rect.y += 2
        if fast_enemy_rect.y > screen_height:
            fast_enemy_rect.y = random.randint(-100, -40)
            fast_enemy_rect.x = random.randint(0, screen_width - fast_enemy_rect.width)
        screen.blit(enemy_fast_img, fast_enemy_rect)
        if pygame.time.get_ticks() - enemy_shoot_time > 500:
            bullet = EnemyBullet(fast_enemy_rect.centerx, fast_enemy_rect.bottom, bullet_enemy_img)
            enemy_bullets.add(bullet)
            enemy_shoot_time = pygame.time.get_ticks()

    # Menggambar strong enemy secara diagonal
    for strong_enemy_rect in strong_enemies:
        strong_enemy_rect.x += 1
        strong_enemy_rect.y += 1
        if strong_enemy_rect.y > screen_height or strong_enemy_rect.x > screen_width:
            strong_enemy_rect.x = random.randint(0, screen_width - strong_enemy_rect.width)
            strong_enemy_rect.y = random.randint(-100, -40)
        screen.blit(enemy_strong_img, strong_enemy_rect)
        if pygame.time.get_ticks() - enemy_shoot_time > 500:
            bullet = EnemyBullet(strong_enemy_rect.centerx, strong_enemy_rect.bottom, bullet_enemy_img)
            enemy_bullets.add(bullet)
            enemy_shoot_time = pygame.time.get_ticks()

    # Update
    player_bullets.update()
    enemy_bullets.update()
    explosions.update()

    # Check for collisions
    for bullet in player_bullets:
        for i, enemy_rect in enumerate(enemies):
            if bullet.rect.colliderect(enemy_rect):
                enemy_hits[i] += 1
                bullet.kill()
                if enemy_hits[i] >= 3:
                    enemy_hits[i] = 0
                    explosion = Explosion(enemy_rect.centerx, enemy_rect.centery, explosion_img)
                    explosions.add(explosion)
                    explosion_sound.play()
                    enemy_rect.y = random.randint(-100, -40)
                    enemy_rect.x = random.randint(0, screen_width - enemy_rect.width)
                    score += 2
        
        for i, fast_enemy_rect in enumerate(fast_enemies):
            if bullet.rect.colliderect(fast_enemy_rect):
                fast_enemy_hits[i] += 1
                bullet.kill()
                if fast_enemy_hits[i] >= 1:
                    fast_enemy_hits[i] = 0
                    explosion = Explosion(fast_enemy_rect.centerx, fast_enemy_rect.centery, explosion_img)
                    explosions.add(explosion)
                    explosion_sound.play()
                    fast_enemy_rect.y = random.randint(-100, -40)
                    fast_enemy_rect.x = random.randint(0, screen_width - fast_enemy_rect.width)
                    score += 1

        for i, strong_enemy_rect in enumerate(strong_enemies):
            if bullet.rect.colliderect(strong_enemy_rect):
                strong_enemy_hits[i] += 1
                bullet.kill()
                if strong_enemy_hits[i] >= 6:
                    strong_enemy_hits[i] = 0
                    explosion = Explosion(strong_enemy_rect.centerx, strong_enemy_rect.centery, explosion_img)
                    explosions.add(explosion)
                    explosion_sound.play()
                    strong_enemy_rect.x = random.randint(0, screen_width - strong_enemy_rect.width)
                    strong_enemy_rect.y = random.randint(-100, -40) 
                    score += 3

    for bullet in enemy_bullets:
        if bullet.rect.colliderect(player_rect):
            player_hits += 1
            bullet.kill()
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                explosion = Explosion(player_rect.centerx, player_rect.centery, explosion_img)
                explosions.add(explosion)
                if player_lives <= 0:
                    running = False

    # Check for player collisions with enemies
    for i, enemy_rect in enumerate(enemies):
        if player_rect.colliderect(enemy_rect):
            player_hits += 1
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                if player_lives <= 0:
                    running = False
            explosions.add(Explosion(enemy_rect.centerx, enemy_rect.centery, enemy_img))
            explosion_sound.play()
            enemy_rect.y = random.randint(-100, -40)
            enemy_rect.x = random.randint(0, screen_width - enemy_rect.width)

    for i, fast_enemy_rect in enumerate(fast_enemies):
        if player_rect.colliderect(fast_enemy_rect):
            player_hits += 1
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                if player_lives <= 0:
                    running = False
            explosions.add(Explosion(fast_enemy_rect.centerx, fast_enemy_rect.centery, explosion_img))
            explosion_sound.play()
            fast_enemy_rect.y = random.randint(-100, -40)
            fast_enemy_rect.x = random.randint(0, screen_width - fast_enemy_rect.width)

    for i, strong_enemy_rect in enumerate(strong_enemies):
        if player_rect.colliderect(strong_enemy_rect):
            player_hits += 1
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                if player_lives <= 0:
                    running = False
            explosions.add(Explosion(strong_enemy_rect.centerx, strong_enemy_rect.centery, explosion_img))
            explosion_sound.play()
            strong_enemy_rect.x = random.randint(0, screen_width - strong_enemy_rect.width)
            strong_enemy_rect.y = random.randint(-100, -40)

    # Draw
    player_bullets.draw(screen)
    enemy_bullets.draw(screen)
    explosions.draw(screen)

     # Display player lives
    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f"Lives: {player_lives}", True, white)
    screen.blit(lives_text, (screen_width - 100, 10))

    # Update display
    pygame.display.flip()

pygame.quit()