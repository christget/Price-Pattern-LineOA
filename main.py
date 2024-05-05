from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from io import BytesIO
import os
import random
import time
from pathlib import Path
import tempfile
import cv2
import errno
import base64
import hashlib
import hmac

from app import price_data
from app import get_image
from app import pattern_detect

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

from dotenv import load_dotenv

app = FastAPI()

@app.get("/")
def helloWorld():
    return {"Hello" : "World"}


@app.post("/pattern_detect")
def image_detect(message: str):
    words_list = message.split(", ")

    sym = words_list[0].upper()
    start = words_list[1]
    end = words_list[2]
    tf = words_list[3]

    priceData = price_data(ticker=sym, start_date=start, end_date=end, timeframe=tf)
    getImage = get_image(priceData)
    image, predict = pattern_detect(source=getImage)

    bytes_io = BytesIO()
    image.save(bytes_io, format="png")

    return Response(content=bytes_io.getvalue(), media_type="image/png", headers= {"classification-results": str(predict)})


load_dotenv()

channel_access_token = "yLKqKgW9bDBrCTHMJRjA+ocCpQ3rBj26OMzgZNTNOgvDT2COMiGOaFCCeeZq8jdgxSSA/UloAfVSlxChspd+QUGNXzJNt4HQHvgLg2ap+zrW9zTctiA7uxR5bqeGzGS81ZMFtAQvaC+b3234S3t+tgdB04t89/1O/w1cDnyilFU="
channel_secret = "bd52780d26db0e6e185cbe5ce70f04f3"

# channel_secret = os.getenv("CHANNEL_SECRET")
# channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)


# @app.post("/callback")
# async def callback(request: Request):
#     body = await request.body()
#     signature = request.headers['X-Line-Signature']
    
#     try:
#         handler.handle(body.decode("utf-8"), signature)
#     except InvalidSignatureError as e:
#         raise HTTPException(status_code=400, detail="Invalid signature: %s" % e.message)
    
#     return 'OK'

@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    body_str = body.decode("utf-8")
    signature = request.headers['X-Line-Signature']
    
    # Compute HMAC-SHA256 digest
    hash = hmac.new(channel_secret.encode('utf-8'), body, hashlib.sha256).digest()
    computed_signature = base64.b64encode(hash).decode()

    # Compare X-Line-Signature with the computed signature
    if signature != computed_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process the request here after validating the signature...
    
    return 'OK'

# function for create tmp dir for download content
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Directories
save_dir = 'static/tmp/'

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    ## event.message.text คือข้อความที่เขาพิมพ์มา
    text = event.message.text
    try:
        words_list = text.split(", ")
        sym = words_list[0].upper()
        start = words_list[1]
        end = words_list[2]
        tf = words_list[3]
    except Exception:
        start_word = ['สวัสดีหัวไหล่ ','Hello There']
        response_word = random.choice(start_word) + "😎 ส่งข้อความเข้ามารูปแบบดังนี้ aapl, 2023-09-01, 2023-10-01, 1h"
        with ApiClient(configuration) as api_clients:
            line_bot_api = MessagingApi(api_clients)
            messages = [TextMessage(text=response_word)]
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    replyToken= event.reply_token,
                    messages= messages
                )
            )
            
    try:
        priceData = price_data(ticker=sym, start_date=start, end_date=end, timeframe=tf)
        getImage = get_image(priceData)
        image, predict = pattern_detect(source=getImage)
    except Exception:
        start_word = ['อุ๊ปส​์!','Ops!']
        response_word = random.choice(start_word) + " ระบบเกิดข้อผิดพลาด โปรดลองใหม่ภายหลัง 😵‍💫"
        with ApiClient(configuration) as api_clients:
            line_bot_api = MessagingApi(api_clients)
            messages = [TextMessage(text=response_word)]
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    replyToken= event.reply_token,
                    messages= messages
                )
            )

    # bytes_io = BytesIO()
    # image.save(bytes_io, format="png")

    pattern = predict[0]["class"]
    confidence = round(float(predict[0]["conf"]), 2)

    results =  {"class" : pattern, "conf" : confidence }

    # try:
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix="png" + '-', delete=False) as tf:
        # Convert PIL Image to bytes and write to temporary file
        image.save(tf, format="PNG")
        tempfile_path = tf.name

        # content = bytes_io.getvalue()
        # with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix="png" + '-', delete=False) as tf:
        #     for chunk in image.iter_content():
        #         tf.write(chunk)
        #     tempfile_path = tf.name

    dist_path = tempfile_path + '.' + "png"
    os.rename(tempfile_path, dist_path)

    # Read the image using OpenCV
    im = cv2.imread(dist_path)
    im0 = im.copy()

    save_path = str(save_dir + os.path.basename(tempfile_path) + '_result.' + "png")
    cv2.imwrite(save_path, im0)

    # Assuming Request is an imported class or object
    url = Request.url_for('/', save_path)

    #url = request.url_root + '/' + save_path

    # im_file = open(dist_path, "rb")
    # im = cv2.imread(im_file)
    # im0 = im.copy()

    # save_path = str(save_dir + os.path.basename(tempfile_path) + '_result.' + "png") 
    # cv2.imwrite(save_path, im0)

    # url = Request.url_for(save_path) #+ '/' + save_path
    with ApiClient(configuration) as api_clients:
        line_bot_api = MessagingApi(api_clients)
        text_message = TextMessage(text='Object detection result:')
    
        # Assuming ImageMessage expects a single URL argument
        image_message = ImageMessage(originalContentUrl=url, previewImageUrl=url)
        
        messages = [text_message, image_message]
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                replyToken= event.reply_token,
                messages= messages
            )
        )
        # line_bot_api.reply_message(
        #     ReplyMessageRequest(
        #         event.reply_token, 
        #         [
        #         TextMessage(text='Object detection result:'),
        #         ImageMessage(url,url)
        #         ]
        #     )
        # )
    # except Exception:
    #     start_word = ['อุ๊ปส​์!','Ops!']
    #     response_word = random.choice(start_word) + " ระบบเกิดข้อผิดพลาด โปรดลองใหม่ภายหลัง 🤢"
    #     with ApiClient(configuration) as api_clients:
    #         line_bot_api = MessagingApi(api_clients)
    #         messages = [TextMessage(text=response_word)]
    #         line_bot_api.reply_message(
    #             ReplyMessageRequest(
    #                 replyToken= event.reply_token,
    #                 messages= messages
    #             )
    #         )

# create tmp dir for download content
make_static_tmp_dir()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)