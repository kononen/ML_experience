# utils/inference.py

import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.utils.db_utils import set_task_status
from app.utils.log_utils import log_event
#from app.trained_models import SimpleClassifier  # <-- именно так

N_FEATURES = 5

# Проверяем, доступен ли MPS (Mac GPU)
if torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(N_FEATURES, 8), # если N_FEATURES=20, будет 20 входов
            nn.ReLU(),
            nn.Linear(8, 2)
        )
    def forward(self, x):
        return self.fc(x)

# Пути к вашим .pth-файлам
MODEL_M_PATH = "trained_models/model_m.pth"
MODEL_K_PATH = "trained_models/model_k.pth"

model_m = SimpleClassifier().to(device)
model_m.load_state_dict(torch.load(MODEL_M_PATH, map_location=device))
model_m.eval()

model_k = SimpleClassifier().to(device)
model_k.load_state_dict(torch.load(MODEL_K_PATH, map_location=device))
model_k.eval()

def run_inference(task_id: str, raw_clients: list):
    """
    1) Преобразуем raw_clients → numpy, LabelEncoding + StandardScaler.
    2) Запускаем инференс двух моделей.
    3) Формируем список final_labels = ["n","g","b",...].
    4) Если всё успешно → set_task_status(task_id, "completed", info="n,g,b,...", error_code=None).
    5) Если поймали исключение → set_task_status(task_id, "error", info="<текст ошибки>", error_code="500").
    """
    try:
        log_event("INFO", f"[{task_id}] Начата фоновая обработка (inference).")

        # 1) Преобразование raw_clients в numpy и reshaping
        data = np.array(raw_clients, dtype=object)
        if data.ndim == 1:
            data = data.reshape(1, -1)

        # 2) Предполагаем, что колонка 0 — категориальная
        categorical_columns = [0]
        data = np.where(pd.isnull(data), 0, data)  # None/NaN → 0

        for col_idx in categorical_columns:
            le = LabelEncoder()
            col_values = data[:, col_idx].astype(str)
            try:
                encoded = le.fit_transform(col_values)
            except Exception as e:
                raise ValueError(f"Не удалось закодировать категорию в колонке {col_idx}: {e}")
            data[:, col_idx] = encoded

        # 3) Перевод в float32
        try:
            data_float = data.astype(np.float32)
        except Exception as e:
            raise ValueError(f"Не удалось преобразовать в float32: {e}")

        # 4) Масштабирование
        scaler = StandardScaler()
        try:
            data_scaled = scaler.fit_transform(data_float)
        except Exception as e:
            raise ValueError(f"Не удалось масштабировать данные: {e}")

        # 5) Инференс
        inputs_tensor = torch.tensor(data_scaled, dtype=torch.float32).to(device)
        with torch.no_grad():
            outputs_m = model_m(inputs_tensor)
            _, preds_m = torch.max(outputs_m, dim=1)
            preds_m = preds_m.cpu().numpy()

            outputs_k = model_k(inputs_tensor)
            _, preds_k = torch.max(outputs_k, dim=1)
            preds_k = preds_k.cpu().numpy()

        # 6) Формируем финальные метки
        final_labels = []
        for m_val, k_val in zip(preds_m, preds_k):
            if (m_val == 0 and k_val == 0) or (m_val == 1 and k_val == 1):
                final_labels.append("n")
            elif (m_val == 1 and k_val == 0):
                final_labels.append("g")
            elif (m_val == 0 and k_val == 1):
                final_labels.append("b")
            else:
                final_labels.append("unknown")

        # 7) Сохраняем в БД: status="completed", info="n,g,b,...", error_code=None
        csv_labels = ",".join(final_labels)
        set_task_status(
            task_id=task_id,
            status_str="completed",
            info=csv_labels,
            error_code=None
        )
        log_event("INFO", f"[{task_id}] Завершён инференс. Метки: {csv_labels}")

    except Exception as e:
        # 8) При ошибке: status="error", info="<текст ошибки>", error_code="500"
        err_text = str(e)
        set_task_status(
            task_id=task_id,
            status_str="error",
            info=err_text,
            error_code="500"
        )
        log_event("ERROR", f"[{task_id}] Ошибка при инференсе: {err_text}")
