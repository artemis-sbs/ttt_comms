from random import randrange

from board import *
import sbs
from lib.sbs_utils.playership import PlayerShip


class Player(PlayerShip):
    def spawn(self, sim):
        # playerID will be a NUMBER, a unique value for every space object that you create.
        super().spawn(sim,0,0,0, "Artemis", "TSN", "Battle Cruiser")
        self.face_desc = "ter #964b00 8 1;ter #968b00 3 0;ter #968b00 4 0;ter #968b00 5 2;ter #fff 3 5;ter #964b00 8 4;"

