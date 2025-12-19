# # models.py

# app/models.py

from typing import Any, List, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator

FEATURE_NAMES = ["cat", "num1", "num2", "num3", "num4"]

# Для числовых полей
NUMERIC_FIELDS = ["num1", "num2", "num3", "num4"]
NUMERIC_BOUNDS = {
    "num2": (0.0, 200.0),
}

# Для полей с **только** нижней границей ≥ 0
NUMERIC_LOWER_ONLY = {"num1", "num3"}

# Для категориального поля
CATEGORICAL_FIELDS = ["cat"]
CATEGORICAL_VALUES = {
    "cat": {"A", "B", "C"},
}


class SingleClient(BaseModel):
    cat: Optional[str] = Field(None, description="Категориальный признак cat")
    num1: Optional[float] = Field(None, description="Число num1 (любой)")
    num2: Optional[float] = Field(None, description="Число num2 (0 ≤ num2 ≤ 200)")
    num3: Optional[float] = Field(None, description="Число num3 (-10 ≤ num3 ≤ 10)")
    num4: Optional[float] = Field(None, description="Число num4 (любой)")

    # 1) Валидатор для всех числовых полей
    @field_validator(*NUMERIC_FIELDS, mode="before")
    def check_numeric_or_null(cls, v: Any, info) -> Any:
        """
        Этот валидатор применится сразу ко всем полям, указанных в NUMERIC_FIELDS.
        - Если v is None → возвращаем None.
        - Пытаемся привести в float.
        - Если у поля указан диапазон в NUMERIC_BOUNDS → проверяем.
        """
        # Если прислали JSON null → v == None
        if v is None:
            return None

        # Попробуем привести к float
        try:
            f = float(v)
        except (TypeError, ValueError):
            raise ValueError(f"Поле '{info.field_name}' должно быть числом или null, а пришло {v!r}")

        # Проверим диапазон, если указан
        # Специально: для тех полей, где только нижняя граница
        if info.field_name in NUMERIC_LOWER_ONLY:
            if f < 0:
                raise ValueError(f"Поле '{info.field_name}' = {f} должно быть ≥ 0")
        # Для остальных полей с жёстким диапазоном (num2 и, если добавите, другие)
        elif info.field_name in NUMERIC_BOUNDS:
            lo, hi = NUMERIC_BOUNDS[info.field_name]
            if not (lo <= f <= hi):
                raise ValueError(f"Поле '{info.field_name}' = {f} вне диапазона [{lo}, {hi}]")

    # 2) Валидатор для всех категориальных полей
    @field_validator(*CATEGORICAL_FIELDS, mode="before")
    def check_categorical_or_null(cls, v: Any, info) -> Any:
        """
        Валидатор для всех полей, перечисленных в CATEGORICAL_FIELDS.
        - Если v is None → возвращаем None.
        - Иначе проверяем, что это строка и v ∈ CATEGORICAL_VALUES[field_name].
        """
        if v is None:
            return None

        if not isinstance(v, str):
            raise ValueError(f"Поле '{info.field_name}' должно быть строкой или null, а пришло {type(v).__name__}")

        allowed = CATEGORICAL_VALUES[info.field_name]
        if v not in allowed:
            raise ValueError(f"Поле '{info.field_name}'={v!r} недопустимо; должно быть одной из {allowed}")
        return v


class PredictRequest(BaseModel):
    clients: List[SingleClient]

    @field_validator("clients", mode="before")
    def check_clients_list(cls, v: Any) -> Any:
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError("Поле 'clients' должно быть непустым списком JSON-объектов")
        return v




# from typing import Any, List, Optional
# import numpy as np
# from pydantic import BaseModel, validator, ValidationError, root_validator, Field

# # # ------------------------------------------------------------------------------------------------
# # # Список полей в том порядке, который ожидает модель SimpleClassifier
# # FEATURE_NAMES = ["cat", "num1", "num2", "num3", "num4"]
# # # Множество допустимых значений для категориального признака 'cat'
# # CATEGORICAL_VALUES = {"A", "B", "C"}
# # # Диапазон для числового признака num2
# # NUM2_BOUNDS = (0.0, 200.0)
# # # ------------------------------------------------------------------------------------------------

# FEATURE_NAMES = ["cat", "num1", "num2", "num3", "num4"]
# # Определяем, какие поля – числовые, и для каких из них нужен диапазон
# NUMERIC_FIELDS = ["num1", "num2", "num3", "num4"]#, "num5", …, "num20"]
# NUMERIC_BOUNDS = {
#     "num2": (0.0, 200.0),
#     "num3": (-10.0, 10.0),
#     # и т. д. для тех, у кого есть явный диапазон
# }

# # Допустимые значения для категориальных
# CATEGORICAL_FIELDS = ["cat"]#, "cat2", "cat3"]
# CATEGORICAL_VALUES = {
#     "cat": {"A", "B", "C"},
#    # "cat2": {"X", "Y", "Z"},
#    # "cat3": {"M", "N"},
# }

# class SingleClient(BaseModel):
#     """
#     Описание одного клиента: словарь с ключами FEATURE_NAMES.
#       - cat: строка "A"|"B"|"C" или None (NaN)
#       - num1: float (любой)
#       - num2: float в диапазоне [0.0, 200.0]
#       - num3: float или None (NaN) [-10, 10]
#       - num4: float (любой)
#     """
#     # cat: Optional[str] = Field(None, description="Категориальный признак: A|B|C или null")
#     # num1: float = Field(..., description="Числовой признак num1 (float)")
#     # num2: float = Field(..., ge=NUM2_BOUNDS[0], le=NUM2_BOUNDS[1], description="Числовой признак num2 (0 ≤ num2 ≤ 200)")
#     # num3: Optional[float] = Field(None, description="Числовой признак num3 (может быть null)")
#     # num4: float = Field(..., description="Числовой признак num4 (float)")

#     # @validator("cat")
#     # def check_cat(cls, v):
#     #     if v is None:
#     #         return None
#     #     if v not in CATEGORICAL_VALUES:
#     #         raise ValueError(f"Поле 'cat' должно быть одной из {CATEGORICAL_VALUES} или null, а пришло {v!r}")
#     #     return v

#     # @validator("num3", pre=True)
#     # def allow_nan_num3(cls, v):
#     #     # Если приходит что-то, преобразуем в float или None
#     #     if v is None:
#     #         return None
#     #     try:
#     #         f = float(v)
#     #         return f
#     #     except Exception:
#     #         raise ValueError(f"Поле 'num3' должно быть числом или null, а пришло {v!r}")

#     # # num1 и num4 уже проверяются как float автоматически; при желании можно добавить дополнительные валидации aquí.

#     cat: Optional[str] = Field(None, description="Категориальный признак cat")
#     # cat2: Optional[str] = Field(None, description="Категториальный признак cat2")
#     # cat3: Optional[str] = Field(None, description="Категориальный признак cat3")

#     num1: Optional[float] = Field(None, description="Число num1 (любой)")
#     num2: Optional[float] = Field(None, description="Число num2 (0 ≤ num2 ≤ 200)")
#     num3: Optional[float] = Field(None, description="Число num3 (-10 ≤ num3 ≤ 10)")
#     num4: Optional[float] = Field(None, description="Число num4 (любой)")
    
#     # 1) Валидатор для всех числовых полей (вместо многострочных дублирующих функций)
#     @validator(*NUMERIC_FIELDS, pre=True)
#     def check_numeric_or_null(cls, v, field):
#         """
#         Этот валидатор применится сразу ко всем полям, названным в NUMERIC_FIELDS.
#         - Если v is None → возвращаем None (пустое значение допускается).
#         - Пытаемся привести в float. 
#         - Если у этого поля указан диапазон в NUMERIC_BOUNDS → проверяем, не выходит ли за пределы.
#         """
#         if v is None:
#             return None
#         try:
#             f = float(v)
#         except (TypeError, ValueError):
#             raise ValueError(f"Поле '{field.name}' должно быть числом или null, а пришло {v!r}")
#         # Проверяем диапазон, если он задан
#         if field.name in NUMERIC_BOUNDS:
#             lo, hi = NUMERIC_BOUNDS[field.name]
#             if not (lo <= f <= hi):
#                 raise ValueError(f"Поле '{field.name}' = {f} вне диапазона [{lo}, {hi}]")
#         return f

#     # 2) Валидатор для всех категориальных полей
#     @validator(*CATEGORICAL_FIELDS, pre=True)
#     def check_categorical_or_null(cls, v, field):
#         """
#         Этот валидатор будет вызван сразу для всех полей, перечисленных в CATEGORICAL_FIELDS.
#         - Если v is None → возвращаем None.
#         - Иначе проверяем, что v in CATEGORICAL_VALUES[field.name].
#         """
#         if v is None:
#             return None
#         if not isinstance(v, str):
#             raise ValueError(f"Поле '{field.name}' должно быть строкой или null, а пришло {type(v).__name__}")
#         allowed = CATEGORICAL_VALUES[field.name]
#         if v not in allowed:
#             raise ValueError(f"Поле '{field.name}'={v!r} недопустимо; должно быть одной из {allowed}")
#         return v
        

# class PredictRequest(BaseModel):
#     """
#     Ожидаем JSON вида:
#     {
#       "clients": [
#          {"cat": "A", "num1": 0.0, "num2": 10.0, "num3": null, "num4": 5.0},
#          {"cat": "B", "num1": -50.5, "num2": 150.0, "num3": 1.0, "num4": 100.0},
#          ...
#       ]
#     }
#     - clients: непустой список словарей SingleClient
#     """
#     clients: List[SingleClient]

#     # @validator("clients", pre=True)
#     # def check_clients_type(cls, v):
#     #     if not isinstance(v, list) or len(v) == 0:
#     #         raise ValueError("Поле 'clients' должно быть непустым списком JSON-объектов")
#     #     return v

#     # @validator("clients")
#     # def validate_each_client(cls, clients_list: List[SingleClient]):
#     #     # Pydantic сам вызывает валидацию для каждого SingleClient, поэтому здесь ничего доп. не делаем
#     #     return clients_list

#     @validator("clients", pre=True)
#     def check_clients_list(cls, v):
#         if not isinstance(v, list) or len(v) == 0:
#             raise ValueError("Поле 'clients' должно быть непустым списком JSON-объектов")
#         return v
