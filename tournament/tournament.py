#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

class Database():

    def __init__(self):
        self.db = connect()
        self.cursor = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()
        return True

    def makeQuery(self, query):
        self.cursor.execute(query)

    def commit(self):
        self.db.commit()

    def getRows(self):
        return self.cursor.fetchall()


def commit_query(query, database_object):
    database_object.makeQuery(query)
    database_object.commit()

def deleteMatches():
    """Remove all the match records from the database."""
    with Database() as db_obj:
        #clear match records
        query = "delete from matches;"
        commit_query(query, db_obj)

        #set scores to 0
        query = "update scores set wins = 0;"
        db_obj.makeQuery(query)
        commit_query(query, db_obj)

    return


def deletePlayers():
    """Remove all the player records from the database."""
    with Database() as db_obj:
        # clear scores
        query = 'delete from scores;'
        commit_query(query, db_obj)

        #clear matches
        query = 'delete from matches'
        commit_query(query, db_obj)

        #clear players
        query = 'delete from players'
        commit_query(query, db_obj)

    return

def countPlayers():
    #TESTED -- WORKS
    """Returns the number of players currently registered."""
    with Database() as db_obj:
        query = "select count('*') from players;"
        db_obj.makeQuery(query)
        count = db_obj.getRows()[0][0]

    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    # register player in players db
    query = "insert into players values('{0}')".format(name)
    with Database() as db_obj:
        commit_query(query, db_obj)

    # get the player's unique ID number
    query = "select id from players where name='{0}'".format(name)
    with Database() as db_obj:
        commit_query(query, db_obj)
        player_id = db_obj.getRows()[0][0]

    # register the player in score with zero wins
    query = "insert into scores values('{0}',0)".format(player_id)
    with Database() as db_obj:
        commit_query(query, db_obj)

    return


def playerStandings():
    # TESTED - WORKS!
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    query = "select players.id, players.name, scores.wins, subq.n_matches from players join scores on scores.id = players.id join (select id, count(*) as n_matches from matches group by id) as subq on players.id = subq.id order by scores.wins desc;"
    with Database() as db_obj:
        db_obj.makeQuery(query)
        return db_obj.getRows()

print playerStandings()

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    with Database() as db_obj:
        # enter winner's match
        query = "insert into matches values({0},{1},{2},{3});".format(winner,0,'True',loser)
        commit_query(query, db_obj)

        # enter loser's match
        query = "insert into matches values({0},{1},{2},{3});".format(loser,0,'False',winner)
        commit_query(query, db_obj)

        # gets updated score of winner
        query = "select n_wins from (select id, count(*) as n_wins from matches where win=True group by id) as subq where id={0};".format(winner)
        commit_query(query, db_obj)
        n_wins = db_obj.getRows()[0][0]

        # update score of winner
        query = """update scores
        set wins={0}
        where id={1}""".format(n_wins, winner)
    return
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairings = []
    for idx, row in enumerate(playerStandings()):
        current_id, current_name, current_wins, current_n_matches = row 
        if idx % 2 == 0:
            # even row -- start constructing matchup
            id1, name1 = current_id, current_name
        else:
            # odd row -- finish matchtup
            id2, name2 = current_id, current_name
            pairings.append((id1, name1, id2, name2))
    return pairings

print swissPairings()

