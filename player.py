from typing import Tuple
import pygame
import json
from constant import *

class Player(pygame.sprite.Sprite):
    def __init__(self, player_id: str, position: pygame.math.Vector2, groups: Tuple[pygame.sprite.Group], collide_group: pygame.sprite.Group):
        super().__init__(groups)
        self.animation_index = 0
        self.animation_frames = []
        self.animations = {}

        self.state = "idle" # idle, walk, attack, hit
        self.direction = "right" # right, left
        self.is_jumping = True

        self.player_id = player_id
        self.position = position
        self.vertical_speed = 0
        self.horizontal_speed = 0

        self.collide_group = collide_group

        self.load_config()
        self.setup()

    def load_config(self):
        with open(f"assets/image/player/{self.player_id}/config.json") as f:
            data = json.load(f)
        self.config_data = data

    def setup(self):
        data = self.config_data
        for animation in data["animations"]:
            self.animations[animation] = []
            for frame_name in data["animations"][animation]["frames"]:
                frame_path = f"assets/image/player/{self.player_id}/" + frame_name
                frame = pygame.image.load(frame_path).convert_alpha()
                self.animations[animation].append(frame)
        self.animation_frames = self.animations[data["default_animation"]]
        self.image = self.animation_frames[self.animation_index]

        # 根据 pivot 设置 rect
        pivot_data = data["animations"][data["default_animation"]]["pivot"]
        pivot_point = pygame.math.Vector2(pivot_data["dx"], pivot_data["dy"])
        self.rect = self.image.get_rect(topleft=(self.position - pivot_point).xy)

        # 根据 rect 设置 collide_rect
        collide_data = data["animations"][data["default_animation"]]["frame_rect"]
        collide_point = pygame.math.Vector2(collide_data["dx"], collide_data["dy"])
        self.collide_rect = pygame.Rect(
            self.rect.x + collide_point.x,
            self.rect.y + collide_point.y,
            collide_data["width"],
            collide_data["height"]
        )

        self.attack_rect = pygame.Rect(0, 0, 0, 0)

    def update_animation(self):
        if self.direction == "right":
            self.image = self.animation_frames[int(self.animation_index)]
        elif self.direction == "left":
            self.image = pygame.transform.flip(self.animation_frames[int(self.animation_index)], True, False)
        self.animation_index += self.config_data["animations"][self.state]["frameRate"]
        if self.animation_index >= len(self.animation_frames):
            self.animation_index = 0
            self.action_after_animation()

    
    def action_after_animation(self):
        # 攻击或受击动画播放完毕后，恢复到 idle 或 walk 状态
        if self.state in ["attack", "hit"]:
            if self.state in ["attack"]:
                if "move_after_attack" in self.config_data["animations"]["attack"]:
                    move_after_attack = self.config_data["animations"]["attack"]["move_after_attack"]
                    if self.direction == "right":
                        self.position.x += move_after_attack["dx"]
                    elif self.direction == "left":
                        self.position.x -= move_after_attack["dx"]
                    self.position.y += move_after_attack["dy"]

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]:
                self.change_state("walk")
            else:
                self.change_state("idle")
    
    
    def change_state(self, state):
        self.state = state
        self.animation_frames = self.animations[state]
        self.animation_index = 0
        # self.is_jumping = True
        self.collide_rect.x = self.position.x - self.config_data["animations"][state]["pivot"]["dx"] + self.config_data["animations"][state]["frame_rect"]["dx"]
        self.collide_rect.y = self.position.y - self.config_data["animations"][state]["pivot"]["dy"] + self.config_data["animations"][state]["frame_rect"]["dy"]
        self.collide_rect.width = self.config_data["animations"][state]["frame_rect"]["width"]
        self.collide_rect.height = self.config_data["animations"][state]["frame_rect"]["height"]
    
    def change_direction(self, direction):
        self.direction = direction

        pivot_data = self.config_data["animations"][self.state]["pivot"]
        collide_rect = self.config_data["animations"][self.state]["frame_rect"]
        if self.direction == "right":
            self.collide_rect.x = self.position.x - pivot_data["dx"] + collide_rect["dx"]
        elif self.direction == "left":
            self.collide_rect.right = self.position.x + pivot_data["dx"] - collide_rect["dx"]

    def user_input(self):
        keys = pygame.key.get_pressed()
        key_pressed_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        key_pressed_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        if self.state not in ["attack", "hit"] and not self.is_jumping:
            if key_pressed_left and key_pressed_right:
                self.horizontal_speed = 0
            elif key_pressed_left:
                self.change_direction("left")
                self.horizontal_speed = -self.config_data["speed"]
            elif key_pressed_right:
                self.change_direction("right")
                self.horizontal_speed = self.config_data["speed"]
            else:
                self.horizontal_speed = 0

        if self.state == "hit":
            self.horizontal_speed *= HIT_SPEED_REDUCTION

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vertical_speed = -self.config_data["jump_speed"]

        # if self.collide_rect.right > WINDOW_WIDTH:
        #     self.collide_rect.right = WINDOW_WIDTH
        # if self.collide_rect.left < 0:
        #     self.collide_rect.left = 0

    def apply_horizontal_movement(self):
            self.collide_rect.x += self.horizontal_speed

    def update_horizontal_collisions(self):
        for sprite in self.collide_group:
            if self.collide_rect.colliderect(sprite.collide_rect):
                if self.horizontal_speed > 0:
                    if self.position.x < sprite.collide_rect.right:
                        self.collide_rect.right = sprite.collide_rect.left
                    else:
                        self.collide_rect.left = sprite.collide_rect.right
                elif self.horizontal_speed < 0:
                    if self.position.x > sprite.collide_rect.left:
                        self.collide_rect.left = sprite.collide_rect.right
                    else:
                        self.collide_rect.right = sprite.collide_rect.left
                else:
                    if self.position.x > sprite.collide_rect.left:
                        self.collide_rect.left = sprite.collide_rect.right
                    else:
                        self.collide_rect.right = sprite.collide_rect.left
        
    def apply_vertical_movement(self):
        self.vertical_speed += GRAVITY
        self.collide_rect.y += self.vertical_speed
    
    def update_vertical_collisions(self):
        for sprite in self.collide_group:
            if self.collide_rect.colliderect(sprite.collide_rect):
                if self.vertical_speed > 0:
                    self.collide_rect.bottom = sprite.collide_rect.top
                    self.is_jumping = False
                    self.vertical_speed = 0
                elif self.vertical_speed < 0:
                    self.collide_rect.top = sprite.collide_rect.bottom
                    self.vertical_speed = 0
        
        if not self.is_jumping and not self.vertical_speed == 0:
            self.is_jumping = True
            
    
    def update_player_rect(self):
        pivot_data = self.config_data["animations"][self.state]["pivot"]
        frame_rect_data = self.config_data["animations"][self.state]["frame_rect"]
        attack_rect_data = self.config_data["animations"]["attack"]["attack_frame_rects"]
        if self.direction == "right":
            # self.collide_rect.x = self.position.x - pivot_data["dx"] + frame_rect_data["dx"]
            # self.collide_rect.y = self.position.y - pivot_data["dy"] + frame_rect_data["dy"]
            self.rect.x = self.collide_rect.x - frame_rect_data["dx"]
            self.rect.y = self.collide_rect.y - frame_rect_data["dy"]
            self.position.x = self.rect.x + pivot_data["dx"]
            self.position.y = self.rect.y + pivot_data["dy"]
            
            if self.state == "attack":
                self.attack_rect.x = self.rect.x + attack_rect_data[int(self.animation_index)]["dx"]
                self.attack_rect.y = self.rect.y + attack_rect_data[int(self.animation_index)]["dy"]
                self.attack_rect.width = attack_rect_data[int(self.animation_index)]["width"]
                self.attack_rect.height = attack_rect_data[int(self.animation_index)]["height"]
            else:
                self.attack_rect.x = 0
                self.attack_rect.y = 0
                self.attack_rect.width = 0
                self.attack_rect.height = 0
        elif self.direction == "left":
            # self.collide_rect.x = self.position.x - pivot_data["dx"] - frame_rect_data["dx"]
            # self.collide_rect.y = self.position.y - pivot_data["dy"] + frame_rect_data["dy"]
            self.rect.right = self.collide_rect.right + frame_rect_data["dx"]
            self.rect.top = self.collide_rect.top - frame_rect_data["dy"]
            self.position.x = self.rect.right - pivot_data["dx"]
            self.position.y = self.rect.y + pivot_data["dy"]
            if self.state == "attack":
                self.attack_rect.right = self.rect.right - attack_rect_data[int(self.animation_index)]["dx"]
                self.attack_rect.top = self.rect.top + attack_rect_data[int(self.animation_index)]["dy"]
                self.attack_rect.width = attack_rect_data[int(self.animation_index)]["width"]
                self.attack_rect.height = attack_rect_data[int(self.animation_index)]["height"]
            else:
                self.attack_rect.x = 0
                self.attack_rect.y = 0
                self.attack_rect.width = 0
                self.attack_rect.height = 0

    def be_hit(self):
        self.change_state("hit")

    def handle_event(self, event):
        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            # if event.key in [pygame.K_RIGHT, pygame.K_d] and not self.state == "attack":
            #     self.change_direction("right")
            # elif event.key in [pygame.K_LEFT, pygame.K_a] and not self.state == "attack":
            #     self.change_direction("left")

            if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_d, pygame.K_a] and self.state not in ["attack"]:
                self.change_state("walk")

            # jump
            if event.key == pygame.K_SPACE:
                if not self.is_jumping:
                    self.is_jumping = True
                    self.vertical_speed = -self.config_data["jump_speed"]

            if event.key == pygame.K_k:
                if not self.state == "attack":
                    self.change_state("attack")

            if event.key == pygame.K_h:
                self.be_hit()

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_d, pygame.K_a] and self.state not in ["jump", "attack"]:
                if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT] and not keys[pygame.K_d] and not keys[pygame.K_a]:
                    self.change_state("idle")

    def update(self):

        self.user_input()
        self.apply_horizontal_movement()
        self.update_horizontal_collisions()
        self.apply_vertical_movement()
        self.update_vertical_collisions()
        self.update_player_rect()
        self.update_animation()




if __name__ == "__main__":
    from main import Game

    pygame.init()
    game = Game()
    game.run()
    pygame.quit()