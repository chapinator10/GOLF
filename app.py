from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class GolfGame:
    def __init__(self):
        self.players = {}
        self.history = []
        self.round = 0
        self.game_over = False
        self.winner = None

    def add_player(self, name):
        if name and name not in self.players:
            self.players[name] = 0
            return True
        return False

    def call_it(self, caller, correct, hand_values):
        self.round += 1
        change = -25 if correct else 25
        self.players[caller] += change
        entry = {
            'round': self.round,
            'caller': caller,
            'correct': correct,
            'hand_values': hand_values.copy(),
            'score_changes': {caller: change}
        }

        for name, val in hand_values.items():
            self.players[name] += val
            entry['score_changes'][name] = val

        self.history.append(entry)

        for score in self.players.values():
            if abs(score) >= 100:
                self.game_over = True
                self.determine_winner()
                break

    def determine_winner(self):
        self.winner = min(self.players, key=self.players.get)

    def reset(self):
        self.__init__()


# Global game instance
game = GolfGame()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_player":
            name = request.form.get("player_name")
            game.add_player(name)

        elif action == "call_it":
            caller = request.form.get("caller")
            correct = request.form.get("correct") == "yes"
            hand_values = {}
            for name in game.players:
                if name != caller:
                    val = request.form.get(f"hand_{name}")
                    try:
                        hand_values[name] = int(val)
                    except:
                        hand_values[name] = 0
            game.call_it(caller, correct, hand_values)

        elif action == "reset":
            game.reset()

        return redirect(url_for('index'))

    return render_template("index.html", game=game)

if __name__ == "__main__":
    app.run(debug=True)
