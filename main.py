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
   ImageSendMessage, LocationSendMessage, LocationMessage
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
    PHOTO_URL_BASE = "https://psf-ikoma-burasampo-datastore.s3-ap-northeast-1.amazonaws.com/public/posts/photos"
    SEARCH_DISTANCE = 0.01

    user_lat = event.message.latitude
    user_lng = event.message.longitude

    # timelineAPIから投稿を取得
    response = requests.post(
        'https://api.ikoma.burasampo.jp/map/search/',
        json.dumps({
          "user_id": 258,
          "amount": 1,
            "location_lat_south": user_lat - SEARCH_DISTANCE,
            "location_lat_north": user_lat + SEARCH_DISTANCE,
            "location_lng_west": user_lng - SEARCH_DISTANCE,
            "location_lng_east": user_lng + SEARCH_DISTANCE
            }),
        headers={'Content-Type': 'application/json'})
    for panel in response.json()['posts']:
        for post in panel:
            if('photo_url' in post):
                title = post['title']
                comment = post['comment']
                photo_url = post['photo_url']
                user_name = post['user_name']

                text_message = TextSendMessage(
                    text="投稿者：{}\nタイトル：{}\nコメント：{}".format(user_name, title, comment)
                )
                image_message = ImageSendMessage(
                    original_content_url=f"https://psf-ikoma-burasampo-datastore.s3-ap-northeast-1.amazonaws.com/public/posts/photos/original/{photo_url}",
                    preview_image_url=f"https://psf-ikoma-burasampo-datastore.s3-ap-northeast-1.amazonaws.com/public/posts/photos/thumbnail/{photo_url}",
                )

                line_bot_api.reply_message(event.reply_token, [text_message,image_message])
                return
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='投稿は見つかりませんでした'))




#友達追加時イベント
@handler.add(FollowEvent)
def handle_follow(event):
   line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text='友達追加ありがとう！'))


if __name__ == "__main__":
   port = int(os.getenv("PORT"))
   app.run(host="0.0.0.0", port=port)
