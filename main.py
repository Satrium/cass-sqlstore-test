import time, json
import cassiopeia as cass
from cassiopeia.core import Summoner, Account, Match, League, ChampionMasteries, ChallengerLeague
from cassiopeia._configuration import settings
from cassiopeia.data import Platform, Queue

from cassiopeia_sqlstore.common import Constant

desired_name_length = 30

def fill_string_to_size(string):
    string_length = len(string)
    for i in range(string_length, desired_name_length):
        string = string + " "
    return string

def get_title(string):
    desired_length = 25 + desired_name_length
    string_length = len(string)
    characters_to_fill = desired_length - string_length
    part = characters_to_fill / 2
    string = ("#" * (int(part)-1)) + " " + string + " "
    while len(string) < desired_length:
        string = string + "#"
    return string

def get_endl():
    return "#" * (25 + desired_name_length)

def get_sqlstore():
    cass.apply_settings({
        "pipeline":{
            "SQLStore":{
                "connection_string":"postgres://cassio:cassio@localhost/cassio",
                "package":"cassiopeia_sqlstore.SQLStore",
                "debug":False
            },
            "DDragon":{},
            "RiotAPI":{}
        }
    })
    cass.set_default_region("EUW")
    settings = cass.configuration._settings
    for source in settings.pipeline._sources:
        for s in source:
            if s.__class__.__name__ == "SQLStore":
                return s

def title(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(get_title(name))
            func(*args, **kwargs)
        return wrapper
    return decorator

times = {}

def add_time(key, time):
    if not key in times:
        times[key] = [time]
    else:
        times[key].append(time)

def clear_constant_cache():
    constant._cache_by_id = {}
    constant._cache_by_value = {}

def check_put(function, data, name=None, key=None):
    try:
        if not name:
            name = function.__name__
        if not key:
            key = name
        mock = json.load(open(data))
        t = time.time()
        function(mock, None)
        elapsed = time.time() - t
        add_time(key, elapsed)
        print(fill_string_to_size(name), elapsed * 1000)
    except Exception as e:
        print(name + " failed with exception")
        print(e)
        import traceback
        traceback.print_exc()

def check_get(function, query, name):
    if not "platform" in query:
        query["platform"] = Platform.europe_west
    try:
        t = time.time()
        function(query, None)
        elapsed = time.time() - t
        add_time(name, elapsed)
        print(fill_string_to_size(name), elapsed * 1000)
    except Exception as e:
        print(name + " failed with exception")
        print(e)
        import traceback
        traceback.print_exc()

@title("Summoner endpoint")
def check_summoner(sqlstore):
    check_put(sqlstore.put_summoner, "mock/summoner.json")
    check_get(sqlstore.get_summoner, {"id":34918968}, "get_summoner_by_id")
    check_get(sqlstore.get_summoner, {"name":"Satrium"}, "get_summoner_by_name")
    check_get(sqlstore.get_summoner, {"account.id":38073405}, "get_summoner_by_accountid")

@title("Match endpoint")
def check_match(sqlstore):
    check_put(sqlstore.put_match, "mock/normal01.json", "put_match_first", "put_match_first")
    check_put(sqlstore.put_match, "mock/normal02.json", "put_normal", "put_match_second")
    check_get(sqlstore.get_match, {"id":3537528481}, "get_match_normal")
    check_put(sqlstore.put_match, "mock/ranked01.json", "put_ranked", "put_match_second")
    check_get(sqlstore.get_match, {"id":3534904584}, "get_match_ranked")
    check_put(sqlstore.put_match, "mock/aram01.json", "put_aram","put_match_second")
    check_get(sqlstore.get_match, {"id":3537608767}, "get_match_aram")

    check_put(sqlstore.put_timeline, "mock/timeline01.json", "put_first_timeline")
    check_put(sqlstore.put_timeline, "mock/timeline02.json", "put_second_timeline")
    check_get(sqlstore.get_timeline, {"id":3534904584}, "get_timeline")

    check_put(sqlstore.put_match, "mock/match_regionswapped.json", "put_ranked")
    check_get(sqlstore.get_match, {"id":198993936, "platform": Platform.oceania}, "get_match_ranked")

@title("Champion Mastery endpoint")
def check_champion_mastery(sqlstore):
    check_put(sqlstore.put_champion_mastery_list, "mock/championmastery.json")
    check_get(sqlstore.get_champion_mastery_list,{"summoner.id":34918968},"get_champion_mastery_list")

@title("Champion endpoint")
def check_champion(sqlstore):
    check_put(sqlstore.put_champion_status_list, "mock/championlistf2p.json", "put_champion_status_list_f2p")
    check_put(sqlstore.put_champion_status_list, "mock/championlist.json")
    check_get(sqlstore.get_champion_status_list, {}, "get_champion_list")
    check_get(sqlstore.get_champion_status_list, {"freeToPlay":True}, "get_champion_list_f2p")

@title("Spectator endpoint")
def check_spectator(sqlstore):
    check_put(sqlstore.put_current_game_info, "mock/currentgame.json")
    check_get(sqlstore.get_current_game, {"summoner.id":22412667}, "get_current_game")
    check_put(sqlstore.put_featured_games, "mock/featuredgames.json")
    check_get(sqlstore.get_featured_games, {}, "get_featured_games")

@title("League endpoint")
def check_league(sqlstore):
    check_put(sqlstore.put_league_positions, "mock/leaguepositions.json", "put_league_positions")
    check_get(sqlstore.get_league_positions, {"summoner.id":34918968}, "get_league_positions")
    check_put(sqlstore.put_league, "mock/league.json", "put_league_list")
    check_get(sqlstore.get_league, {"id":"de6e5560-fe24-11e7-b5a5-c81f66dd0e0d"}, "get_league")
    check_put(sqlstore.put_league, "mock/challenger.json", "put_challenger_league")
    check_get(sqlstore.get_challenger_league,{"queue":Queue.ranked_solo_fives}, "get_challenger_league")
    check_put(sqlstore.put_league, "mock/masters.json", "put_master_league")
    check_get(sqlstore.get_master_league,{"queue":Queue.ranked_solo_fives},"get_master_league")

@title("Lol-Status endpoint")
def check_lol_status(sqlstore):
    check_put(sqlstore.put_status, "mock/lol-status.json", "put_status")
    check_get(sqlstore.get_status, {}, "get_status")


sqlstore = get_sqlstore()

check_summoner(sqlstore)
check_match(sqlstore)
check_champion_mastery(sqlstore)
check_champion(sqlstore)
check_spectator(sqlstore)
check_lol_status(sqlstore)
check_league(sqlstore)
