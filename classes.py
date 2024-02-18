import uuid

class Player:
    def __init__(self, sid: str, cookie_id:str, display_name: str) -> None:
        self.session_id = cookie_id
        self.sid = sid
        self.display_name = display_name


class Lobby:
    def __init__(self, code: int) -> None:
        self.players = []
        self.code = code

    def has_player(self, player: Player) -> bool:
        return player.sid in [p.sid for p in self.players]

    def add_player(self, player: Player) -> bool:
        if not self.has_player(player):
            self.players.append(player)
            return True
        else:
            return False

    def remove_player(self, player: Player) -> bool:
        if self.has_player(player):
            self.players.remove(player)
            return True
        else:
            return False
