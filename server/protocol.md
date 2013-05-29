Big fat refactor two: messages no longer bother with responses. It's all very UDP.

Registration
============

Console to server. Must be the first transaction.

{ 
    'a' : 'register'
    'name' : _console name as string_ 
}

Status
======

Console to server. Report the console's current status. If a status packet is not recieved within two seconds, the console is determined to have timed out and is dropped (all in-progress games being decided randomly).

Query:
{
    'a' : 'status'
    'avail_slots': _list of available message slots_
    'avail_games': _suggested games_
    'bored': _boolean; true if the console is waiting for a new game_
}

Message Slots
-------------

Message slot objects describe an available space on the console for displaying
a message. It is usually characterized by a length.
{
    'slotid': _identifier for this slot_
    'len': _numeric width of available slot in characters_
}

Available Games
---------------

Available game objects represent potential games this console can play at this time.
{
    'message': _message to display on other console_
    'level': _numeric difficulty (optional)_
    'time': _maximum time to accomplish game (optional)_
    'gameid': _id of this game_
}

Messages
========

Server to console. Messages fill message slots. They can be posted to fill slots that are currently empty, overwrite full slots, or release slots.
{
    'a': 'message'
    'slotid': _identifier for this slot, as in message slot object_
    'text': _text to display in the slot; null to free slot_


Game Update
===========
Console to server. Game updates are posted whenever a game is in progress, or after it has been won or lost.
{
    'a': 'update'
    'gameid': _id of this game_
    'running': _boolean, true if game in progress; if false, result included_
    'result': _boolean; true if won, false if lost_
    'score': _numeric, optional; for spectacular win or massive fail_
}

Game Control
============
Server to console. A game control message is sent to start or cancel a game.
{
    'a': 'control'
    'operation': _string, either 'start' or 'cancel'_
    'game': _entire game object as above_
}

