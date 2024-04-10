import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import shutil
from ultralytics import YOLO
from PIL import Image
import io

model_file_path = os.path.join(os.path.dirname(__file__), 'model', 'best.pt')


def price_data(ticker, start_date, end_date, timeframe="1h"):
  # fetch historical price data
  data = yf.download(ticker, start=start_date, end=end_date, interval=timeframe)
  return data

def get_image(data: pd.DataFrame):
    # Set the backend to 'Agg' (non-interactive)
    plt.switch_backend('Agg')

    # plot candlestick chart
    fig, ax = mpf.plot(data.head(72), type="candle", style="yahoo", ylabel="", ylabel_lower="", axtitle="", figsize=(6.4, 6.4), returnfig=True)

    # convert chart to image
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    buf.seek(0)

    image = Image.open(buf)

    return image

def pattern_detect(source, confidence=0.5):
    """
    model: the trained object detection model (.pt file)
    source: image inputs
    confidence: object confidence threshold for detection
    """

    # model initialize
    model = YOLO(model_file_path)

    # model inference
    results = model.predict(source=source, conf=confidence)

    pred = []

    for result in results:
        names = result.names
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
          pred_result = {
            "xyxy": box.xyxy.tolist()[0],
            "conf": round(box.conf[0], 2),
            "class": names[box.cls[0]]
          }

          pred.append(pred_result)

    im_array = results[0].plot()  # plot a BGR numpy array of predictions
    im = Image.fromarray(im_array[:, :, ::-1])  # RGB PIL image
    buf = io.BytesIO()
    im.save(buf, format="png")

    image = Image.open(buf)

    if len(pred) == 0:
      return image, "No detections"
    else:
      return image, pred


