"""
Example code showing how to create an echo bot by using ngrok and webhooks
"""

import yaml
from webexteamssdk import WebexTeamsAPI
from pyngrok import ngrok
from flask import Flask, request

with open('variables.yaml', 'r') as file:
    variables = yaml.safe_load(file)


class Bot:

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api = WebexTeamsAPI(access_token=self.bot_token)
        self.id = self.api.people.me().id

        self.https_tunnel = None
        self.webhook = None

    def create_webhook(self) -> None:
        self.webhook = self.api.webhooks.create(
            name="ephemeral_bot_tunnel",
            targetUrl=self.https_tunnel.public_url + "/messages",
            resource="messages",
            event="created",
            filter="roomType=direct"
        )

    def delete_webhook(self) -> None:
        self.api.webhooks.delete(self.webhook.id)

    def start_tunnel(self) -> None:
        self.https_tunnel = ngrok.connect(bind_tls=True, addr="http://localhost:5002")

    def stop_tunnel(self) -> None:
        ngrok.disconnect(self.https_tunnel.api_url)

    def startup(self) -> None:
        self.start_tunnel()
        self.create_webhook()

    def teardown(self) -> None:
        self.delete_webhook()
        self.stop_tunnel()


app = Flask(__name__)


@app.route("/messages", methods=['POST'])
def index():
    if request.method == 'POST':

        payload = request.get_json()

        # Ignore own bot messages
        if payload['actorId'] == bot.id:
            return 'success'

        message_id = payload["data"]["id"]
        room_id = payload["data"]["roomId"]

        # Load message
        message = bot.api.messages.get(message_id)

        # Echo back the message
        bot.api.messages.create(roomId=room_id, text=f"You said {message.text}")

        return 'success'


if __name__ == "__main__":

    bot = Bot(variables["bot_token"])
    bot.startup()

    app.run(port=5002)  # can not use debug due to ngrok error, have to fix later
