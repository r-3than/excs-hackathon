import uuid

class Player:
    def __init__(self, sid: str, cookie_id:str, display_name: str) -> None:
        self.session_id = cookie_id
        self.sid = sid
        self.display_name = display_name
        self.ff_amount = 10000
        self.share_c = 0.0

    def __str__(self):
        return f"Free Funds:{self.ff_amount}, Share Count:{self.share_c}"

    def calc_share_value(self, share_value):
        """
        Returns value of shares using share_value

        share_value (float): Amount in GBP the value of 1 stock
        """
        return share_value * self.share_c

    def calc_score(self, share_value):
        """
        Returns total value of portfolio of free funds and shares

        share_value (float): Amount in GBP the value of 1 stock
        """
        return self.ff_amount + self.calc_share_value(share_value)

    def action_buy(self, buy_amount, share_value):
        """
        Action of buying an amount of stocks 

        buy_amount (float): Amount in GBP  to buy in stocks
        share_value (float): Amount in GBP the value of 1 stock
        
        Return error code 1 if trying to enter a negative amount 
        """
        if (buy_amount <= 0):
            return 1
        if (buy_amount <= self.ff_amount):

            r_buy_amount = buy_amount
            self.ff_amount -= r_buy_amount
            bought_share_c = r_buy_amount / share_value
            self.share_c += bought_share_c
                
            return f"Bought {bought_share_c} stocks for {r_buy_amount}"
        else:
            return "Insufficient funds"

    def action_sell(self, sell_amount, share_value):
        """
        Action of selling an amount of stocks 

        sell_amount (float): Amount in GBP  to sell in stocks
        share_value (float): Amount in GBP the value of 1 stock
        
        Return error code 1 if trying to enter a negative amount 
        """
        if (sell_amount <= 0):
            return 1

        acc_share_value = share_value * self.share_c
        if (sell_amount <= acc_share_value):

            sell_share_c = sell_amount / share_value
            self.share_c -= sell_share_c
            self.ff_amount += sell_amount

            return f"Sold {sell_share_c} stocks for {sell_amount}"

        else:
            return "Insufficient funds"

    def wait(self):
        """
        Waiting - no action
        """
        return "Waiting"



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
