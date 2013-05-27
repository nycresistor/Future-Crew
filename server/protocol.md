BIG FAT REFACTOR: Tornado isn't really set up for the kind of messaging I was trying to do, so instead we're doing things in a more traditional webby kind of way (consoles initiate all transactions).

Registration
------------

Must be the first transaction.

Query:
{ 
    'register': _console name as string_ 
}

Response:
{
    'ok': _Boolean_,
}

Status
------

Report the console's current status. If a status packet is not recieved within two seconds, the console is determined to have timed out and is dropped (all in-progress games being decided randomly).

Everything is shoehorned into these requests.

Query:
{
    'avail_slots': _list of available message slots_
    'game_updates': _updates on currently running game(s)_
    'avail_games': _suggested games_
}

Response:
{
    'ok': _Boolean, acknowledges server is okay_
    'game_control': _start or stop running games(s)_
    'messages': _messages for message slots_
    'master_state': _global data about larger game_
}

Message Slots
-------------

Message slot objects describe an available space on the console for displaying
a message. It is usually characterized by a width and height.
{
    'slotid': _identifier for this slot_
    'w': _numeric width of available slot in characters_
    'h': _numeric width of available slot in characters (optional) (defaults to 1)_
}

Messages
--------

Messages fill message slots. They can be posted to fill slots that are currently empty, overwrite full slots, or release slots.
{
    'slotid': _identifier for this slot, as in message slot object_
    'text': _text to display in the slot; null to free slot_

Available Games
---------------

Available game objects represent potential games this console can play at this time.
{
    'message': _message to display on other console_
    'level': _numeric difficulty (optional)_
    'time': _maximum time to accomplish game (optional)_
    'gameid': _id of this game_
}

Game Update
-----------
Game updates are posted whenever a game is in progress, or after it has been won or lost.
{
    'gameid': _id of this game_
    'running': _boolean, true if game in progress; if false, result included_
    'result': _boolean; true if won, false if lost_
    'score': _numeric, optional; for spectacular win or massive fail_
}

Game Control
------------
A game control message is sent to start or cancel a game.
{
    'operation': _string, either 'start' or 'cancel'_
    'gameid': _id of this game as specified in available game object_
}

