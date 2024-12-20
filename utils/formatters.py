def format_time(seconds: int) -> str:
    if seconds > 3600:
        return f"{seconds // 3600}ч {(seconds % 3600) // 60}м"
    elif seconds > 60:
        return f"{seconds // 60}м {seconds % 60}с"
    return f"{seconds}с"

def format_progress_message(processed: int, total: int, time_left: int) -> str:
    progress = processed / total if total > 0 else 0
    filled_blocks = int(progress * 10)
    empty_blocks = 10 - filled_blocks
    progress_bar = "▰" * filled_blocks + "▱" * empty_blocks

    return (
        f"⏳ Обработка файла...\n"
        f"{progress_bar} {(progress*100):.1f}%\n"
        f"📊 Обработано: {processed}/{total}\n"
        f"⏱ Осталось: {format_time(time_left)}"
    )
