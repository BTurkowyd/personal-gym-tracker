import requests
import random

url = "http://localhost:8000/plot"

data = {
    "plot_type": "scatter",  # can be "scatter", "bar", or "line"
    "x": [random.randint(0, 10) for _ in range(10)],
    "y": [random.randint(0, 10) for _ in range(10)],
    "title": "Random Scatter Plot",
    "seaborn": True,
}

response = requests.post(url, json=data)
if response.status_code == 200:
    with open("plot.png", "wb") as f:
        f.write(response.content)
    print("Plot saved as plot.png")
else:
    print("Error:", response.text)
