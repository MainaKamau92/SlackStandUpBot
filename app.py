import os
import logging
from slack_bolt import App


logging.basicConfig(level=logging.DEBUG)

def fetch_reply_blocks(last_24, next_24, blockers, slack_id):
    return {
	"blocks": [
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f":tada: :tada: <@{slack_id}>! just posted their stand up"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*What you accomplished last 24 hours* :crescent_moon: "
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"{last_24}"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*What you'll be working on next 24 hours :crystal_ball:*"
			}
		},
        {
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"{next_24}"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Blockers* :no_entry_sign:"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"{blockers}"
			}
		}
	]
}
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SIGNIN_SECRET"),
)


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    next()


# Step 5: Payload is sent to this endpoint, we extract the `trigger_id` and call views.open
@app.command("/standup")
def handle_command(body, ack, client, logger):
    logger.info(body)
    ack()

    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "callback_id": "standup-bot",
	"title": {
		"type": "plain_text",
		"text": "Daily Stand Up"
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit"
	},
	"blocks": [
		{
			"type": "input",
            "block_id": "last_24",
			"element": {
				"type": "plain_text_input",
				"action_id": "yesterday",
				"multiline": True,
				"placeholder": {
					"type": "plain_text",
					"text": "What did you do last 24 hours?"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "What did you do yesterday?"
			}
		},
		{
			"type": "input",
            "block_id": "next_24",
			"element": {
				"type": "plain_text_input",
				"action_id": "today",
				"multiline": True,
				"placeholder": {
					"type": "plain_text",
					"text": "What will you do today?"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "What are you dong today?"
			}
		},
		{
			"type": "input",
            "block_id": "blockers",
			"element": {
				"type": "plain_text_input",
				"action_id": "blockers",
				"multiline": True,
				"placeholder": {
					"type": "plain_text",
					"text": "What are the blockers?"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "Any Blockers?"
			}
		}
	],
	"type": "modal"
},
    )
    logger.info(res)


@app.view("standup-bot")
def view_submission(ack, body, logger, client):
    ack()
    last_24 = body["view"]["state"]["values"]["last_24"]["yesterday"]["value"]
    next_24 = body["view"]["state"]["values"]["next_24"]["today"]["value"]
    blockers = body["view"]["state"]["values"]["blockers"]["blockers"]["value"]
    slack_id = body["user"]["id"]
    blocks = fetch_reply_blocks(last_24, next_24, blockers, slack_id)
    client.chat_postMessage(
        channel="XXXXXXXX",
        blocks=blocks["blocks"],
    )
    logger.info(body)

if __name__ == "__main__":
    app.start(3000)
