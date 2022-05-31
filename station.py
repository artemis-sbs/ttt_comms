from random import randrange
from board import *
from lib.sbs_utils.spaceobject import SpaceObject, MSpawnActive

class Station(SpaceObject, MSpawnActive):
	count = 0

	def __init__(self):
		self.num = Station.count
		Station.count += 1
		self.b = Board()

		eyeY = randrange(1, 6)
		mouthY = randrange(1, 6)
		self.face_desc = f"ska #fff 0 0;ska #fff 0 {eyeY};ska #fff 2 {mouthY};"

	def spawn(self, sim):
		super().spawn(sim, -500,0,self.num * 400,f"DS{Station.count}","TSN", "Starbase", "behav_station" )
