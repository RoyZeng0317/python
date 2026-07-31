def format_ohms(ohms: float) -> str:
    """把歐姆數值格式化成 Ω / kΩ / MΩ，方便閱讀。"""
    if ohms >= 1_000_000:
        return f"{ohms / 1_000_000:.4g} MΩ"
    elif ohms >= 1_000:
        return f"{ohms / 1_000:.4g} kΩ"
    # elif ohms >= 
    return f"{ohms:.4g} Ω"