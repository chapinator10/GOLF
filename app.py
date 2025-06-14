from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "golf-secret-key"

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
                    try:
                        val = int(request.form.get(f"hand_{name}", 0))
                    except:
                        val = 0
                    hand_values[name] = val
            game.call_it(caller, correct, hand_values)

        elif action == "reset":
            game.reset()

        return redirect(url_for('index'))

    # Calculate basic stats
    correct_calls = sum(1 for h in game.history if h["correct"])
    total_calls = len(game.history)
    correct_percent = round((correct_calls / total_calls) * 100) if total_calls > 0 else 0
    avg_hand_value = 0
    hand_total = sum(sum(entry["hand_values"].values()) for entry in game.history)
    if total_calls > 0:
        avg_hand_value = round(hand_total / total_calls)

    return render_template(
        "index.html",
        game=game,
        correct_percent=correct_percent,
        avg_hand_value=avg_hand_value,
        total_rounds=total_calls
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

