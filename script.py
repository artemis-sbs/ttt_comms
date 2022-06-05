
import sbs
from lib.sbs_utils.tickdispatcher import TickDispatcher
from lib.sbs_utils.handlerhooks import *
from player import Player
from station import Station


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

