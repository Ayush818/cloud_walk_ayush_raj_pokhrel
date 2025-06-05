import re
import json
import os
from collections import defaultdict
from typing import Dict, List, Set


class QuakeLogParser:
    """
    Quake 3 Arena log parser that processes game logs and extracts statistics.
    """

    def __init__(self):
        """Initialize the parser."""
        self.games = {}
        self.current_game_id = None
        self.game_counter = 0

        # Regex pattern to match kill events
        # Format: timestamp Kill: killer_id victim_id weapon_id: killer_name killed victim_name by weapon
        self.kill_pattern = re.compile(
            r"^\s*\d+:\d+\s+Kill:\s+(\d+)\s+(\d+)\s+(\d+):\s+(.+?)\s+killed\s+(.+?)\s+by\s+(MOD_\w+)"
        )

        # Pattern to detect new game initialization
        self.init_game_pattern = re.compile(r"InitGame:")

    def parse_log_file(self, file_path: str) -> Dict:
        """
        Parse the log file and return game statistics.

        Args:
            file_path: Path to the log file

        Returns:
            Dictionary with game statistics organized by match
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Log file not found: {file_path}")

        # Reset parser state
        self.games = {}
        self.current_game_id = None
        self.game_counter = 0

        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue

                # Check for new game initialization
                if self.init_game_pattern.search(line):
                    self._start_new_game()
                    continue

                # Try to parse kill event
                kill_match = self.kill_pattern.match(line)
                if kill_match:
                    self._process_kill_event(kill_match)

        return self.games

    def _start_new_game(self):
        """Initialize a new game."""
        self.game_counter += 1
        self.current_game_id = f"game_{self.game_counter}"

        self.games[self.current_game_id] = {
            "total_kills": 0,
            "players": [],
            "kills": defaultdict(int),
        }

    def _process_kill_event(self, match):
        """
        Process a kill event from the regex match.

        Args:
            match: Regex match object containing kill event data
        """
        # If no game has been started, create one
        if self.current_game_id is None:
            self._start_new_game()

        # Extract information from the match
        killer_id = match.group(1)
        victim_id = match.group(2)
        weapon_id = match.group(3)
        killer_name = match.group(4).strip()
        victim_name = match.group(5).strip()
        weapon = match.group(6).strip()

        current_game = self.games[self.current_game_id]

        # Increment total kills for the game
        current_game["total_kills"] += 1

        # Handle world kills vs player kills
        if killer_name == "<world>":
            # World kill: decrease victim's score by 1
            if victim_name != "<world>":
                current_game["kills"][victim_name] -= 1
        else:
            # Regular player kill: increase killer's score by 1
            current_game["kills"][killer_name] += 1

        # Collect all players (excluding <world>)
        players_set = set()
        if killer_name != "<world>":
            players_set.add(killer_name)
        if victim_name != "<world>":
            players_set.add(victim_name)

        # Update players list for this game
        existing_players = set(current_game["players"])
        current_game["players"] = sorted(list(existing_players.union(players_set)))

    def _finalize_games(self):
        """Finalize all games by converting defaultdict to regular dict."""
        for game_id, game_data in self.games.items():
            # Convert defaultdict to regular dict for JSON serialization
            self.games[game_id]["kills"] = dict(game_data["kills"])

    def get_formatted_results(self) -> Dict:
        """
        Get results in the required format.

        Returns:
            Dictionary with formatted game results
        """
        self._finalize_games()
        return self.games


def main():
    """Main function to run the parser and display results."""
    print("🎮 QUAKE LOG PARSER")
    print("=" * 50)

    # Initialize parser
    parser = QuakeLogParser()

    # Parse the log file
    log_file_path = os.path.join( "log.txt")

    try:
        print(f"📁 Reading log file: {log_file_path}")
        results = parser.parse_log_file(log_file_path)

        print(f"✅ Successfully parsed {len(results)} games")
        print("\n" + "=" * 50)
        print("PARSED RESULTS:")
        print("=" * 50)

        # Display results in JSON format
        formatted_results = parser.get_formatted_results()
        print(json.dumps(formatted_results, indent=2, ensure_ascii=False))

        # Display summary statistics
        print("\n" + "=" * 50)
        print("SUMMARY STATISTICS:")
        print("=" * 50)

        total_games = len(formatted_results)
        total_kills_all_games = sum(
            game["total_kills"] for game in formatted_results.values()
        )
        all_players = set()

        for game in formatted_results.values():
            all_players.update(game["players"])

        print(f"📊 Total Games: {total_games}")
        print(f"🎯 Total Kills (all games): {total_kills_all_games}")
        print(f"👥 Unique Players: {len(all_players)}")
        print(f"🏆 Players: {sorted(list(all_players))}")

        # Show top performers
        player_total_kills = defaultdict(int)
        for game in formatted_results.values():
            for player, kills in game["kills"].items():
                player_total_kills[player] += kills

        if player_total_kills:
            top_players = sorted(
                player_total_kills.items(), key=lambda x: x[1], reverse=True
            )
            print(f"\n🥇 Top 5 Players (by total kills):")
            for i, (player, kills) in enumerate(top_players[:5], 1):
                print(f"   {i}. {player}: {kills} kills")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("📋 Make sure the log.txt file exists in the cloud_walk directory.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
