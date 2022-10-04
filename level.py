import pygame
from constant import *
from camera import CameraGroup
from block import Platform
from player import Player

class Level:
    def __init__(self):

        # level setup
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_group = CameraGroup()
        self.collide_group = pygame.sprite.Group()
        self.active_group = pygame.sprite.Group()

        self.setup_level()
    
    def setup_level(self):
        self.background = pygame.image.load("assets/image/background.jpg").convert_alpha()
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))

        for y, line in enumerate(MAP):
            for x, char in enumerate(line):
                if char == "X":
                    Platform(
                        position=pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE),
                        groups=[self.visible_group, self.collide_group]
                    )
                elif char == "P":
                    self.player = Player(
                        player_id="player_02",
                        position=pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE),
                        groups=[self.visible_group, self.active_group],
                        collide_group=self.collide_group
                    )
    
    def handle_event(self, event):
        self.player.handle_event(event)
    
    def draw_player_rect(self):
        offset_rect = pygame.Rect(
            self.player.rect.left - self.visible_group.offset.x,
            self.player.rect.top - self.visible_group.offset.y,
            self.player.rect.width,
            self.player.rect.height
        )
        pygame.draw.rect(self.display_surface, (0, 0, 255), offset_rect, 2)
        offset_rect = pygame.Rect(
            self.player.collide_rect.left - self.visible_group.offset.x,
            self.player.collide_rect.top - self.visible_group.offset.y,
            self.player.collide_rect.width,
            self.player.collide_rect.height
        )
        pygame.draw.rect(self.display_surface, (0, 255, 0), offset_rect, 2)
        offset_rect = pygame.Rect(
            self.player.attack_rect.left - self.visible_group.offset.x,
            self.player.attack_rect.top - self.visible_group.offset.y,
            self.player.attack_rect.width,
            self.player.attack_rect.height
        )
        pygame.draw.rect(self.display_surface, (255, 0, 0), offset_rect, 2)

        pygame.draw.circle(self.display_surface, (0, 0, 255), self.player.position-self.visible_group.offset, 5)

    def run(self):
        self.display_surface.blit(self.background, (0, 0))
        self.active_group.update()
        self.visible_group.draw(self.player)

        self.draw_player_rect()



        # # 画出player的碰撞盒
        # pygame.draw.rect(self.screen, (0, 0, 255), self.player.rect, 2)
        # pygame.draw.rect(self.screen, (0, 255, 0), self.player.collide_rect, 2)
        # pygame.draw.rect(self.screen, (255, 0, 0), self.player.attack_rect, 2)
        # # 画出player的中心点
        # pygame.draw.circle(self.screen, (0, 0, 255), self.player.position, 5)
