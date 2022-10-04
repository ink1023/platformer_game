import pygame
from constant import *
from level import Level

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.run()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.level.handle_event(event)

            self.level.run()

            self.clock.tick(FPS)
            pygame.display.update()



if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()