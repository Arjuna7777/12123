import collections
import random

import pygame

from arkanoid.rounds.base import BaseRound
from arkanoid.sprites.brick import Brick
from arkanoid.sprites.edge import (TopEdge,
                                   SideEdge)
from arkanoid.sprites.powerup import (CatchPowerUp,
                                      ExpandPowerUp,
                                      ExtraLifePowerUp,
                                      LaserPowerUp,
                                      SlowBallPowerUp)


class Round1(BaseRound):
    """Initialises the background, brick layout and powerups for round one."""

    # The offset from the top edge to where the bottom row of bricks starts.
    _BOTTOM_ROW_VERTICAL_OFFSET = 250

    def __init__(self, top_offset):
        """Initialise round 1.

        Args:
            top_offset:
                The number of pixels from the top of the screen before the
                top edge can be displayed.
        """
        super().__init__(top_offset)

        self.name = 'Round 1'

    def _create_background(self):
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        # TODO: background image should be loaded from a file.
        background.fill((0, 0, 100))
        return background

    def _create_edges(self):
        """Create the edge sprites and position them at the edges of the
        screen.

        Returns:
            A named tuple with attributes 'left', 'right', and 'top' that
            reference the corresponding edge sprites.
        """
        edges = collections.namedtuple('edge', 'left right top')
        left_edge = SideEdge()
        right_edge = SideEdge()
        top_edge = TopEdge()
        left_edge.rect.topleft = 0, self.top_offset
        right_edge.rect.topright = self.screen.get_width(), self.top_offset
        top_edge.rect.topleft = left_edge.rect.width, self.top_offset
        return edges(left_edge, right_edge, top_edge)

    def _create_bricks(self):
        """Create the bricks and position them on the screen.

        Returns:
            A pygame.sprite.Group of bricks.
        """
        colours = 'green', 'blue', 'yellow', 'red', 'grey'
        values = 80, 100, 120, 160, 180
        brick_types = zip(colours, values)

        # Create the distribution of powerup classes.
        powerup_classes = []
        powerup_classes.extend([CatchPowerUp] * 3)
        powerup_classes.extend([ExpandPowerUp] * 4)
        powerup_classes.extend([ExtraLifePowerUp] * 2)
        powerup_classes.extend([SlowBallPowerUp] * 2)
        powerup_classes.extend([LaserPowerUp] * 4)
        random.shuffle(powerup_classes)

        # Randomly select the indexes for the bricks that will contain
        # powerups, for the bottom 4 rows.
        powerup_indexes = random.sample(range(52), len(powerup_classes))

        bricks, count = [], 0

        # Each coloured brick forms a new layer.
        for colour, value in brick_types:
            # Grey bricks take 2 hits to destroy.
            destroy_after = 2 if colour == 'grey' else 1

            for i in range(13):
                powerup_class = None

                if count in powerup_indexes:
                    powerup_class = powerup_classes.pop(0)

                brick = Brick(colour, value, destroy_after=destroy_after,
                              powerup_cls=powerup_class)

                bricks.append(brick)
                count += 1

        self._position_bricks(bricks)

        return pygame.sprite.Group(*bricks)

    def _position_bricks(self, bricks):
        top = self.edges.top.rect.top + self._BOTTOM_ROW_VERTICAL_OFFSET
        colour, rect = None, None

        for brick in bricks:
            if colour != brick.colour:
                colour = brick.colour
                left = self.edges.left.rect.width
                if rect:
                    top -= rect.height

            if brick.visible:
                # Each layer consists of 13 bricks added horizontally.
                rect = self.screen.blit(brick.image, (left, top))
                # Update the brick's rect with the new position
                brick.rect = rect

            left += rect.width+1
