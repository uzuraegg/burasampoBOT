from flask import Flask, request, abort
import os
from linebot import (
   LineBotApi, WebhookHandler
)
from linebot.exceptions import (
   InvalidSignatureError
)
from linebot.models import (
   MessageEvent, TextMessage, TextSendMessage, FollowEvent,
   ImageMessage, AudioMessage,
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
 #オウム返しプログラム 
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
   line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text=event.message.text))
 #友達追加時イベント 
@handler.add(FollowEvent)
def handle_follow(event):
   line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text='友達追加ありがとう'))


if __name__ == "__main__":
   port = int(os.getenv("PORT"))
   app.run(host="0.0.0.0", port=port)
