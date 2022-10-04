import pygame
from constant import *

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2(0, 0)

        cam_left = CAMERA_EDGE_LEFT
        cam_top = CAMERA_EDGE_RIGHT
        cam_width = WINDOW_WIDTH - (cam_left + CAMERA_EDGE_RIGHT)
        cam_height = WINDOW_HEIGHT - (cam_top + CAMERA_EDGE_BOTTOM)
        self.camera_rect = pygame.Rect(cam_left, cam_top, cam_width, cam_height)

    def draw(self, player):
        if player.collide_rect.left < self.camera_rect.left:
            self.camera_rect.left = player.collide_rect.left
        if player.collide_rect.right > self.camera_rect.right:
            self.camera_rect.right = player.collide_rect.right
        if player.collide_rect.top < self.camera_rect.top:
            self.camera_rect.top = player.collide_rect.top
        if player.collide_rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = player.collide_rect.bottom

        # camera offset 
        self.offset = pygame.math.Vector2(
            self.camera_rect.left - CAMERA_EDGE_LEFT,
            self.camera_rect.top - CAMERA_EDGE_TOP)

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

