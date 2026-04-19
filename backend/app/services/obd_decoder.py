# backend/app/services/obd_decoder.py
OBD_DB = {
    "P0171": "Система слишком бедная (банк 1)",
    "P0300": "Случайные/множественные пропуски зажигания",
    "P0420": "Эффективность катализатора ниже порога (банк 1)",
}

def decode_obd(code: str) -> str:
    return OBD_DB.get(code.upper(), "Неизвестный код ошибки")