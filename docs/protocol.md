The protocol for future crew is entirely unidirectional.

Notation note: a 'game' is a task carried out on a console. A 'session' is what players think of as a game;
a few people playing Future Crew together.

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

Starting and Stopping: Session Control
======================================

Games are started or aborted with these messages.

```
{
    'a':'session_start'
}
```


```
{
    'a':'session_abort'
}
```


Session update
==============

Server to console. Sent when game is starting, game is over, or potentially for in-game
events (like "Level 2!!!"). Whenever a session update is received, all in-progress games should
immediately be cancelled and all slots cleared.
```
{
    'a': 'session_update'
    'state': 'starting', 'won', 'lost', 'reset', or 'update'
    'message': _a message to display to all clients_
    'score': _total session score_
}
```

Status
======

Console to server. Report the console's current status. If a status packet is not recieved within two seconds, the console is determined to have timed out and is dropped (all in-progress games being decided randomly).

```
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

```
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

```
{
    'slotid': _identifier for this slot_
    'slow': _optional, True if this terminal is slow (like a teletype)_
    'len': _numeric width of available slot in characters_
}
```

Available Games
---------------

Available game objects represent potential games this console can play at this time.

```
{
    'level': _optional; numeric difficulty_
    'short': _optional; should be true if this gave is given less than 10 seconds_
    'time': _optional; maximum time to accomplish game_
    'gameid': _id of this game_
}
```

Messages
========

Server to console. Messages fill message slots. They can be posted to fill slots that are currently empty, overwrite full slots, or release slots.
```
{
    'a': 'message'
    'slotid': _identifier for this slot, as in message slot object_
    'text': _text to display in the slot; null to free slot_
    'level': _optional; numeric. 0 for normal message, negative for disposable, 1+ for ALERT_
    'success': _only displayed if this is a success/failure message; boolean value that is True if the game was won, False otherwise_
}
```

Announcements
=============

Announcement for scroller or whatnot
```
{ 
    'a': 'announcement'
    'name': _name of console that announcement pertains to (optional)_
    'message': _text of message_
    'game_score': _number of points won in this game (negative for a loss)_
    'score': _current game score_
}
```

Glitches
========

Server to console. Run a glitch which disrupts gameplay to a greater or lesser extent.
```
{
    'a': 'glitch'
    'glitchid': _identifier for this glitch, as in glitch slot object_
}
```

Game Update
===========
Console to server. Game updates are posted while a game is in progress, or after it has been won or lost. It can be used to update the message displayed on the remote console as well.
```
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
```
{
    'a': 'control'
    'operation': _string, either 'start' or 'cancel'_
    'game': _entire game object as above_
}
```
