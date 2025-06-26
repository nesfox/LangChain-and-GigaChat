"""
Скачивает письма из mail-почты за последние N суток,
включая тексты и все вложения, через IMAP-SSL.

Требуется «Пароль приложения» mail-почты (web-интерфейс → Аккаунт → Безопасность
→ Пароли приложений).
IMAP-доступ должен быть включён (Почта → Все настройки → Почтовые программы).

1. Подключается к почтовому ящику через IMAP с SSL
2. Скачивает письма за указанное количество дней
3. Сохраняет тексты писем и все вложения
4. Требует специальных настроек в почтовом аккаунте
"""
from dataclasses import dataclass
import imaplib
import email
from email.header import decode_header
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import TypeAlias
from dotenv import find_dotenv, load_dotenv
from langchain_core.tools import tool # декоратор для интеграции с LangChain


load_dotenv(find_dotenv())
# Путь для сохранения вложений (указываете любой,
# где удобно хранить собранные файлы)
SAVE_ATTACHMENTS_DIRECTORY = "C:/Users/smoly/SBER_GIGA/LangChain-and-GigaChat/attachments"


Filename: TypeAlias = str  # псевдоним имя файла, в котором хранится аттачмент письма


@dataclass
class Email:
    """Данные по конкретному письму в почтовом ящике"""
    subject: str  # тема письма
    body: str  # тело письма
    attachments: list[Filename]  # список имён файлов прикрепленных к письму
    date: str  # дата письма

# Вспомогательные функции


def _imap_date(dt: datetime) -> str:
    """Формат даты для IMAP: 25-June-2025"""
    return dt.strftime("%d-%b-%Y")

# Так как заголовки могут приходить в разных кодировках
# ниже функция будет их декодировать


def _decode(s):
    """Декодирует заголовки (Subject, From, filename…)"""
    parts = decode_header(s)
    decoded = []
    for text, enc in parts:
        decoded.append(
            text.decode(enc or "utf-8", errors="ignore")
            if isinstance(text, bytes)
            else text
        )
    return "".join(decoded)


class IncorrectEnvVariables(Exception):
    """Не хватает нужной переменной окружения"""
    pass


class CantSearchEmails(Exception):
    """Не получилось найти письма"""


class CantReadEmail(Exception):
    """Не получилось прочесть конкретное письмо"""


@tool
def fetch_recent_emails(days: int = 2, SAVE_ATTACHMENTS_DIRECTORY: str = "attachments") -> list[Email]:
    """Возвращает почтовые сообщения и вложения за последние *days* суток."""
    user = os.getenv("EMAIL_LOGIN")
    password = os.getenv("EMAIL_PASSWORD")
    imap_host = os.getenv("EMAIL_IMAP_HOST")
    imap_port = os.getenv("EMAIL_IMAP_PORT")
    if not all((user, password, imap_host, imap_port)):
        raise IncorrectEnvVariables("set correct env variables")

    emails: list[Email] = []
    # вычисляем дату за какой промежуток собираем информацию
    since = datetime.now(timezone.utc) - timedelta(days=days)
    since_str = _imap_date(since)

    # ── Подключаемся ─────────────
    imap = imaplib.IMAP4_SSL(imap_host, imap_port) # Создаёт SSL-соединение
    imap.login(user, password)                     # Авторизация
    imap.select("INBOX")                           # Залетаем во входящие письма

    # ── Ищем письма ─────────────
    status, data = imap.search(None, "SINCE", since_str)  # 'SINCE 26-June-2025'
    if status != "OK":
        raise CantSearchEmails("Поиск не удался:", data)

    ids = data[0].split()
    print(f"Найдено {len(ids)} писем за последние {days} дня(ей)")

    # ── Готовим каталог для вложений ─────────────
    Path(SAVE_ATTACHMENTS_DIRECTORY).mkdir(exist_ok=True)

    # ── Обрабатываем каждое письмо ───────────────
    for num in ids:
        status, msg_data = imap.fetch(num, "(RFC822)") # RFC822 - это стандарт, который определяет формат электронных писем
        if status != "OK":
            raise CantReadEmail(f"Не удалось получить письмо id={num}")

        msg = email.message_from_bytes(msg_data[0][1])

        email_subject = _decode(msg.get("Subject", ""))
        email_date = msg.get("Date", "")

        # Текст письма (всегда берём первую текстовую часть)
        body = ""
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" and part.get_filename() is None:
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="ignore")
                break
        email_body = body

        # Вложения
        attachments: list[Filename] = []
        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                print("attachments", filename)
                filename = _decode(filename).strip()
                filepath = Path(SAVE_ATTACHMENTS_DIRECTORY) / filename
                # предотвращаем перезапись
                if filepath.exists():
                    base, ext = os.path.splitext(filename)
                    filepath = Path(SAVE_ATTACHMENTS_DIRECTORY) / f"{base}_{num.decode()}{ext}"
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                attachments.append(Filename(filepath))

        emails.append(Email(
            subject=email_subject,
            body=email_body,
            attachments=attachments,
            date=email_date
        ))
    imap.close()
    imap.logout() # завершение IMAP-сессии
    return emails



















# # Для тестирования и запуска кода рекомендуется запустить код ниже"""
# # Скачивает письма из mail-почты за последние N суток,
# # включая тексты и все вложения, через IMAP-SSL.

# # Требуется «Пароль приложения» mail-почты (web-интерфейс → Аккаунт → Безопасность
# # → Пароли приложений).
# # IMAP-доступ должен быть включён (Почта → Все настройки → Почтовые программы).
# # """
# from dataclasses import dataclass
# import imaplib
# import email
# from email.header import decode_header
# import os
# from pathlib import Path
# from datetime import datetime, timedelta, timezone
# from typing import TypeAlias
# from langchain_core.tools import tool
# from dotenv import load_dotenv
# load_dotenv()

# SAVE_ATTACHMENTS_DIRECTORY = "attachments"


# Filename: TypeAlias = str  # имя файла, в котором хранится аттачмент письма


# @dataclass
# class Email:
#     """Данные по конкретному письму в почтовом ящике"""
#     subject: str  # тема письма
#     body: str  # тело письма
#     attachments: list[Filename]  # список имён файлов прикрепленных к письму
#     date: str  # дата письма


# def _imap_date(dt: datetime) -> str:
#     """Формат даты для IMAP: 25-June-2025"""
#     return dt.strftime("%d-%b-%Y")


# def _decode(s):
#     """Декодирует заголовки (Subject, From, filename…)"""
#     parts = decode_header(s)
#     decoded = []
#     for text, enc in parts:
#         decoded.append(
#             text.decode(enc or "utf-8", errors="ignore")
#             if isinstance(text, bytes)
#             else text
#         )
#     return "".join(decoded)


# class IncorrectEnvVariables(Exception):
#     """Не хватает нужной переменной окружения"""
#     pass


# class CantSearchEmails(Exception):
#     """Не получилось найти письма"""


# class CantReadEmail(Exception):
#     """Не получилось прочесть конкретное письмо"""


# # @tool
# def fetch_recent_emails_impl(days: int = 3) -> list[Email]:
#     """Возвращает почтовые сообщения и вложения за последние *days* суток."""
#     user = os.getenv("EMAIL_LOGIN")
#     password = os.getenv("EMAIL_PASSWORD")
#     imap_host = os.getenv("EMAIL_IMAP_HOST")
#     imap_port = os.getenv("EMAIL_IMAP_PORT")
#     if not all((user, password, imap_host, imap_port)):
#         raise IncorrectEnvVariables("set correct env variables")

#     emails: list[Email] = []
#     since = datetime.now(timezone.utc) - timedelta(days=days)
#     since_str = _imap_date(since)

#     # ── Подключаемся ───────────────
#     imap = imaplib.IMAP4_SSL(imap_host, imap_port)
#     imap.login(user, password)
#     imap.select("INBOX")

#     # ── Ищем письма ────────────────
#     status, data = imap.search(None, "SINCE", since_str)  # 'SINCE 13-May-2025'
#     if status != "OK":
#         raise CantSearchEmails("Поиск не удался:", data)


#     ids = data[0].split()
#     print(f"Найдено {len(ids)} писем за последние {days} дня(ей)")

#     # ── Готовим каталог для вложений ──────────────
#     Path(SAVE_ATTACHMENTS_DIRECTORY).mkdir(exist_ok=True)

#     # ── Обрабатываем каждое письмо ──────────────
#     for num in ids:
#         status, msg_data = imap.fetch(num, "(RFC822)")
#         if status != "OK":
#             raise CantReadEmail(f"Не удалось получить письмо id={num}")

#         msg = email.message_from_bytes(msg_data[0][1])

#         email_subject = _decode(msg.get("Subject", ""))
#         email_date = msg.get("Date", "")

#         # Текст письма (всегда берём первую текстовую часть)
#         body = ""
#         for part in msg.walk():
#             ctype = part.get_content_type()
#             if ctype == "text/plain" and part.get_filename() is None:
#                 charset = part.get_content_charset() or "utf-8"
#                 body = part.get_payload(decode=True).decode(charset, errors="ignore")
#                 break
#         email_body = body

#         # Вложения
#         attachments: list[Filename] = []
#         for part in msg.walk():
#             filename = part.get_filename()
#             if filename:
#                 print("attachment", filename)
#                 filename = _decode(filename).strip()
#                 filepath = Path(SAVE_ATTACHMENTS_DIRECTORY) / filename
#                 # предотвращаем перезапись
#                 if filepath.exists():
#                     base, ext = os.path.splitext(filename)
#                     filepath = Path(SAVE_ATTACHMENTS_DIRECTORY) / f"{base}_{num.decode()}{ext}"
#                 with open(filepath, "wb") as f:
#                     f.write(part.get_payload(decode=True))
#                 attachments.append(Filename(filepath))

#         emails.append(Email(
#             subject=email_subject,
#             body=email_body,
#             attachments=attachments,
#             date=email_date
#         ))
#     imap.close()
#     imap.logout()
#     return emails


# if __name__ == "__main__":
#     try:
#         print("EMAIL_LOGIN:", os.getenv("EMAIL_LOGIN"))
#         # print("EMAIL_PASSWORD:", os.getenv("EMAIL_PASSWORD"))
#         print("EMAIL_IMAP_HOST:", os.getenv("EMAIL_IMAP_HOST"))
#         print("EMAIL_IMAP_PORT:", os.getenv("EMAIL_IMAP_PORT"))
#         emails = fetch_recent_emails_impl(days=2)
#         print("\n== Письма найдены: ==")
#         for email in emails:
#             print(f"\nТема: {email.subject}")
#             print(f"Дата: {email.date}")
#             print(f"Вложения: {email.attachments}")
#             print(f"Текст письма:\n{email.body[:500]}")
#     except Exception as e:
#         print("Ошибка:", e)
