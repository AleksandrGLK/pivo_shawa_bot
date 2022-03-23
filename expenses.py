""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    amount: int
    category_text: str


class Expense(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    id: Optional[int]
    amount: int
    category_name: str


def add_expense(raw_message: str, user_id: int) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    inserted_row_id = db.insert("expense", {
        "person_id": user_id,
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name)

def get_summer_statistics(user_id: int) -> str:
    """Возвращает строкой статистику выпитого пива и съеденной шавермы за лето"""
    now = _get_now_datetime()
    cursor = db.get_cursor()
    first_day_of_summer = f'{now.year:04d}-06-01'
    last_day_of_summer = f'{now.year:04d}-09-31'
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) between "
                   f"'{first_day_of_summer}' and '{last_day_of_summer}' "
                   f"and person_id={user_id} ")
    result = cursor.fetchone()
    if not result[0]:
        return (f"До лета {(datetime.datetime(int(now.year), 6, 1)-datetime.datetime.now()).days} дней\n"
                f"Осталось совсем чуть-чуть")
    all_summer_expenses = result[0] if result[0] else 0
    cursor.execute(f"select sum(amount), count(amount) "
                   f"from expense where date(created) between "
                   f"'{first_day_of_summer}' and '{last_day_of_summer}' "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename = 'beer')")
    result = cursor.fetchone()
    beer_summer_expenses = result[0] if result[0] else 0
    beer_summer_col = result[1] if result[1] else 0
    cursor.execute(f"select sum(amount), count(amount) "
                   f"from expense where date(created) between "
                   f"'{first_day_of_summer}' and '{last_day_of_summer}' "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename = 'shaverma')")
    result = cursor.fetchone()
    shaverma_summer_expenses = result[0] if result[0] else 0
    shaverma_summer_col = result[1] if result[1] else 0
    return (f"Расходы за лето:\n"
            f"пиво — {beer_summer_expenses} руб. {beer_summer_col} шт.\n"
            f"шаверма — {shaverma_summer_expenses} руб. {shaverma_summer_col} шт.\n\n"
            f"всего — {all_summer_expenses} руб.\n"
            f"До конца лета осталось {(datetime.datetime(int(now.year), 8, 31) - datetime.datetime.now()).days} - дней\n")

def get_full_statistics(user_id: int) -> str:
    """Возвращает строкой статистику выпитого пива и съеденной шавермы за все время"""
    now = _get_now_datetime()
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) <= date('now', 'localtime')"
                   f"and person_id={user_id} ")
    result = cursor.fetchone()
    if not result[0]:
        return "Еще ничего не съедено и не выпито!"
    all_time_expenses = result[0] if result[0] else 0
    cursor.execute(f"select sum(amount), count(amount) "
                   f"from expense where date(created) <= date('now', 'localtime') "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename = 'beer')")
    result = cursor.fetchone()
    beer_time_expenses = result[0] if result[0] else 0
    beer_full_col = result[1] if result[1] else 0
    cursor.execute(f"select sum(amount), count(amount) "
                   f"from expense where date(created) <= date('now', 'localtime') "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename = 'shaverma')")
    result = cursor.fetchone()
    shaverma_time_expenses = result[0] if result[0] else 0
    shaverma_full_col = result[1] if result[1] else 0
    return (f"Расходы за все время:\n"
            f"пиво — {beer_time_expenses} руб. {beer_full_col} шт.\n"
            f"шаверма — {shaverma_time_expenses} руб. {shaverma_full_col} шт.\n\n"
            f"всего — {all_time_expenses} руб.\n")


def get_today_statistics(user_id: int) -> str:
    """Возвращает строкой статистику расходов за сегодня"""
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created)=date('now', 'localtime')"
                   f"and person_id={user_id} ")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0] if result[0] else 0
    cursor.execute(f"select sum(amount), count(amount)"
                   f"from expense where date(created)=date('now', 'localtime') "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename='beer')")
    result = cursor.fetchone()
    beer_today_expenses = result[0] if result[0] else 0
    beer_today_col =  result[1] if result[1] else 0
    cursor.execute(f"select sum(amount), count(amount) "
                   f"from expense where date(created)=date('now', 'localtime') "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename='shaverma')")
    result = cursor.fetchone()
    shaverma_today_expenses = result[0] if result[0] else 0
    shaverma_today_col =  result[1] if result[1] else 0
    return (f"Расходы сегодня:\n"
            f"пиво — {beer_today_expenses} руб. {beer_today_col} шт.\n"
            f"шаверма — {shaverma_today_expenses} руб. {shaverma_today_col} шт.\n\n"
            f"всего — {all_today_expenses} руб.\n"
            f"За текущий месяц: /month")


def get_month_statistics(user_id: int) -> str:
    """Возвращает строкой статистику расходов за текущий месяц"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'"
                   f"and person_id={user_id} ")
    result = cursor.fetchone()
    if not result[0]:
        return "В этом месяце ещё нет расходов"
    all_month_expenses = result[0] if result[0] else 0
    cursor.execute(f"select sum(amount), count(amount)"
                   f"from expense where date(created) >= '{first_day_of_month}' "
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename = 'beer')")
    result = cursor.fetchone()
    beer_month_expenses = result[0] if result[0] else 0
    beer_month_col =  result[1] if result[1] else 0
    cursor.execute(f"select sum(amount), count(amount)"
                   f"from expense where date(created) >= '{first_day_of_month}'"
                   f"and person_id={user_id} "
                   f"and category_codename in (select codename "
                   f"from category where codename = 'shaverma')")
    result = cursor.fetchone()
    shaverma_month_expenses = result[0] if result[0] else 0
    shaverma_month_col =  result[1] if result[1] else 0
    return (f"Расходы за месяц:\n"
            f"пиво — {beer_month_expenses} руб. {beer_month_col} шт.\n"
            f"шаверма — {shaverma_month_expenses} руб. {shaverma_month_col} шт.\n\n"
            f"всего — {all_month_expenses} руб.\n"
            f"За весь период: /statistic")


def last(user_id: int) -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        f"select e.id, e.amount, c.name "
        f"from expense e left join category c "
        f"on c.codename=e.category_codename "
        f"where e.person_id={user_id} "
        f"order by created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int, user_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id, user_id)


def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500 пиво")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def _get_budget_limit() -> int:
    """Возвращает дневной лимит трат для основных базовых трат"""
    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]
