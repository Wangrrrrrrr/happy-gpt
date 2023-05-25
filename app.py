from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import random
import openai

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
openai.api_key = os.environ['OPENAI_SECRET']

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
        card = {
              "type": "bubble",
              "hero": {
                "type": "image",
                "url": "https://lions-clubs.dev2.rib.tw/static/documents/images/Lions_Clubs_International.png",
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover",
                "action": {
                  "type": "uri",
                  "uri": "http://linecorp.com/"
                }
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "113年度獲獎獅友名單",
                    "weight": "bold",
                    "size": "xl"
                  }
                ]
              },
              "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                      "type": "uri",
                      "label": "公文連結",
                      "uri": "https://lions-clubs.dev2.rib.tw"
                    }
                  }
                ],
                "flex": 0
              }
            }
    msg = event.message.text

    ai_msg = msg[:4].lower()
    if ai_msg == 'hey:':
            # 將第六個字元之後的訊息發送給 OpenAI
            response = openai.Completion.create(
                model='text-davinci-003',
                prompt=msg[4:],
                max_tokens=256,
                temperature=0.5,
                )
            # 接收到回覆訊息後，移除換行符號
            reply_msg = TextSendMessage(text=response["choices"][0]["text"].replace('\n',''))
    
    if msg == "午餐吃什麼":
        lunch_options = ['便當', '麵類', '飯類', '燉飯', '三明治']
        #message = TextSendMessage(text=event.message.text)
        reply_msg = TextSendMessage(text=random.choice(lunch_options))
    line_bot_api.reply_message(event.reply_token, reply_msg)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
