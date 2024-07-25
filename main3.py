import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()

# Ukuran layar
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 832

# Membuat layar full screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders")

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Ukuran
PLAYER_SIZE = (128, 128)
ENEMY_SIZE = (132, 132)
BULLET_SIZE = (12, 12)
EXPLOSION_SIZE = (128, 128)

# Memuat gambar
def load_and_scale_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size)

player_img = load_and_scale_image('Assets/Image/player.png', PLAYER_SIZE)
enemy_img = load_and_scale_image('Assets/Image/enemy.png', ENEMY_SIZE)
enemy_fast_img = load_and_scale_image('Assets/Image/enemy_fast.png', ENEMY_SIZE)
enemy_strong_img = load_and_scale_image('Assets/Image/enemy_strong.png', ENEMY_SIZE)
bullet_img = load_and_scale_image('Assets/Image/bullet.png', BULLET_SIZE)
bullet_enemy_img = load_and_scale_image('Assets/Image/bullet_enemy.png', BULLET_SIZE)
explosion_img = pygame.image.load('Assets/Image/explosion.png')

# Memuat dan memutar musik latar belakang
pygame.mixer.music.load('Assets/Sound/background.wav')
pygame.mixer.music.play(-1)

# Memuat efek suara
bullet_sound = pygame.mixer.Sound('Assets/Sound/bullet.wav')
explosion_sound = pygame.mixer.Sound('Assets/Sound/explosion.wav')

# Inisialisasi pemain
player_rect = player_img.get_rect()
player_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)

# Menggambar bintang-bintang
def draw_stars(screen):
    for _ in range(10):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(screen, WHITE, (x, y), 2)

# Membuat kelompok musuh
def create_enemies(img, count):
    enemies = []
    for _ in range(count):
        enemy_rect = img.get_rect()
        enemy_rect.x = random.randint(0, SCREEN_WIDTH - enemy_rect.width)
        enemy_rect.y = random.randint(-100, -40)
        enemies.append(enemy_rect)
    return enemies

enemies = create_enemies(enemy_img, 6)
fast_enemies = create_enemies(enemy_fast_img, 3)
strong_enemies = create_enemies(enemy_strong_img, 3)

# Kelas Peluru
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
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Kelas Ledakan
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.images = [pygame.transform.scale(img, EXPLOSION_SIZE) for _ in range(9)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 8

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame]

# Grup peluru
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Waktu penembakan musuh
enemy_shoot_time = pygame.time.get_ticks()

# Hitungan hit musuh
enemy_hits = [0] * len(enemies)
fast_enemy_hits = [0] * len(fast_enemies)
strong_enemy_hits = [0] * len(strong_enemies)
player_hits = 0
player_lives = 3

# Skor
score = 0

# High score
high_score = 0

# kondisi
running = True

# Fungsi utama game
def main_game_loop():
    global enemy_shoot_time, player_hits, player_lives, score, running
    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.QUIT:
            #     running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player_rect.centerx, player_rect.top, bullet_img)
                    player_bullets.add(bullet)
                    bullet_sound.play()

        if player_lives <= 0:
            running = False
            main_menu()

        # Mengisi layar dengan warna hitam
        screen.fill(BLACK)
        
        # Menggambar bintang-bintang
        draw_stars(screen)

        # Player mengikuti mouse
        player_rect.centerx = pygame.mouse.get_pos()[0]
        screen.blit(player_img, player_rect)

        # Menggambar musuh
        draw_enemies()

        # Update
        player_bullets.update()
        enemy_bullets.update()
        explosions.update()

        # Draw
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)
        explosions.draw(screen)

        # Check for collisions
        handle_collisions()

        #display scores
        display_score()

        # Display player lives
        display_lives()

        # Update display
        pygame.display.flip()

        pygame.time.delay(5)

    main_menu()

# Menggambar musuh
def draw_enemies():
    global enemy_shoot_time
    for enemy_rect in enemies:
        enemy_rect.y += 1
        if enemy_rect.y > SCREEN_HEIGHT:
            enemy_rect.y = random.randint(-100, -40)
            enemy_rect.x = random.randint(0, SCREEN_WIDTH - enemy_rect.width)
        screen.blit(enemy_img, enemy_rect)
        if pygame.time.get_ticks() - enemy_shoot_time > 500:
            bullet = EnemyBullet(enemy_rect.centerx, enemy_rect.bottom, bullet_enemy_img)
            enemy_bullets.add(bullet)
            enemy_shoot_time = pygame.time.get_ticks()

    # Menggambar fast enemies
    for fast_enemy_rect in fast_enemies:
        fast_enemy_rect.y += 2
        if fast_enemy_rect.y > SCREEN_HEIGHT:
            fast_enemy_rect.y = random.randint(-100, -40)
            fast_enemy_rect.x = random.randint(0, SCREEN_WIDTH - fast_enemy_rect.width)
        screen.blit(enemy_fast_img, fast_enemy_rect)
        if pygame.time.get_ticks() - enemy_shoot_time > 500:
            bullet = EnemyBullet(fast_enemy_rect.centerx, fast_enemy_rect.bottom, bullet_enemy_img)
            enemy_bullets.add(bullet)
            enemy_shoot_time = pygame.time.get_ticks()

    # Menggambar strong enemy secara diagonal
    for strong_enemy_rect in strong_enemies:
        strong_enemy_rect.x += 1
        strong_enemy_rect.y += 1
        if strong_enemy_rect.y > SCREEN_HEIGHT or strong_enemy_rect.x > SCREEN_WIDTH:
            strong_enemy_rect.x = random.randint(0, SCREEN_WIDTH - strong_enemy_rect.width)
            strong_enemy_rect.y = random.randint(-100, -40)
        screen.blit(enemy_strong_img, strong_enemy_rect)
        if pygame.time.get_ticks() - enemy_shoot_time > 500:
            bullet = EnemyBullet(strong_enemy_rect.centerx, strong_enemy_rect.bottom, bullet_enemy_img)
            enemy_bullets.add(bullet)
            enemy_shoot_time = pygame.time.get_ticks()

# Menangani tabrakan
def handle_collisions():
    global player_hits, player_lives, score, running
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
                    enemy_rect.x = random.randint(0, SCREEN_WIDTH - enemy_rect.width)
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
                    fast_enemy_rect.x = random.randint(0, SCREEN_WIDTH - fast_enemy_rect.width)
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
                    strong_enemy_rect.x = random.randint(0, SCREEN_WIDTH - strong_enemy_rect.width)
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
                    main_menu()

    # Check for player collisions with enemies
    for i, enemy_rect in enumerate(enemies):
        if player_rect.colliderect(enemy_rect):
            player_hits += 1
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                if player_lives <= 0:
                    running = False
                    main_menu()
            explosions.add(Explosion(enemy_rect.centerx, enemy_rect.centery, enemy_img))
            explosion_sound.play()
            enemy_rect.y = random.randint(-100, -40)
            enemy_rect.x = random.randint(0, SCREEN_WIDTH - enemy_rect.width)

    for i, fast_enemy_rect in enumerate(fast_enemies):
        if player_rect.colliderect(fast_enemy_rect):
            player_hits += 1
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                if player_lives <= 0:
                    running = False
                    main_menu()
            explosions.add(Explosion(fast_enemy_rect.centerx, fast_enemy_rect.centery, explosion_img))
            explosion_sound.play()
            fast_enemy_rect.y = random.randint(-100, -40)
            fast_enemy_rect.x = random.randint(0, SCREEN_WIDTH - fast_enemy_rect.width)

    for i, strong_enemy_rect in enumerate(strong_enemies):
        if player_rect.colliderect(strong_enemy_rect):
            player_hits += 1
            if player_hits >= 1:
                player_lives -= 1
                player_hits = 0
                if player_lives <= 0:
                    running = False
                    main_menu()
            explosions.add(Explosion(strong_enemy_rect.centerx, strong_enemy_rect.centery, explosion_img))
            explosion_sound.play()
            strong_enemy_rect.x = random.randint(0, SCREEN_WIDTH - strong_enemy_rect.width)
            strong_enemy_rect.y = random.randint(-100, -40)

# High Score
def display_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# Menampilkan jumlah nyawa pemain
def display_lives():
    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))

# Display high score
def show_high_score():  
    # Example high score

    font = pygame.font.SysFont(None, 72)
    score_text = font.render(f"High Score: {score}", True, WHITE)
    screen.fill(BLACK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - score_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(1000)

# Main menu
def main_menu():
    global running

    running = True

    menu_font = pygame.font.SysFont(None, 72)
    play_text = menu_font.render("Play (1)", True, WHITE)
    high_score_text = menu_font.render("High Score (2)", True, WHITE)
    quit_text = menu_font.render("Quit (3)", True, WHITE)
    
    while running:
        screen.fill(BLACK)
        
        screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2 - play_text.get_height() // 2 - 100))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - high_score_text.get_height() // 2))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 - quit_text.get_height() // 2 + 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_game_loop()
                elif event.key == pygame.K_2:
                    show_high_score()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

# Main function
def main():
    main_menu()

if __name__ == "__main__":
    main()