import json
import urllib.error
import urllib.request


class GameClient:

    def __init__(self, server_url="http://127.0.0.1:8000"):

        self.server_url = server_url
        self.player_id = None
        self.nickname = None

    #Send request to server
    def send_request(self, endpoint, method="GET", data=None):

        url = self.server_url + endpoint

        headers = {
            "Content-Type": "application/json"
        }

        body = None

        if data is not None:
            body = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method
        )

        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.URLError:
            print("Cannot connect to server.")
            return None

        except (TimeoutError, OSError):
            print("Server request failed or timed out.")
            return None

        except json.JSONDecodeError:
            print("Invalid server response.")
            return None

    #Register player
    def register_player(self, nickname):

        data = {"nickname": nickname}
        response = self.send_request("/players/register", "POST", data)

        if response:
            self.player_id = response.get("player_id")
            self.nickname = nickname
            return True

        return False

    #Submit player score
    def submit_score(self, score, ship_name=None):

        if self.player_id is None:
            print("Player is not registered.")
            return False

        data = {
            "player_id": self.player_id,
            "score": score,
            "ship_name": ship_name
        }

        response = self.send_request("/scores", "POST", data)
        return response is not None

    #Get leaderboard
    def get_leaderboard(self):

        response = self.send_request("/leaderboard", "GET")

        if response:
            return response.get("leaderboard", [])

        return []
