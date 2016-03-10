import pygame

from objects.game_object import BaseObject

from maths.vector import Vector

from constants import SPRITE_MANAGER, SCREEN, BACKGROUND

from math import atan2, pi, cos, sin, radians

ANGULAR_VELOCITY = 7
SPEED_GROWTH = .2
SPEED_CHANGE = 3
MAX_SPEED = 5
BASE_SPEED = 1


class TestPilot(BaseObject):

    def __init__(self, sprite_name, controller, pos):
        BaseObject.__init__(self, sprite_name, pos, SPRITE_MANAGER.instance)

        self.old_image = self.image
        self.joystick = controller
        self.create_point = 1
        # in degrees, 0 is top, 90 is left, 180 is down, 270 is right
        self.facing_direction = 0
        self.moving_direction = 0
        self.prev_moving_direction = 0
        self._rotate(self.facing_direction)
        self.trajectory = Vector(0, 0)
        self.prev_trajectory = Vector(0, 0)

        self.radius = self.rect.centerx - self.rect.x
        self.old_hspeed, self.old_vspeed = 0, 0
        self.hspeed, self.vspeed = 1, 1
        self.speed = BASE_SPEED
        self.prev_y = 0
        self.prev_x = 0
        self.begun_movement = False
        self.point_list = []
        self.changed_dir = False
        self.slowing_down = False
        self.slowing_down_x = False
        self.slowing_down_y = False

    def _adjust_angle(self):
        dx = self.right.x - self.rect.centerx
        dy = self.right.y - self.rect.centery
        rads = atan2(dy, dx)
        rads %= 2*pi
        return rads

    def _rotate(self, angle):
        self.image = pygame.transform.rotate(self.old_image, angle)
        self.rect = self.image.get_rect()

    def _update_rotation(self):
        if self.right.x < 0:
            self.facing_direction += ANGULAR_VELOCITY
            if self.facing_direction > 360:
                self.facing_direction -= 360
        else:
            self.facing_direction -= ANGULAR_VELOCITY
            if self.facing_direction < 0:
                self.facing_direction += 360
        self._rotate(self.facing_direction)

    def _adjust_speed(self):
        # these number might be wrong...
        if self.facing_direction > 0 and self.facing_direction < 90:
            self._update_speeds(-1, -1)
        elif self.facing_direction == 90:
            self._update_speeds(-1, 0)
        elif self.facing_direction > 90 and self.facing_direction < 180:
            self._update_speeds(-1, 1)
        elif self.facing_direction == 180:
            self._update_speeds(0, 1)
        elif self.facing_direction > 180 and self.facing_direction < 270:
            self._update_speeds(1, 1)
        elif self.facing_direction == 270:
            self._update_speeds(1, 0)
        elif self.facing_direction > 270 and self.facing_direction < 360:
            self._update_speeds(1, -1)
        elif self.facing_direction == 360 or self.facing_direction == 0:
            self._update_speeds(0, -1)

    def _update_speeds(self, x, y):
        self._update_vspeed(y)
        self._update_hspeed(x)

    # need to redo all this shit...
    def _update_vspeed(self, y):
        # take an iterative apporach...
        if y == 0:
            return
        if y > 0:
            if self.prev_y >= 0:
                if self.slowing_down_y:
                    self.vspeed, self.slowing_down_y = self.slow_down(self.vspeed)
                else:
                    self.vspeed += SPEED_GROWTH
                    if self.vspeed > MAX_SPEED:
                        self.vspeed = MAX_SPEED
                self.prev_y = y
            elif self.prev_y < 0:
                self.slowing_down = True
                self.vspeed, self.slowing_down_y = self.slow_down(self.vspeed)  # we are slowing down
                self.prev_y = y
        elif y < 0:
            if self.prev_y <= 0:
                if self.slowing_down_y:
                    self.vspeed, self.slowing_down_y = self.slow_down(self.vspeed)
                else:
                    self.vspeed += SPEED_GROWTH
                    if self.vspeed > MAX_SPEED:
                        self.vspeed = MAX_SPEED
                self.prev_y = y
            elif self.prev_y > 0:
                self.slowing_down = True
                self.vspeed, self.slowing_down_y = self.slow_down(self.vspeed)
                self.prev_y = y

    def slowed(self, speed):
        if speed < 1:
            return True
        return False

    def slow_down(self, speed):
        if self.slowed(speed):
            self.slowing_down = False
            return speed, False
        else:
            speed *= .95
            return speed, True

    # need to redo all this shit...
    def _update_hspeed(self, x):
        if x == 0:
            return
        if x > 0:
            if self.prev_x >= 0:
                if self.slowing_down_x:
                    self.hspeed, self.slowing_down_x = self.slow_down(self.hspeed)
                else:
                    self.hspeed += SPEED_GROWTH
                    if self.hspeed > MAX_SPEED:
                        self.hspeed = MAX_SPEED
                self.prev_x = x
            elif self.prev_x < 0:
                self.slowing_down = True
                self.hspeed, self.slowing_down_x = self.slow_down(self.hspeed)
                self.prev_x = x
        elif x < 0:
            if self.prev_x <= 0:
                if self.slowing_down_x:
                    self.hspeed, self.slowing_down_x = self.slow_down(self.hspeed)
                else:
                    self.hspeed += SPEED_GROWTH
                    if self.hspeed > MAX_SPEED:
                        self.hspeed = MAX_SPEED
                self.prev_x = x
            elif self.prev_x > 0:
                self.slowing_down = True
                self.hspeed, self.slowing_down_x = self.slow_down(self.hspeed)
                self.prev_x = x

    def _get_new_pos(self):
            if self.slowing_down:
                rads = self.prev_moving_direction
            else:
                rads = radians(self.moving_direction)
                self.prev_moving_direction = rads
            dx, dy = sin(rads) * (BASE_SPEED * self.hspeed), cos(rads) * (BASE_SPEED * self.vspeed)
            self.pos.x -= dx
            self.pos.y -= dy

    def _check_inputs(self):
        self.left, self.right = self.joystick.get_axes()

        if self.left.x == 0 and self.left.y == 0:
            if self.right.x != 0 or self.right.y != 0:
                self._update_rotation()

        if self.left.x != 0 or self.left.y != 0:
            self.moving_direction = self.facing_direction
            self._adjust_speed()
            self.begun_movement = True

    def update(self):
        self._check_inputs()
        if self.begun_movement:
            self._get_new_pos()
        self.move()
