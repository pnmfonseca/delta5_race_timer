
from flask import Flask
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, Response
from datetime import datetime

APP = Flask(__name__, static_url_path='/static')
BASEDIR = os.path.abspath(os.path.dirname(__file__))

APP.config['SECRET_KEY'] = 'secret!'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'database.db')
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(APP)

sys.path.append('../delta5interface')
sys.path.append('/home/pi/delta5/delta5interface')  # Needed to run on startup
from Delta5Race import get_race_state
from Delta5Interface import get_hardware_interface

from model.models import Pilot ,Heat ,CurrentLap ,SavedRace ,Frequency ,Profiles ,LastProfile ,FixTimeRace
from authorization import check_auth, authenticate, requires_auth
#from server import RACE
HEARTBEAT_THREAD = None

INTERFACE = get_hardware_interface()
RACE = get_race_state() # For storing race management variables

PROGRAM_START = datetime.now()
RACE_START = datetime.now() # Updated on race start commands

#
# Routes
#

@APP.route('/old/')
def index():
    '''Route to round summary page.'''
    # A more generic and flexible way of viewing saved race data is needed
    # - Individual round/race summaries
    # - Heat summaries
    # - Pilot summaries
    # Make a new dynamic route for each? /pilotname /heatnumber /
    # Three different summary pages?
    # - One for all rounds, grouped by heats
    # - One for all pilots, sorted by fastest lap and shows average and other stats
    # - One for individual heats
    #
    # Calculate heat summaries
    # heat_max_laps = []
    # heat_fast_laps = []
    # for heat in SavedRace.query.with_entities(SavedRace.heat_id).distinct() \
    #     .order_by(SavedRace.heat_id):
    #     max_laps = []
    #     fast_laps = []
    #     for node in range(RACE.num_nodes):
    #         node_max_laps = 0
    #         node_fast_lap = 0
    #         for race_round in SavedRace.query.with_entities(SavedRace.round_id).distinct() \
    #             .filter_by(heat_id=heat.heat_id).order_by(SavedRace.round_id):
    #             round_max_lap = DB.session.query(DB.func.max(SavedRace.lap_id)) \
    #                 .filter_by(heat_id=heat.heat_id, round_id=race_round.round_id, \
    #                 node_index=node).scalar()
    #             if round_max_lap is None:
    #                 round_max_lap = 0
    #             else:
    #                 round_fast_lap = DB.session.query(DB.func.min(SavedRace.lap_time)) \
    #                 .filter(SavedRace.node_index == node, SavedRace.lap_id != 0).scalar()
    #                 if node_fast_lap == 0:
    #                     node_fast_lap = round_fast_lap
    #                 if node_fast_lap != 0 and round_fast_lap < node_fast_lap:
    #                     node_fast_lap = round_fast_lap
    #             node_max_laps = node_max_laps + round_max_lap
    #         max_laps.append(node_max_laps)
    #         fast_laps.append(time_format(node_fast_lap))
    #     heat_max_laps.append(max_laps)
    #     heat_fast_laps.append(fast_laps)
    # print heat_max_laps
    # print heat_fast_laps
    return render_template('rounds-old.html', num_nodes=RACE.num_nodes, rounds=SavedRace, \
        pilots=Pilot, heats=Heat)
        #, heat_max_laps=heat_max_laps, heat_fast_laps=heat_fast_laps

@APP.route('/old/heats')
def heats():
    '''Route to heat summary page.'''
    return render_template('heats-old.html', num_nodes=RACE.num_nodes, heats=Heat, pilots=Pilot, \
        frequencies=[node.frequency for node in INTERFACE.nodes], \
        channels=[Frequency.query.filter_by(frequency=node.frequency).first().channel \
            for node in INTERFACE.nodes])

@APP.route('/old/race')
@requires_auth
def race():
    '''Route to race management page.'''
    return render_template('race-old.html', num_nodes=RACE.num_nodes,
                           current_heat=RACE.current_heat,
                           heats=Heat, pilots=Pilot,
                           fix_race_time=FixTimeRace.query.get(1).race_time_sec,
						   lang_id=RACE.lang_id,
        frequencies=[node.frequency for node in INTERFACE.nodes],
        channels=[Frequency.query.filter_by(frequency=node.frequency).first().channel
            for node in INTERFACE.nodes])

@APP.route('/old/settings')
@requires_auth
def settings():
    '''Route to settings page.'''

    return render_template('settings-old.html', num_nodes=RACE.num_nodes,
                           pilots=Pilot,
                           frequencies=Frequency,
                           heats=Heat,
                           last_profile =  LastProfile,
                           profiles = Profiles,
                           current_fix_race_time=FixTimeRace.query.get(1).race_time_sec,
						   lang_id=RACE.lang_id)

# Debug Routes

@APP.route('/old/hardwarelog')
@requires_auth
def hardwarelog():
    '''Route to hardware log page.'''
    return render_template('hardwarelog-old.html')

@APP.route('/old/database')
@requires_auth
def database():
    '''Route to database page.'''
    return render_template('database-old.html', pilots=Pilot, heats=Heat, currentlaps=CurrentLap, \
        savedraces=SavedRace, frequencies=Frequency, )
