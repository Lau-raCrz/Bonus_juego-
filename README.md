# Ejercicio de bonus

##  Objetivo 

El objetivo de este laboratorio fue implementar un videojuego en Pygame controlado por múltiples hilos y sincronizado mediante semáforos, con el propósito de comprender el funcionamiento de la concurrencia, los mecanismos de exclusión mutua (Lock) y la coordinación de acceso a recursos compartidos (Semaphore).

El juego debía mostrar un personaje principal controlado por el jugador, enemigos que aparecen de forma aleatoria y limitada (según el semáforo), y un sistema de vidas representado por corazones en pantalla.
La meta fue mantener la integridad del programa y evitar condiciones de carrera mientras los hilos crean, mueven y eliminan enemigos.

##  Descripción general del programa

El sistema se compone de dos grandes procesos concurrentes:

Hilo principal:
Se encarga del bucle de juego, lectura del teclado, detección de colisiones, dibujo del escenario y control de las vidas del jugador.

Hilo secundario (daemon):
Genera enemigos de forma constante, regulados por un semáforo que limita la cantidad máxima de enemigos en pantalla.

Ambos procesos comparten variables (como la lista enemigos), protegidas por un candado (Lock) que garantiza exclusión mutua, impidiendo accesos simultáneos peligrosos.


## Explicacion de codigo

### Inicialización de Pygame

Lo primero que se hizo fue inicializar los módulos de Pygame y se crea la ventana principal de 600×400 píxeles.
También se definen los colores, la fuente y el título de la ventana.

```
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Juego")

```

### Carga de recursos gráficos
Se cargan las imágenes necesarias para el fondo, el jugador, los corazones (vidas) y los enemigos.
Cada imagen se convierte para optimizar su rendimiento gráfico (convert() y convert_alpha()).

```
fondo = pygame.image.load("Fondo.jpg").convert()
player_img = pygame.image.load("Pacman.png").convert_alpha()
corazon = pygame.image.load("Corazon.png").convert_alpha()
enemigo_imgs = [
    pygame.transform.scale(pygame.image.load("Fantasma.png").convert_alpha(), (40, 40)),
    pygame.transform.scale(pygame.image.load("Fantasma2.png").convert_alpha(), (40, 40))
]
```

### Variables globales

Se define el rectángulo físico del jugador. Los enemigos, lista compartida entre hilos que guarda las posiciones y sprites de los enemigos. Con el mutex ya que bloquea secciones críticas durante la modificación de enemigos.Con semaforo_enemigos limita el número de enemigos simultáneos a 3 máximo. Por ultimo, vidas y inicio_tiempo son las que controlan el marcador del juego.
```
player = pygame.Rect(300, 340, 50, 50)
enemigos = []
mutex = threading.Lock()
semaforo_enemigos = threading.Semaphore(3)
vidas = 3
inicio_tiempo = time.time()
```
### Hilo de creación de enemigos

Se ejecuta en un hilo independiente y cada segundo intenta crear un nuevo enemigo. Con el método acquire() bloquea la creación si ya existen 3 enemigos activos y cuando se libera un espacio (mediante release()), un nuevo enemigo podrá ser generado. El uso del mutex asegura que solo un hilo a la vez modifique la lista enemigos.


```
def crear_enemigos():
    while True:
        time.sleep(1)
        semaforo_enemigos.acquire()
        with mutex:
            img = random.choice(enemigo_imgs)
            rect = pygame.Rect(random.randint(0, 560), 0, 40, 40)
            enemigos.append({"rect": rect, "img": img})
```
### Movimiento de enemigos

Lo que se hace en esta parte es desplazar cada enemigo hacia abajo. Si un enemigo sale de la pantalla, se elimina de la lista y se libera un permiso del semáforo. Con enemigos[:] crea una copia temporal, permitiendo modificar la lista sin errores de iteración.

```
def mover_enemigos():
    with mutex:
        for e in enemigos[:]:
            e["rect"].move_ip(0, 5)
            if e["rect"].y >= 400:
                enemigos.remove(e)
                semaforo_enemigos.release()
```

### Detección de colisiones

En este punto se comprueba si el jugador colisiona con un enemigo. Si hay colisión se elimina el enemigo, se reduce una vida y se libera un permiso del semáforo, permitiendo que otro enemigo aparezca.
```
def detectar_colisiones():
    global vidas
    with mutex:
        for e in enemigos[:]:
            if player.colliderect(e["rect"]):
                enemigos.remove(e)
                vidas -= 1
                semaforo_enemigos.release()

```
### Interfaz y dibujo
Ambas funciones actualizan el HUD (interfaz del jugador), mostrando las vidas restantes y el tiempo de juego.

```
def dibujar_corazones(x, y):
    for i in range(vidas):
        screen.blit(corazon, (x + i * 35, y))

def dibujar_texto(texto, x, y, color=WHITE):
    render = font.render(texto, True, color)
    screen.blit(render, (x, y))
```
### Actualización de la pantalla
Refresca la pantalla con todo lo dibujado hasta ahora, Pygame primero dibuja todo en un “buffer” oculto, y este comando lo muestra al usuario (técnica de doble buffer). Con la funcion clock.tick(30)
Limita la velocidad del bucle a 30 fotogramas por segundo (FPS). Evitando que el juego corra a toda velocidad y consuma 100% del CPU.

```
pygame.display.flip()
clock.tick(30)
```


### Bucle principal del juego
Se inicia el hilo demonio que genera enemigos. En este punto se crea y pone en funcionamiento un nuevo hilo de ejecución en el programa, distinto del hilo principal donde corre el juego y se dibuja la pantalla. En Python, un hilo (thread) es una tarea que se ejecuta de forma paralela o concurrente a otras, compartiendo la misma memoria pero trabajando de manera independiente. En este caso, el hilo tiene como función ejecutar la rutina crear_enemigos, que se encarga de generar enemigos nuevos cada cierto tiempo sin interrumpir el flujo principal del juego. El parámetro target=crear_enemigos le indica a Python cuál función debe ejecutar dentro de ese hilo, mientras que el argumento daemon=True convierte ese hilo en un hilo demonio (daemon thread). Esto significa que el hilo no es esencial para mantener vivo el programa: cuando el hilo principal termina (por ejemplo, al cerrar la ventana del juego), todos los hilos demonio se cierran automáticamente sin necesidad de detenerlos manualmente. Finalmente, el método .start() es el que inicia realmente el hilo, haciendo que Python cree una nueva línea de ejecución que correrá crear_enemigos() de manera continua y paralela al bucle principal (while running:). Gracias a esta línea, el juego puede seguir procesando eventos, dibujando la pantalla y moviendo al jugador, mientras en segundo plano el hilo genera enemigos de forma independiente, manteniendo el juego fluido y evitando bloqueos o pausas.

```
threading.Thread(target=crear_enemigos, daemon=True).start()
```

### Cierre y pantalla final
Lo ultimo que se hace es que la pantalla se limpia en blanco. Se muestra un mensaje final y el tiempo total que el jugador sobrevivió y tambien se mantiene visible durante 3 segundos y luego el juego termina con pygame.quit().

```
screen.fill(WHITE)
dibujar_texto("GAME OVER", 240, 180, RED)
dibujar_texto(f"Tiempo sobrevivido: {tiempo}s", 200, 220)
pygame.display.flip()
time.sleep(3)
pygame.quit()
```
