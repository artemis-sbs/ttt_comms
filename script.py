from random import randrange

from board import *
import sbs
from lib.sbs_utils.spaceobject import SpaceObject, MSpawnPlayer, MSpawnActive
from lib.sbs_utils.tickdispatcher import TickDispatcher
from lib.sbs_utils.playership import PlayerShip
from lib.sbs_utils.consoledispatcher import ConsoleDispatcher
from lib.sbs_utils.consoledispatcher import MCommunications
from lib.sbs_utils.handlerhooks import *


class TicTacToe:
	def render(b: Board):
		state = b.check_winner()
		s = ''
		match state:
			case EndGame.UNKNOWN:
				TicTacToe.missionState = "mission_options"
				for index, p in enumerate(b.grid):
					match p:
						case Turn.X_TURN:
							s += "X "
						case Turn.O_TURN:
							s += "O "
						case _:
							s += f'. '
							
					if (index % 3) == 2:
						s += ' :  '
			case EndGame.X_WINS:
				s = "X Wins"
			case EndGame.O_WINS:
				s = "O Wins"
			case EndGame.DRAW:
				s = "Draw"
		return s


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


class Player(PlayerShip, MSpawnPlayer, MCommunications):
	def __init__(self):
		pass

	def spawn(self, sim):
		# playerID will be a NUMBER, a unique value for every space object that you create.
		super().spawn(sim,0,0,0, "Artemis", "TSN", "Battle Cruiser")
		self.enable_comms("ter white 0 0;ter #fff 5 2;ter #fff 6 3 -3 2;ter white 0 0;ter #fff 5 2;ter white 0 0;ter #fff 5 2;")
		# Just an example every 5 seconds call on_tick
		TickDispatcher.do_interval(sim, self._tick, 5)

	def _tick(self, sim, task):
		print("Example delayed tick")

	def comms_message(self, sim, message, other_id):
		stat: Station = SpaceObject.get_as(other_id, Station)
		if stat is None:
			return

		match message:
			case 'replay':
				stat.b.clear()
			case _:
				slot = int(message)
				stat.b.set_grid(slot)
				# 

		# Have to repaint thee buttons
		self.show_comms_ttt(sim, other_id)

	def comms_selected(self, sim, other_id):
		tempStr = f"Selected: {other_id}  (comms)"

		sbs.send_message_to_player_ship(0, "green", tempStr)

		# this sends data about who the comms officer is talking to now
		self.show_comms_ttt(sim, other_id)

	def show_comms_ttt(self, sim, other_id):
		if not sim.space_object_exists(other_id):
			return

		otherShip = sim.get_space_object(other_id)
		blob = otherShip.data_set

		if "behav_station" == otherShip.tick_type:
			text = blob.get("name_tag", 0)
			if not otherShip.side:
				text += " (" + otherShip.side + ")"

		# get the station by ID
		stat: Station = SpaceObject.get_as(other_id, Station)

		if stat is None:
			return

		render = TicTacToe.render(stat.b)
		if stat.b.turn != Turn.X_TURN:
			sbs.send_comms_message_to_player_ship(self.id, other_id, "green",
											  self.face_desc, 'Artemis > '+text,
											  render,
											  "player")
		else:
			sbs.send_comms_message_to_player_ship(self.id, other_id, "blue",
											  stat.face_desc, f'{text} > Artemis',
											  render,
											  "Station")
		print(render)
		
		sbs.send_comms_selection_info(self.id, stat.face_desc, "pink", text)
		if stat.b.check_winner() != EndGame.UNKNOWN:
			sbs.send_comms_button_info(self.id, "red", f"Replay", f"replay")

		elif stat.b.turn == Turn.X_TURN:
			for i, s in enumerate(stat.b.grid):
				if s == EndGame.UNKNOWN:
					sbs.send_comms_button_info(
						self.id, "red", f"pick {i+1}", f"{i}")
		elif stat.b.turn == Turn.O_TURN:
			# Have the station play in 5 seconds
			task = TickDispatcher.do_once(sim, self.station_play, 5)
			task.station_id = other_id

	def station_play(self, sim, t):
		slot = randrange(0,8)
		stat: Station = SpaceObject.get_as(t.station_id, Station)
		# This would be bad
		if stat is None:
			return

		done = False
		while not done:
			# pick a slot randomly
			if stat.b.grid[slot] == EndGame.UNKNOWN:
				stat.b.set_grid(slot)
				break
			slot = randrange(0,8)
			
		# update Comms buttons
		self.show_comms_ttt(sim, t.station_id)

class GuiMain:
	def __init__(self) -> None:
		self.gui_state = 'options'

	def present(self, sim):
		match self.gui_state:
			case  "sim_on":
				self.gui_state = "blank"
				sbs.send_gui_clear(0)

			case  "options":
				sbs.send_gui_clear(0)
				# Setting this to a state we don't process
				# keeps the existing GUI displayed
				self.gui_state = "presenting"
				sbs.send_gui_text(
					0, "Mission: Comms TicTacToe.^^This is a comms only mission that plays TicTacToe with all ships.^^This is to teach sending comms messages", "text", 25, 30, 99, 90)
				sbs.send_gui_button(0, "Start Mission", "start", 80, 95, 99, 99)

	def on_message(self, sim, message_tag, clientID):
		match message_tag:
			case "continue":
				self.gui_state = "blank"

			case "start":
				sbs.create_new_sim()
				sbs.resume_sim()
				Mission.start(sim)


class Mission:
	main = GuiMain()
	player = Player()
	stations = []

	def start(sim):
		Mission.player.spawn(sim)
		for s in range(4):
			station = Station()
			station.spawn(sim)
		TickDispatcher.do_once(sim, lambda sim, t: print("Tick once"), 3)
		TickDispatcher.do_interval(
			sim, lambda sim, t: print("Tick 3 times"), 3, 3)


def HandlePresentGUI(sim):
	Mission.main.present(sim)

########################################################################################################


def HandlePresentGUIMessage(sim, message_tag, clientID):
	Mission.main.on_message(sim, message_tag, clientID)
	# Later this should be
	# GuiDispatcher.on_message(sim, message_tag, clientID)
	# and the GUI is found by ID

