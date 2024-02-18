class Round:
    def __init__(self, round_data, max_value, min_value, chunks=5):
        self.round_data = round_data
        self.chunks = chunks
        self.max_value = max_value
        self.min_value = min_value
        self.players = {}
        self.active = True

    def add_player(self, player_name, account):
        """
        Add a player to the round with their corresponding account.

        player_name (str): Name of the player
        account (Account): Account object representing the player's funds and shares
        """
        self.players[player_name] = account

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

    def get_all_player_accounts(self):
        """
        Get all player accounts in the round.

        Returns:
            dict: Dictionary containing player names as keys and corresponding Account objects as values
        """
        return self.players
    
    def end_round(self):
        self.active = False