counter = 100


class User:

    def __init__(self, user_id, name, password):
        # global counter
        # counter += 1
        self.id = user_id
        self.name = name
        self.password = password
        self.countGames = 0
        self.words = {}
        self.countWins = 0

    # def __str__(self):
    #     return f"id: {self.id} " \
    #            f"name: {self.name}" \
    #            f" password: {self.password} " \
    #            f" count games: {self.countGames}" \
    #            f" count wins: {self.countWins}"
