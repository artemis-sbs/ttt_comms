import sbs
from random import randrange
from board import *
from lib.sbs_utils.spaceobject import SpaceObject, MSpawnActive
from lib.sbs_utils.consoledispatcher import MCommunications
from lib.sbs_utils.tickdispatcher import TickDispatcher
import lib.sbs_utils.faces as faces


class TicTacToe:
    def render(b: Board):
        state = b.check_winner()
        s = ''
        match state:
            case EndGame.X_WINS:
                s = "X Wins^^"
            case EndGame.O_WINS:
                s = "O Wins^^"
            case EndGame.DRAW:
                s = "Draw^^"
            case _:
                if b.turn == Turn.X_TURN:
                    s = "X-TURN^^"
                else:
                    s = "O-TURN^^"

        
        for index, p in enumerate(b.grid):
            match p:
                case Turn.X_TURN:
                    s += "X "
                case Turn.O_TURN:
                    s += "O "
                case _:
                    s += f'. '

            if (index % 3) == 2:
                s += '^^'

        return s


class Station(SpaceObject, MSpawnActive, MCommunications):
    count = 0
    first_contact = True

    def __init__(self):
        self.num = Station.count
        Station.count += 1
        self.b = Board()

        self.face_desc = faces.random_skaraan()

    def spawn(self, sim):
        super().spawn(sim, -500, 0, self.num * 400,
                      f"DS{Station.count}", "TSN", "Starbase", "behav_station")
        self.enable_comms(self.face_desc)

        

    def comms_message(self, sim, message, other_id):
        match message:
            case 'replay':
                self.b.clear()
            case _:
                slot = int(message)
                self.b.set_grid(slot)
                #

        # Have to repaint thee buttons
        self.show_comms_ttt(sim, other_id)
        
    def comms_selected(self, sim, player_id):
        tempStr = f"Selected: {self.id}  (comms)"

        sbs.send_message_to_player_ship(player_id, "green", tempStr)

        # this sends data about who the comms officer is talking to now
        if self.first_contact:
            self.show_comms_ttt(sim, player_id)
            self.first_contact = False

    def show_comms_ttt(self, sim, player_id):
        player_so = SpaceObject.get(player_id)
        if player_so is None:
            return
        station_text = self.comm_id(sim)
        # get the player by ID
        player_text = player_so.comm_id(sim)

        render = TicTacToe.render(self.b)
        if self.b.turn != Turn.X_TURN:
            # station turn
            sbs.send_comms_message_to_player_ship(player_id, self.id,  "green",
                                                  player_so.face_desc, f'{player_text}>{station_text}',
                                                  render,
                                                  "player")
        else:
            sbs.send_comms_message_to_player_ship(player_id, self.id, "blue",
                                                  self.face_desc, f'{station_text}>{player_text}',
                                                  render,
                                                  "Station")
        print(render)

        sbs.send_comms_selection_info(player_id, self.face_desc, "pink", station_text)
        #sbs.send_comms_selection_info(player_id, faces.random_torgoth(), "pink", station_text)
        if self.b.check_winner() != EndGame.UNKNOWN:
            sbs.send_comms_button_info(player_id, "red", f"Replay", f"replay")

        elif self.b.turn == Turn.X_TURN:
            for i, s in enumerate(self.b.grid):
                if s == EndGame.UNKNOWN:
                    sbs.send_comms_button_info(
                        player_id, "red", f"pick {i+1}", f"{i}")
        elif self.b.turn == Turn.O_TURN:
            # Have the station play in 5 seconds
            t = TickDispatcher.do_once(sim, self.station_play, 5)
            t.player_id = player_id



    def station_play(self, sim, t):
        slot = randrange(0, 8)
        done = False
        while not done:
            # pick a slot randomly
            if self.b.grid[slot] == EndGame.UNKNOWN:
                self.b.set_grid(slot)
                break
            slot = randrange(0, 8)

        # update Comms buttons
        self.show_comms_ttt(sim, t.player_id)
