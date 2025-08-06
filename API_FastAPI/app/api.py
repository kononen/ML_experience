# api.py

import uuid
import json
import re
from fastapi import FastAPI, HTTPException, status, Body, BackgroundTasks, Response, Path
import numpy as np

from app.utils.db_utils import (
    set_task_status,
    get_task_status,
    get_task_record,
    any_task_processing
)
from app.utils.log_utils import log_event
from app.utils.inference import run_inference

from app.models import PredictRequest, FEATURE_NAMES  # теперь импортируем и список FEATURE_NAMES

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.post("/predict", status_code=status.HTTP_200_OK)
def predict(
    request: PredictRequest = Body(...),        # FastAPI и Pydantic-валидация
    background_tasks: BackgroundTasks = None
):
    """
    1) request.clients — List[SingleClient], Pydantic-валидация уже отработала.
    2) Проверяем, нет ли сейчас задачи status="processing". Если есть — 503.
    3) Генерируем task_id, сохраняем status="processing", логируем.
    4) Преобразуем List[SingleClient] → List[List[Any]] в порядке FEATURE_NAMES.
    5) background_tasks.add_task(run_inference, task_id, raw_clients_list_of_lists)
    6) Возвращаем {"task_id": <uuid4>, "status": "processing"}.
    """
    if any_task_processing():
        log_event("WARNING", "Получен запрос, но уже есть невыполненная задача")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис сейчас занят. Попробуйте позже."
        )

    task_id = str(uuid.uuid4())
    set_task_status(task_id, status_str="processing", info=None, error_code=None)
    log_event("INFO", f"[{task_id}] Задача поставлена в очередь")

    # --- Сюда попало List[SingleClient], достаём атрибуты в виде обычных dict'ов или атрибутов
    clients_models = request.clients  # List[SingleClient]
    
    # Преобразуем в List[List[Any]], заменяем None → np.nan, чтобы inference смог отработать так же, как раньше
    raw_clients_list_of_lists = []
    for client in clients_models:
        row = []
        for feat in FEATURE_NAMES:
            val = getattr(client, feat)
            # Pydantic уже гарантировал: cat → str|None, num* → float|None (или обязательно float)
            if val is None:
                row.append(np.nan)
            else:
                row.append(val)
        raw_clients_list_of_lists.append(row)

    # Запускаем инференс в фоне
    background_tasks.add_task(run_inference, task_id, raw_clients_list_of_lists)

    return {"task_id": task_id, "status": "processing"}


@app.get("/status/{task_ids}")
def get_status( 
    task_ids: str = Path(..., description="Один или несколько task_id через запятую (пробелы допустимы)")
):
    try:
        raw_ids = [tid.strip() for tid in re.split(r",\s*", task_ids.strip()) if tid.strip()]
        if not raw_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нужно указать хотя бы один task_id"
            )

        response_list = []
        for tid in raw_ids:
            rec = get_task_status(tid)
            if rec["status"] == "not_found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Задача с ID {tid} не найдена"
                )
            response_list.append(rec)

        pretty = json.dumps({"tasks": response_list}, ensure_ascii=False, indent=2)
        return Response(content=pretty, media_type="application/json", status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        log_event("ERROR", f"Ошибка при /status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при получении статусов"
        )


@app.get("/results/{task_ids}")
def get_results(
    task_ids: str = Path(..., description="Один или несколько task_id через запятую (пробелы допустимы)")
):
    try:
        raw_ids = [tid.strip() for tid in re.split(r",\s*", task_ids.strip()) if tid.strip()]
        if not raw_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нужно указать хотя бы один task_id"
            )

        tasks_output = []
        for tid in raw_ids:
            rec = get_task_record(tid)
            print(rec)
            if rec is None:
                tasks_output.append({
                    "task_id": tid,
                    "status": "not_found",
                    "results": None
                })
                continue

            st   = rec["status"]
            info = rec.get("info")
            ec   = rec.get("error_code")

            if st == "processing":
                tasks_output.append({
                    "task_id": tid,
                    "status": "processing",
                    "results": None
                })
            elif st == "error":
                tasks_output.append({
                    "task_id": tid,
                    "status": "error",
                    "error_code": ec,
                    "error_info": info,
                    "results": None
                })
            else:  # completed
                labels_list = info.split(",") if info else []
                tasks_output.append({
                    "task_id": tid,
                    "status": "completed",
                    "results": labels_list
                })

        # Формируем «pretty JSON» вручную, чтобы вложенные списки шли в одну строку
        lines = []
        lines.append("{")
        lines.append('  "tasks": [')

        for idx, task in enumerate(tasks_output):
            lines.append("    {")
            lines.append(f'      "task_id": "{task["task_id"]}",')
            lines.append(f'      "status": "{task["status"]}",')

            if task["status"] == "completed":
                res_str = json.dumps(task["results"], ensure_ascii=False)
                lines.append(f'      "results": {res_str}')
            elif task["status"] == "error":
                ec_str   = json.dumps(task["error_code"], ensure_ascii=False)
                info_str = json.dumps(task["error_info"], ensure_ascii=False)
                lines.append(f'      "error_code": {ec_str},')
                lines.append(f'      "error_info": {info_str},')
                lines.append(f'      "results": null')
            else:
                lines.append(f'      "results": null')

            if idx < len(tasks_output) - 1:
                lines.append("    },")
            else:
                lines.append("    }")

        lines.append("  ]")
        lines.append("}")
        pretty_manual = "\n".join(lines)
        return Response(content=pretty_manual, media_type="application/json", status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        log_event("ERROR", f"Ошибка при /results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при получении результатов"
        )
