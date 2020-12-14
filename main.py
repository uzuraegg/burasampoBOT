from flask import Flask, request, abort
import requests, json
import os
from linebot import (
   LineBotApi, WebhookHandler
)
from linebot.exceptions import (
   InvalidSignatureError
)
from linebot.models import (
   MessageEvent, TextMessage, TextSendMessage, FollowEvent,
   ImageMessage, LocationMessage,
)

app = Flask(__name__)
 #環境変数取得 
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
 #APIの設定 
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
 #テスト用 
@app.route("/")
def hello_world():
   return "hello world!"
 #Webhookからのリクエストをチェック 
@app.route("/callback", methods=['POST'])
def callback():
   signature = request.headers['X-Line-Signature']
   body = request.get_data(as_text=True)
   app.logger.info("Request body: " + body)
   try:
       handler.handle(body, signature)
   except InvalidSignatureError:
       abort(400)
   return 'OK'
 #返信プログラム
@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    lat = event.message.latitude
    lon = event.message.longitude

    # timelineAPIから投稿を取得
    response = requests.post(
        'https://api.ikoma.burasampo.jp/map/search/',
        json.dumps({
          "user_id": 258,
          "amount": 1,
            "location_lat_south": lat + 0.25,
            "location_lat_north": lat - 0.25,
            "location_lng_west": lon + 0.25,
            "location_lng_east": lon - 0.25
            }),
        headers={'Content-Type': 'application/json'})

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response.json()))


#友達追加時イベント
@handler.add(FollowEvent)
def handle_follow(event):
   line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text='友達追加ありがとう！'))


if __name__ == "__main__":
   port = int(os.getenv("PORT"))
   app.run(host="0.0.0.0", port=port)
