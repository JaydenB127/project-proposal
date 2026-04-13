import requests
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

BASE_URL = "http://localhost:8000"
API_KEY = "324d6266-31b0-48d9-b794-d69e5b7d9a79"

headers = {
    "X-API-Key": API_KEY
}

# ======================
# LOAD DATA CỦA BẠN
# ======================
df = pd.read_csv("BTC_USD_daily_data.csv")  # <-- đổi đúng tên file

# lấy giá đóng cửa
prices = df["Close"].values.astype(np.float32)

# normalize
mean = prices.mean()
std = prices.std()
prices = (prices - mean) / std

# ======================
# TẠO DATASET CHO LSTM
# ======================
def create_sequences(data, seq_length=20):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

X, y = create_sequences(prices)

X = torch.tensor(X).unsqueeze(-1)  # (batch, seq, 1)
y = torch.tensor(y)

# ======================
# MODEL LSTM
# ======================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out).squeeze()

model = LSTMModel()
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ======================
# TẠO RUN
# ======================
resp = requests.post(
    f"{BASE_URL}/api/v1/runs",
    json={"name": "btc_real_data", "experiment": "custom_dataset"},
    headers=headers
)

res = resp.json()
print(res)  # thêm dòng này để debug

run_id = res.get("data", {}).get("id") or res.get("id")
print(f"Run ID: {run_id}")

# ======================
# TRAIN
# ======================
epochs = 10
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()

    preds = model(X)
    loss = loss_fn(preds, y)

    loss.backward()
    optimizer.step()

    loss_value = loss.item()

    print(f"epoch {epoch+1}/{epochs} loss={loss_value:.4f}")

    # log metric
    requests.post(
        f"{BASE_URL}/api/v1/runs/{run_id}/metrics",
        json={
            "metrics": [
                {"key": "train_loss", "value": loss_value, "step": epoch+1}
            ]
        },
        headers=headers
    )

# ======================
# FINISH
# ======================
requests.post(
    f"{BASE_URL}/api/v1/runs/{run_id}/finish",
    headers=headers
)

print("✅ DONE - Check dashboard: http://localhost:5173")