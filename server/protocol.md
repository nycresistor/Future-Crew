
Registration
------------

Initiated by console

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

Get Status
----------

Query:
{
    'a':'status'
}


Request Game
------------

Initiated by server. Ask a console for a game to play.

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

Initiated by the server. Start a game that the console had returned as a response to a game request.

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

Game Status
-----------

Get the current status of a game.

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

