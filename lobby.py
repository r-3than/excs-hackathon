class Lobby:
    def __init__(self, code: int) -> None:
        self.players = []
        self.code = code
        
    def add_player(self, player_id: str) -> None:
        if player_id not in self.players:
            self.players.append(player_id)
            
    def remove_player(self, player_id: str) -> None:
        if player_id in self.players:
            self.players.remove(player_id)
        