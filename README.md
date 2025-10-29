🎯 Objetivo del laboratorio

El objetivo de este laboratorio fue implementar un videojuego en Pygame controlado por múltiples hilos y sincronizado mediante semáforos, con el propósito de comprender el funcionamiento de la concurrencia, los mecanismos de exclusión mutua (Lock) y la coordinación de acceso a recursos compartidos (Semaphore).

El juego debía mostrar un personaje principal controlado por el jugador, enemigos que aparecen de forma aleatoria y limitada (según el semáforo), y un sistema de vidas representado por corazones en pantalla.
La meta fue mantener la integridad del programa y evitar condiciones de carrera mientras los hilos crean, mueven y eliminan enemigos.

⚙️ Descripción general del programa

El sistema se compone de dos grandes procesos concurrentes:

Hilo principal:
Se encarga del bucle de juego, lectura del teclado, detección de colisiones, dibujo del escenario y control de las vidas del jugador.

Hilo secundario (daemon):
Genera enemigos de forma constante, regulados por un semáforo que limita la cantidad máxima de enemigos en pantalla.

Ambos procesos comparten variables (como la lista enemigos), protegidas por un candado (Lock) que garantiza exclusión mutua, impidiendo accesos simultáneos peligrosos.
