The protocol for future crew is entirely unidirectional.

Registration
============

Console to server. Must be the first transaction.

```
{ 
    'a' : 'register'
    'name' : _console name as string_ 
}
```

Unregistration
==============

There is no unregistration message; the client merely closes the socket.

Status
======

Console to server. Report the console's current status. If a status packet is not recieved within two seconds, the console is determined to have timed out and is dropped (all in-progress games being decided randomly).

```json
Query:
{
    'a' : 'status'
    'avail_slots': _list of available message slots_
    'avail_games': _suggested games_
    'avail_glitches': _available glitches_
    'bored': _boolean; true if the console is waiting for a new game_
}
```

Glitch Slots
------------

The glitch slot describes a glitch that can run on the console.

```json
{
    'glitchid': _identifier of the glitch_
    'difficulty': _0 is completely cosmetic, 10 is game-ruining_
    'duration': _glitch duration in seconds_
}
```

Message Slots
-------------

Message slot objects describe an available space on the console for displaying
a message. It is usually characterized by a length.

```json
{
    'slotid': _identifier for this slot_
    'len': _numeric width of available slot in characters_
}
```

Available Games
---------------

Available game objects represent potential games this console can play at this time.

```json
{
    'message': _message to display on other console_
    'level': _numeric difficulty (optional)_
    'time': _maximum time to accomplish game (optional)_
    'gameid': _id of this game_
}
```

Messages
========

Server to console. Messages fill message slots. They can be posted to fill slots that are currently empty, overwrite full slots, or release slots.
```json
{
    'a': 'message'
    'slotid': _identifier for this slot, as in message slot object_
    'text': _text to display in the slot; null to free slot_
    'level': _optional; numeric. 0 for normal message, negative for disposable, 1+ for ALERT_
}
```

Glitches
========

Server to console. Run a glitch which disrupts gameplay to a greater or lesser extent.
```json
{
    'a': 'glitch'
    'glitchid': _identifier for this glitch, as in glitch slot object_
}
```

Game Update
===========
Console to server. Game updates are posted while a game is in progress, or after it has been won or lost. It can be used to update the message displayed on the remote console as well.
```json
{
    'a': 'update'
    'gameid': _id of this game_
    'message': _replacement message text (alert! hurry up!)_
    'running': _boolean, true if game in progress; if false, result included_
    'result': _boolean; true if won, false if lost_
    'score': _numeric, optional; for spectacular win or massive fail_
}
```

Game Control
============
Server to console. A game control message is sent to start or cancel a game.
```json
{
    'a': 'control'
    'operation': _string, either 'start' or 'cancel'_
    'game': _entire game object as above_
}
```
