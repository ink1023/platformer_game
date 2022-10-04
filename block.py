import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, position: pygame.math.Vector2, groups=None):
        super().__init__(groups)
        self.type = "platform"
        # self.image = pygame.image.load("assets/image/platform.png").convert_alpha()
        self.image = pygame.surface.Surface((32, 32))
        self.image.fill((200, 200, 200))
        self.position = pygame.math.Vector2(position)
        self.rect = self.image.get_rect(topleft=self.position)
        self.collide_rect = self.rect

        pygame.draw.lines(self.image, (255, 0, 0), True, [(0, 0), (32, 0), (32, 32), (0, 32)], 2)



    def update(self, *args):
        self.rect.topleft = self.position
