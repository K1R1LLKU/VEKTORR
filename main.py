import flet as ft
import json
import urllib.request
import urllib.parse
import datetime
import subprocess
import threading
import time
import traceback
from pathlib import Path

# ================================================================
# VEKTOR — стабильная версия для Flet Android/Windows/Linux
# ВАЖНО: используйте одну и ту же версию Flet при запуске и сборке.
# ================================================================
APP_VERSION = "24.1.0"

# ---------- Совместимость с разными версиями Flet ----------
COLORS = getattr(ft, "Colors", None) or getattr(ft, "colors", None)
ICONS = getattr(ft, "Icons", None) or getattr(ft, "icons", None)


def color(name, fallback):
    return getattr(COLORS, name, fallback) if COLORS else fallback


def icon(name, fallback):
    value = getattr(ICONS, name, None) if ICONS else None
    return value if value is not None else fallback


def safe_border(width=1, color_value="#334155"):
    """Совместимость: в новых Flet используется ft.Border.all."""
    border_cls = getattr(ft, "Border", None)
    if border_cls is not None and hasattr(border_cls, "all"):
        return border_cls.all(width, color_value)
    old_border = getattr(ft, "border", None)
    if old_border is not None and hasattr(old_border, "all"):
        return old_border.all(width, color_value)
    return None


CYAN = color("CYAN_ACCENT", "#00f0ff")
CYAN_100 = color("CYAN_100", "#cffafe")
CYAN_200 = color("CYAN_200", "#a5f3fc")
GREEN = color("GREEN_400", "#4ade80")
GREEN_ACCENT = color("GREEN_ACCENT", "#86efac")
RED = color("RED_400", "#f87171")
AMBER = color("AMBER_300", "#fcd34d")
WHITE = color("WHITE", "#ffffff")
GREY = color("GREY_400", "#9ca3af")
BLACK = color("BLACK", "#000000")

SEND = icon("SEND", "send")
SEARCH = icon("SEARCH", "search")
ADD = icon("ADD", "add")
CALENDAR = icon("CALENDAR_MONTH", "calendar_month")
SECURITY = icon("SECURITY", "security")
PLAY = icon("PLAY_ARROW", "play_arrow")

# ---------- Данные ----------
EXERCISES = {
    "Единоборства": ["Бой с тенью", "Отработка двоек", "Работа на лапах", "Скакалка", "Техника защиты"],
    "Бег": ["Лёгкий кросс", "Интервалы", "Спринт 100 м", "Челночный бег", "Фартлек"],
    "Бодибилдинг": ["Жим лёжа", "Приседания", "Становая тяга", "Подтягивания", "Армейский жим"],
    "Кардио": ["Берпи", "Велотренажёр", "Гребля", "Эллипс", "Джампинг-джек"],
    "Растяжка": ["Бабочка", "Растяжка ног", "Мобильность таза", "Кошка-корова", "Плечевой пояс"],
}

ADVISORS = {
    "Репетитор": "Объясняй сложное простыми шагами и задавай наводящие вопросы.",
    "Юрист": "Давай общую правовую информацию, отмечай юрисдикцию и необходимость консультации специалиста.",
    "Аналитик рисков": "Оценивай законность, безопасность, здоровье, финансы и предлагай безопасные альтернативы.",
    "Стратег": "Разбивай планы на этапы, зависимости, риски и проверяемые действия.",
    "OSINT-аналитик": "Работай только с открытыми источниками и законной проверкой собственных ресурсов.",
}

# ---------- Сетевой клиент без requests ----------
class Net:
    @staticmethod
    def post_json(url, payload, api_key, timeout=30):
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "VEKTOR/24.1",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return {"error": str(exc)}

    @staticmethod
    def get_json(url, timeout=10):
        req = urllib.request.Request(url, headers={"User-Agent": "VEKTOR/24.1"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return {"error": str(exc)}


class VektorState:
    def __init__(self):
        self.api_key = ""
        self.advisor = "Репетитор"
        self.tasks = []
        self.food = []
        self.workouts = []
        self.errors = []

    def ask_ai(self, text):
        if not self.api_key:
            return "⚠️ Сначала укажите OpenAI API Key в разделе «Настройки»."
        system = ADVISORS.get(self.advisor, ADVISORS["Аналитик рисков"])
        result = Net.post_json(
            "https://api.openai.com/v1/chat/completions",
            {
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
            },
            self.api_key,
        )
        if "error" in result:
            return f"❌ Ошибка OpenAI: {result['error']}"
        try:
            return result["choices"][0]["message"]["content"]
        except Exception:
            return "❌ OpenAI вернул неожиданный ответ."


state = VektorState()


def main(page: ft.Page):
    page.title = f"VEKTOR v{APP_VERSION}"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO

    status = ft.Text("🔴 API-ключ не подключён", color=RED, size=12)
    advisor_label = ft.Text(f"Советник: {state.advisor}", color=CYAN, weight=ft.FontWeight.BOLD)

    def show_error(where, exc):
        message = f"{where}: {exc}"
        state.errors.append(message)
        return f"⚠️ Не удалось выполнить операцию. Подробность: {exc}"

    # ---------- Чат ----------
    chat_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    chat_input = ft.TextField(hint_text="Сообщение для VEKTOR…", expand=True, multiline=True, min_lines=1, max_lines=4)

    def send_chat(e):
        try:
            text = (chat_input.value or "").strip()
            if not text:
                return
            chat_view.controls.append(ft.Text(f"👤 Вы: {text}", color=CYAN_100))
            chat_input.value = ""
            page.update()
            answer = state.ask_ai(text)
            chat_view.controls.append(ft.Text(f"⚡ VEKTOR ({state.advisor}):\n{answer}", color=GREEN_ACCENT))
            page.update()
        except Exception as exc:
            chat_view.controls.append(ft.Text(show_error("Чат", exc), color=AMBER))
            page.update()

    def make_image(e):
        try:
            prompt = (chat_input.value or "").strip()
            if not prompt:
                chat_view.controls.append(ft.Text("⚠️ Введите описание изображения.", color=AMBER))
                page.update()
                return
            if not state.api_key:
                chat_view.controls.append(ft.Text("⚠️ Нужен OpenAI API Key.", color=AMBER))
                page.update()
                return
            chat_view.controls.append(ft.Text("⏳ Запрос генерации отправлен…", color=AMBER))
            chat_input.value = ""
            page.update()
            result = Net.post_json(
                "https://api.openai.com/v1/images/generations",
                {"model": "dall-e-3", "prompt": prompt, "size": "1024x1024", "n": 1},
                state.api_key,
            )
            if "error" in result:
                chat_view.controls.append(ft.Text(f"❌ Ошибка генерации: {result['error']}", color=RED))
            else:
                url = result.get("data", [{}])[0].get("url")
                if url:
                    chat_view.controls.append(ft.Image(src=url, width=320, height=320, fit=ft.ImageFit.CONTAIN))
                else:
                    chat_view.controls.append(ft.Text("❌ URL изображения не получен.", color=RED))
            page.update()
        except Exception as exc:
            chat_view.controls.append(ft.Text(show_error("Генерация изображения", exc), color=AMBER))
            page.update()

    chat_tab = ft.Column([
        ft.Row([ft.Text("VEKTOR", size=20, weight=ft.FontWeight.BOLD, color=CYAN), advisor_label, status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        chat_view,
        ft.Row([
            chat_input,
            ft.IconButton(icon=SEND, tooltip="Отправить", on_click=send_chat, icon_color=CYAN),
            ft.IconButton(icon="image", tooltip="Создать изображение", on_click=make_image, icon_color="#d8b4fe"),
        ]),
    ], expand=True)

    # ---------- OSINT ----------
    osint_input = ft.TextField(label="IP, домен, ИНН или название компании", expand=True)
    osint_result = ft.Text("Результат появится здесь…", selectable=True, color=CYAN_200)

    def ip_lookup(e):
        value = (osint_input.value or "").strip().replace("https://", "").replace("http://", "").split("/")[0]
        if not value:
            return
        data = Net.get_json(f"http://ip-api.com/json/{urllib.parse.quote(value)}?fields=status,country,city,isp,org,as,query")
        if data.get("status") == "success":
            osint_result.value = (f"🌐 Узел: {data.get('query')}\nСтрана: {data.get('country')}\n"
                                  f"Город: {data.get('city')}\nISP: {data.get('isp')}\n"
                                  f"Организация: {data.get('org')}\nAS: {data.get('as')}\n\n"
                                  f"Wayback: https://web.archive.org/web/*/{value}\n"
                                  f"SSL: https://crt.sh/?q={value}")
        else:
            osint_result.value = f"⚠️ Данные не получены: {data.get('error', 'узел не найден')}"
        page.update()

    def registry_links(e):
        q = urllib.parse.quote((osint_input.value or "").strip())
        osint_result.value = ("🏛️ Проверяйте контрагента только по официальным источникам:\n\n"
            "ФНС ЕГРЮЛ/ЕГРИП: https://egrul.nalog.ru/\n"
            "Арбитраж: https://kad.arbitr.ru/\n"
            "Федресурс: https://bankrot.fedresurs.ru/\n"
            "ФССП: https://fssp.gov.ru/iss/ip/\n"
            "Госзакупки: https://zakupki.gov.ru/\n"
            f"OpenCorporates: https://opencorporates.com/companies?q={q}")
        page.update()

    def dorks(e):
        q = (osint_input.value or "").replace('"', '').strip()
        osint_result.value = (f"🔍 Безопасные запросы по открытым данным для: {q}\n\n"
            f'"{q}" filetype:pdf OR filetype:docx\n'
            f'"{q}" (ИНН OR ОГРН OR арбитраж)\n'
            f'site:linkedin.com/in/ OR site:vk.com "{q}"')
        page.update()

    osint_tab = ft.Column([
        ft.Text("🌐 Законный OSINT и Due Diligence", size=18, weight=ft.FontWeight.BOLD, color=CYAN),
        ft.Row([osint_input, ft.ElevatedButton("Сеть/DNS", icon=SEARCH, on_click=ip_lookup)]),
        ft.Row([ft.ElevatedButton("Официальные реестры", icon=SECURITY, on_click=registry_links),
                ft.ElevatedButton("Dorks", icon=SEARCH, on_click=dorks)]),
        ft.Container(content=osint_result, padding=12, border=safe_border(), expand=True),
    ], expand=True)

    # ---------- Планер ----------
    task_input = ft.TextField(label="Новая задача", expand=True)
    task_time = ft.TextField(label="Время", width=100)
    tasks_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def render_tasks():
        tasks_view.controls.clear()
        for task in state.tasks:
            tasks_view.controls.append(ft.Checkbox(label=f"[{task['time']}] {task['text']}", value=task["done"], on_change=lambda e, t=task: t.update(done=e.control.value)))
        page.update()

    def add_task(e):
        if (task_input.value or "").strip():
            state.tasks.append({"text": task_input.value.strip(), "time": task_time.value.strip() or "—", "done": False})
            task_input.value = ""
            task_time.value = ""
            render_tasks()

    planner_tab = ft.Column([
        ft.Text("📅 Планер и календарь", size=18, weight=ft.FontWeight.BOLD, color=CYAN),
        ft.Row([task_time, task_input, ft.ElevatedButton("Добавить", icon=ADD, on_click=add_task)]),
        tasks_view,
    ], expand=True)

    # ---------- КБЖУ и спорт ----------
    food_name = ft.TextField(label="Продукт", expand=True)
    food_weight = ft.TextField(label="Вес, г", value="100", width=90)
    food_kcal = ft.TextField(label="Ккал/100 г", value="0", width=100)
    kbju_total = ft.Text("Итого: 0 ккал", color=AMBER)
    food_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def add_food(e):
        try:
            grams = float(food_weight.value)
            kcal = float(food_kcal.value) * grams / 100
            state.food.append((food_name.value or "Продукт", grams, kcal))
            food_name.value = ""
            food_view.controls = [ft.Text(f"• {n} — {g:g} г, {k:.0f} ккал") for n, g, k in state.food]
            kbju_total.value = f"Итого: {sum(x[2] for x in state.food):.0f} ккал"
            page.update()
        except Exception as exc:
            page.snack_bar = ft.SnackBar(ft.Text(f"Проверьте числа: {exc}"), open=True)
            page.update()

    sport_dd = ft.Dropdown(label="Вид спорта", value="Единоборства", options=[ft.dropdown.Option(x) for x in EXERCISES], width=170)
    exercise_dd = ft.Dropdown(label="Упражнение", value=EXERCISES["Единоборства"][0], options=[ft.dropdown.Option(x) for x in EXERCISES["Единоборства"]], expand=True)
    workout_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def change_sport(e):
        exercise_dd.options = [ft.dropdown.Option(x) for x in EXERCISES.get(sport_dd.value, [])]
        exercise_dd.value = EXERCISES.get(sport_dd.value, [""])[0]
        page.update()

    def add_workout(e):
        state.workouts.append(f"{sport_dd.value}: {exercise_dd.value}")
        workout_view.controls = [ft.Text(f"🏋️ {x}", color=GREEN_ACCENT) for x in state.workouts]
        page.update()

    sport_dd.on_change = change_sport
    fitness_tab = ft.Column([
        ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="КБЖУ", content=ft.Column([kbju_total, ft.Row([food_name, food_weight, food_kcal]), ft.ElevatedButton("Добавить", icon="restaurant", on_click=add_food), food_view], expand=True)),
            ft.Tab(text="Тренировки", content=ft.Column([ft.Row([sport_dd, exercise_dd]), ft.ElevatedButton("Записать", icon="fitness_center", on_click=add_workout), workout_view], expand=True)),
        ], expand=True)
    ], expand=True)

    # ---------- Безопасный терминал ----------
    terminal_output = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    terminal_input = ft.TextField(label="Диагностическая команда", expand=True)
    allowed_commands = {"ping", "nslookup", "traceroute", "tracert", "ipconfig", "ifconfig", "uname", "whoami"}

    def run_safe_command(e):
        raw = (terminal_input.value or "").strip()
        if not raw:
            return
        command = raw.split()[0].lower()
        if command not in allowed_commands:
            terminal_output.controls.append(ft.Text("⛔ Разрешены только диагностические команды.", color=RED))
            page.update()
            return
        try:
            result = subprocess.run(raw, shell=True, capture_output=True, text=True, timeout=8)
            terminal_output.controls.append(ft.Text(f"> {raw}\n{result.stdout or result.stderr}", font_family="monospace", color=GREEN_ACCENT))
        except Exception as exc:
            terminal_output.controls.append(ft.Text(f"Ошибка: {exc}", color=RED))
        terminal_input.value = ""
        page.update()

    terminal_tab = ft.Column([
        ft.Text("💻 Безопасный терминал диагностики", size=18, weight=ft.FontWeight.BOLD, color=GREEN),
        terminal_output,
        ft.Row([terminal_input, ft.ElevatedButton("Run", icon=PLAY, on_click=run_safe_command)]),
    ], expand=True)

    # ---------- Аналитик и Стратег ----------
    risk_input = ft.TextField(label="Опишите предмет, действие или план", multiline=True, min_lines=3, expand=True)
    risk_output = ft.Text("Результат оценки рисков появится здесь…", selectable=True, color=CYAN_200)

    def risk_analysis(e):
        text = (risk_input.value or "").strip()
        if not text:
            return
        risk_output.value = state.ask_ai(
            "Проанализируй план безопасно и законно. Структура: риски для здоровья, юридические риски, "
            "финансовые и технические риски, что уточнить, безопасный альтернативный план. "
            "Не давай инструкции по взлому, насилию, оружию или обходу закона. План: " + text
        )
        page.update()

    analyst_tab = ft.Column([
        ft.Text("🧠 Аналитик и Стратег", size=18, weight=ft.FontWeight.BOLD, color=CYAN),
        risk_input,
        ft.ElevatedButton("Оценить риски", icon=SECURITY, on_click=risk_analysis),
        ft.Container(content=risk_output, padding=12, border=safe_border(), expand=True),
    ], expand=True)

    # ---------- Настройки ----------
    key_input = ft.TextField(label="OpenAI API Key", password=True, can_reveal_password=True)
    advisor_dd = ft.Dropdown(label="Советник", value=state.advisor, options=[ft.dropdown.Option(x) for x in ADVISORS])

    def save_settings(e):
        state.api_key = (key_input.value or "").strip()
        state.advisor = advisor_dd.value or "Репетитор"
        advisor_label.value = f"Советник: {state.advisor}"
        status.value = "🟢 API-ключ подключён" if state.api_key else "🔴 API-ключ не подключён"
        status.color = GREEN if state.api_key else RED
        page.snack_bar = ft.SnackBar(ft.Text("Настройки сохранены"), open=True)
        page.update()

    settings_tab = ft.Column([
        ft.Text("🔑 Настройки VEKTOR", size=18, weight=ft.FontWeight.BOLD, color=CYAN),
        key_input,
        advisor_dd,
        ft.ElevatedButton("Сохранить", on_click=save_settings),
        ft.Text(f"Версия: {APP_VERSION}", color=GREY, size=12),
    ], expand=True)

    # ---------- Сборка интерфейса ----------
    tabs = ft.Tabs(
        selected_index=0,
        scrollable=True,
        tabs=[
            ft.Tab(text="💬 Чат", content=chat_tab),
            ft.Tab(text="🌐 OSINT", content=osint_tab),
            ft.Tab(text="📅 Планер", content=planner_tab),
            ft.Tab(text="🥗 Спорт", content=fitness_tab),
            ft.Tab(text="🧠 Аналитик", content=analyst_tab),
            ft.Tab(text="💻 Терминал", content=terminal_tab),
            ft.Tab(text="🔑 Настройки", content=settings_tab),
        ],
        expand=1,
    )
    page.add(tabs)


if __name__ == "__main__":
    # Только аварийный лог. Не переписываем код приложения автоматически:
    # безопасные обновления лучше делать через новую сборку APK.
    try:
        ft.app(target=main)
    except Exception:
        Path("vektor_crash.log").write_text(traceback.format_exc(), encoding="utf-8")
        raise
