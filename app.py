from flask import Flask, render_template, request, redirect, url_for
import os
import json # Import json to safely pass the players dictionary

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
            'hand_values': hand_values.copy(), # Store hand values provided
            'score_changes': {caller: change} # Initialize score changes for caller
        }

        for name, val in hand_values.items(): # These are already the non-caller players
            self.players[name] += val
            entry['score_changes'][name] = val # Add score changes for other players

        self.history.append(entry)

        for score in self.players.values():
            if abs(score) >= 100:
                self.game_over = True
                self.determine_winner()
                break

    def determine_winner(self):
        # Winner is the player with the lowest score
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
            # Iterate through all players to collect their hand values,
            # but only if they are not the caller.
            # The JS handles presenting only non-caller inputs,
            # but this server-side logic ensures correctness.
            for name in game.players:
                if name != caller: # IMPORTANT: Only process hand values for non-callers
                    val = request.form.get(f"hand_{name}")
                    try:
                        hand_values[name] = int(val)
                    except (ValueError, TypeError): # Handle cases where input might not be a valid number
                        hand_values[name] = 0 # Default to 0 if invalid input
            game.call_it(caller, correct, hand_values)

        elif action == "reset":
            game.reset()

        return redirect(url_for('index'))

    return render_template("index.html", game=game)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) # Added debug=True for easier development
