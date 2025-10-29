import pygame
import threading
import random
import time

# ================== INICIALIZACIÓN ==================
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Juego con Hilos - Enemigos con Semáforo")

# Colores básicos
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Fuente
font = pygame.font.SysFont("Arial", 24)

# ================== IMÁGENES ==================
fondo = pygame.image.load("Fondo.jpg").convert()
fondo = pygame.transform.scale(fondo, (600, 400))

player_img = pygame.image.load("Pacman.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))

corazon = pygame.image.load("Corazon.png").convert_alpha()
corazon = pygame.transform.scale(corazon, (30, 30))

enemigo_imgs = [
    pygame.transform.scale(pygame.image.load("Fantasma.png").convert_alpha(), (40, 40)),
    pygame.transform.scale(pygame.image.load("Fantasma2.png").convert_alpha(), (40, 40))
]

# ================== VARIABLES ==================
player = pygame.Rect(300, 340, 50, 50)
enemigos = []
mutex = threading.Lock()

# 🔴 Semáforo: máximo 3 enemigos activos al mismo tiempo
semaforo_enemigos = threading.Semaphore(3)

vidas = 3
inicio_tiempo = time.time()

# ================== FUNCIONES ==================
def crear_enemigos():
    """Crea enemigos nuevos en posiciones aleatorias controlados por el semáforo."""
    while True:
        # Espera un segundo antes de intentar crear uno nuevo
        time.sleep(1)
        # Espera hasta que haya espacio disponible (permiso del semáforo)
        semaforo_enemigos.acquire()
        with mutex:
            img = random.choice(enemigo_imgs)
            rect = pygame.Rect(random.randint(0, 560), 0, 40, 40)
            enemigos.append({"rect": rect, "img": img})

def mover_enemigos():
    """Mueve los enemigos hacia abajo y elimina los que salen de la pantalla."""
    with mutex:
        for e in enemigos[:]:
            e["rect"].move_ip(0, 5)
            if e["rect"].y >= 400:
                enemigos.remove(e)
                # Libera un espacio en el semáforo
                semaforo_enemigos.release()

def detectar_colisiones():
    """Detecta colisiones y resta vidas."""
    global vidas
    with mutex:
        for e in enemigos[:]:
            if player.colliderect(e["rect"]):
                enemigos.remove(e)
                vidas -= 1
                # Libera un espacio del semáforo al eliminar enemigo
                semaforo_enemigos.release()

def dibujar_corazones(x, y):
    """Dibuja los corazones en pantalla según las vidas."""
    for i in range(vidas):
        screen.blit(corazon, (x + i * 35, y))

def dibujar_texto(texto, x, y, color=BLACK):
    render = font.render(texto, True, color)
    screen.blit(render, (x, y))

# ================== HILOS ==================
threading.Thread(target=crear_enemigos, daemon=True).start()

# ================== LOOP PRINCIPAL ==================
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento del jugador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.move_ip(-5, 0)
    if keys[pygame.K_RIGHT] and player.right < 600:
        player.move_ip(5, 0)

    mover_enemigos()
    detectar_colisiones()

    # Dibujar fondo
    screen.blit(fondo, (0, 0))

    # Dibujar jugador
    screen.blit(player_img, player)

    # Dibujar enemigos
    with mutex:
        for e in enemigos:
            screen.blit(e["img"], e["rect"])

    # Dibujar corazones y tiempo
    dibujar_corazones(10, 10)
    tiempo = int(time.time() - inicio_tiempo)
    dibujar_texto(f"Tiempo: {tiempo}s", 480, 10)

    pygame.display.flip()
    clock.tick(30)

    if vidas <= 0:
        running = False

# ================== GAME OVER ==================
screen.fill(WHITE)
dibujar_texto("GAME OVER", 240, 180, RED)
dibujar_texto(f"Tiempo sobrevivido: {tiempo}s", 200, 220)
pygame.display.flip()
time.sleep(3)
pygame.quit()
