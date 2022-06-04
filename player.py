from random import randrange

from board import *
import sbs
from lib.sbs_utils.playership import PlayerShip
import lib.sbs_utils.faces as faces


class Player(PlayerShip):
    def spawn(self, sim):
        # playerID will be a NUMBER, a unique value for every space object that you create.
        super().spawn(sim,0,0,0, "Artemis", "TSN", "Battle Cruiser")
        self.face_desc = faces.Characters.URSULA

