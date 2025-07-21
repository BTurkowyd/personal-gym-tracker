from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import seaborn as sns
import matplotlib.pyplot as plt
import io
import pandas as pd
import uvicorn

app = FastAPI()


@app.post("/plot")
async def plot(request: Request):
    data = await request.json()
    plot_type = data.get("plot_type", "scatter")
    x = data.get("x", [])
    y = data.get("y", [])
    title = data.get("title", "Plot")

    df = pd.DataFrame({"x": x, "y": y})

    plt.figure(figsize=(6, 4))
    if plot_type == "scatter":
        sns.scatterplot(data=df, x="x", y="y")
    elif plot_type == "bar":
        sns.barplot(data=df, x="x", y="y")
    elif plot_type == "line":
        sns.lineplot(data=df, x="x", y="y")
    plt.title(title)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
