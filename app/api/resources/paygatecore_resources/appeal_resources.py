# АПЕЛЛЯЦИОННЫЕ РЕСУРСЫ
from typing import List


class AppealResources:
    # Статусы апелляции
    valid_appeal_statuses: List[str] = [
        "process",  # в обработке
        "success",  # одобрена
        "canceled"  # отклонена
    ]

    # Поддерживаемые типы файлов для вложений
    valid_file_types: List[str] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "video/mp4",
        "video/mpeg",
        "application/pdf"
    ]

    # Поддерживаемые расширения файлов для вложений
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mpeg", ".pdf"]

    # Максимальный размер загружаемого файла
    max_file_size: int = 10 * 1024 * 1024  # (10 Мб)

    # Максимальное кол-во файлов во влажениях
    max_files_count: int = 10


appeal_res = AppealResources()
