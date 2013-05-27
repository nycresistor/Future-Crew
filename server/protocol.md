
Registration
------------

Initiated by console. All other queries are posted by the server.

Query:
{ 
    'a:'register',
    'name': _console name as string_ 
}

Response:
{
    'ok': _Boolean_,
    'id': _numeric id assigned by server_
}


Server Requests
---------------

All server requests include a numeric "qid" field; responses must include this field in their responses. The qid field is not explicitly represented in the protocol below.

Request Game
------------

Ask a console for a game to play.

Query:
{
    'a':'request_game',
    _optional fields_
    'difficulty': _value from 0.0 (trivial) to 1.0 (insane)_
}

Response:
{
    'ok': _Boolean; true if the console has a valid game to play_
    'game_id': _numeric or string identifier for this game_
    'message': _string message for another console to display_
}

Begin Game
----------

Start a game that the console had returned as a response to a game request.

Query:
{
    'a':'begin_game'
    'game_id': _numeric or string identifier for this game_
}

Response:
{
    'ok': _Boolean; true if the game has started successfully_
    'message': _string message for another console to display_
}

Console Status
--------------

Get the current status of a console.

Query:
{
    'a':'status'
}

Response:
{
    'is_playing': _Boolean; true if playing a game_
    'has_message': _Boolean; true if displaying a message on this console_
}

Game status
-----------

Query:
{
    'a':'game_status'
    'game_id': _numeric or string identifier for this game_
}

Response:
{
    'finished': _Boolean; true if game has completed_
    'outcome': _Boolean; true if succeeded for false if failed_
}

