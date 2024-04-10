# from io import BytesIO
# from PIL import Image
# import pandas as pd

# from app import price_data
# from app import get_image
# from app import pattern_detect

# def get_input(message: str):
#     words_list = message.split(", ")

#     sym = words_list[0].upper()
#     start = words_list[1]
#     end = words_list[2]
#     tf = words_list[3]

#     print(sym)
#     print(start)
#     print(end)
#     print(tf)

#     priceData = price_data(ticker=sym, start_date=start, end_date=end, timeframe=tf)
#     getImage = get_image(priceData)
#     image, predict = pattern_detect(source=getImage)

#     bytes_io = BytesIO()
#     image.save(bytes_io, format="png")

#     content=bytes_io.getvalue()

#     pattern = predict[0]["class"]
#     confidence = round(float(predict[0]["conf"][0]), 2)

#     label = {"class" : pattern, "conf" : confidence }

#     return content, label



# # mes = "btc-usd, 2023-01-01, 2023-10-01, 1h"
# # image, label = get_input(mes)
# # x=Image.open(image)
# # x.show()
# # print(label)

# from linebot.v3 import (
#     WebhookHandler
# )

# import os
# from dotenv import load_dotenv
# from linebot.v3.messaging import (
#     Configuration
# )
# import errno

# load_dotenv()

# channel_secret = os.getenv("CHANNEL_SECRET", None)
# channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN", None)

# print(channel_access_token)
# print(channel_secret)
# print("======================================")

# configuration = Configuration(access_token=channel_access_token)
# handler = WebhookHandler(channel_secret)

# print(configuration)
# print(handler)

# line_bot_api = LineBotApi(channel_access_token)
# handler = WebhookHandler(channel_secret)


# def callback(request, x_line_signature):
#     body = request.body()
#     try:
#         handler.handle(body.decode("utf-8"), x_line_signature)
#     except InvalidSignatureError as e:
#         raise print(e)#HTTPException(status_code=400, detail="chatbot handle body error.%s" % e.message)
#     return 'OK'