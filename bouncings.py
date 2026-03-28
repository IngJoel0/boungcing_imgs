import os
import random

import pygame

IMG_DIR = os.path.join(os.path.dirname(__file__), 'imgs')
FPS = 60
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tga'}
DEFAULT_WINDOW_SIZE = (1280, 720)
MIN_WINDOW_SIZE = (640, 480)
WINDOW_MARGIN = 0.9
SPRITE_SIZE_RATIO = 0.1
MIN_SPRITE_SIZE = 48
MAX_SPRITE_SIZE = 140
MIN_SPEED = 90
MAX_SPEED = 170


class BouncingImage:
    def __init__(self, image, screen_rect, sprite_size):
        self.image = pygame.transform.smoothscale(image, sprite_size)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, max(0, screen_rect.width - self.rect.width))
        self.rect.y = random.randint(0, max(0, screen_rect.height - self.rect.height))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.vx = random.choice([-1, 1]) * random.uniform(MIN_SPEED, MAX_SPEED)
        self.vy = random.choice([-1, 1]) * random.uniform(MIN_SPEED, MAX_SPEED)

    def update(self, screen_rect, dt):
        self.pos_x += self.vx * dt
        self.pos_y += self.vy * dt
        self.rect.x = round(self.pos_x)
        self.rect.y = round(self.pos_y)

        if self.rect.left <= screen_rect.left:
            self.rect.left = screen_rect.left
            self.pos_x = float(self.rect.x)
            self.vx = abs(self.vx)
        elif self.rect.right >= screen_rect.right:
            self.rect.right = screen_rect.right
            self.pos_x = float(self.rect.x)
            self.vx = -abs(self.vx)

        if self.rect.top <= screen_rect.top:
            self.rect.top = screen_rect.top
            self.pos_y = float(self.rect.y)
            self.vy = abs(self.vy)
        elif self.rect.bottom >= screen_rect.bottom:
            self.rect.bottom = screen_rect.bottom
            self.pos_y = float(self.rect.y)
            self.vy = -abs(self.vy)


def cargar_imagenes():
    if not os.path.isdir(IMG_DIR):
        raise FileNotFoundError(f"No se encontro la carpeta imgs en: {IMG_DIR}")

    rutas = [
        os.path.join(IMG_DIR, n)
        for n in os.listdir(IMG_DIR)
        if os.path.isfile(os.path.join(IMG_DIR, n))
        and os.path.splitext(n)[1].lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]

    images = []
    for ruta in rutas:
        try:
            img = pygame.image.load(ruta).convert_alpha()
            if img.get_width() == 0 or img.get_height() == 0:
                continue
            images.append(img)
        except pygame.error as exc:
            print(f"No se pudo cargar {ruta}: {exc}")

    if not images:
        raise RuntimeError("No se cargo ninguna imagen valida desde la carpeta imgs.")

    return images


def obtener_tamano_ventana():
    info = pygame.display.Info()
    desktop_w = info.current_w or DEFAULT_WINDOW_SIZE[0]
    desktop_h = info.current_h or DEFAULT_WINDOW_SIZE[1]
    width = max(MIN_WINDOW_SIZE[0], int(desktop_w * WINDOW_MARGIN))
    height = max(MIN_WINDOW_SIZE[1], int(desktop_h * WINDOW_MARGIN))
    return min(width, desktop_w), min(height, desktop_h)


def calcular_tamano_sprite(screen_rect):
    side = int(min(screen_rect.width, screen_rect.height) * SPRITE_SIZE_RATIO)
    side = max(MIN_SPRITE_SIZE, min(side, MAX_SPRITE_SIZE))
    return side, side


def crear_pantalla(size):
    try:
        return pygame.display.set_mode(size, pygame.FULLSCREEN)
    except pygame.error:
        return pygame.display.set_mode(DEFAULT_WINDOW_SIZE)


def main():
    pygame.init()
    pygame.display.set_caption('DVD Splash Screensaver')

    screen = crear_pantalla(obtener_tamano_ventana())
    screen_rect = screen.get_rect()

    clock = pygame.time.Clock()
    images = cargar_imagenes()
    sprite_size = calcular_tamano_sprite(screen_rect)
    bouncers = [BouncingImage(img, screen_rect, sprite_size) for img in images]

    font = pygame.font.SysFont(None, 42)
    msg = "Presiona ESC para salir"

    message_interval = 10.0
    message_duration = 4.0
    fade_time = 1.0

    message_timer = 0.0
    cycle_timer = 0.0
    show_message = False

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        for bouncer in bouncers:
            bouncer.update(screen_rect, dt)

        cycle_timer += dt
        if not show_message and cycle_timer >= message_interval:
            show_message = True
            message_timer = 0.0
            cycle_timer = 0.0

        if show_message:
            message_timer += dt
            if message_timer >= message_duration:
                show_message = False
                message_timer = 0.0

        screen.fill((0, 0, 0))

        for bouncer in bouncers:
            screen.blit(bouncer.image, bouncer.rect)

        if show_message:
            if message_timer < fade_time:
                alpha = int(255 * (message_timer / fade_time))
            elif message_timer > message_duration - fade_time:
                alpha = int(255 * (1 - (message_timer - (message_duration - fade_time)) / fade_time))
            else:
                alpha = 255

            alpha = max(0, min(alpha, 255))
            text_surface = font.render(msg, True, (0, 0, 0))
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(screen_rect.centerx, screen_rect.bottom - 40))

            border_surface = font.render(msg, True, (255, 255, 255))
            border_surface.set_alpha(max(0, min(120, alpha)))
            border_rect = border_surface.get_rect(center=text_rect.center)

            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                offset_rect = border_rect.copy()
                offset_rect.move_ip(dx, dy)
                screen.blit(border_surface, offset_rect)

            screen.blit(text_surface, text_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
