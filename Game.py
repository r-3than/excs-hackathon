class Game:
    def __init__(self):
        self.rounds = []
        self.players = {}
        self.active_round = None
        self.active = True

    def add_round(self, round):
        self.rounds.append(round)

    def add_player(self, player_session_token, account):
        """
        Add a player to the round with their corresponding account.

        player_name (str): Name of the player
        account (Account): Account object representing the player's funds and shares
        """
        self.players[player_session_token] = account

    def get_player_account(self, player_name):
        """
        Get the account of a player.

        player_name (str): Name of the player
        Returns:
            Account: Account object representing the player's funds and shares
        """
        return self.players.get(player_name)

    def remove_player(self, player_name):
        """
        Remove a player from the round.

        player_name (str): Name of the player to remove
        """
        if player_name in self.players:
            del self.players[player_name]

    def end_game(self):
        self.active = False