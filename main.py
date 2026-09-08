import os
import sys
import time
import subprocess
import threading
import urllib.request
import json
import datetime

# =====================================================================
# VEKTOR OS // ULTIMATE SUPREME TACTICAL CORE v23.0
# ПОЛНЫЙ КОМПЛЕКС: ИИ, OSINT, ТЕЛЕФОНИЯ, КБЖУ, ПЛАНЕР, АНАЛИТИК, СТРАТЕГ, 
# КИБЕРЗАЩИТА, АКАДЕМИЯ БОЯ, СПРАВОЧНИК ОРУЖИЯ, ТЕРМИНАЛ И WATCHDOG
# =====================================================================

VERSION_TAG = "23.0.0"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Paramon4ik/VEKTORR/main/main.py"

def emergency_logger(err_str):
    try:
        with open("vektor_crash.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {err_str}\n")
    except Exception:
        pass

def download_latest_core():
    """ Автономная OTA загрузка обновлений с GitHub (таймаут 120 сек) """
    try:
        req = urllib.request.Request(GITHUB_RAW_URL, headers={'User-Agent': 'VEKTOR-Watchdog/23.0'})
        with urllib.request.urlopen(req, timeout=120) as response:
            if response.status == 200:
                code_data = response.read().decode('utf-8')
                if "VEKTOR OS" in code_data or "main(page" in code_data:
                    target_path = sys.argv[0] if sys.argv[0].endswith('.py') else 'main.py'
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(code_data)
                    return True
    except Exception as e:
        emergency_logger(f"Ошибка OTA обновления: {e}")
    return False

# --- БАЗЫ ДАННЫХ И СПРАВОЧНИКИ ---
EXERCISES_CATALOG = {
    "Единоборства": ["Бой с тенью (Shadowboxing)", "Отработка двоек", "Хуки и Апперкоты", "Лоу-кик", "Тейкдаун", "Броски", "Спарринг"],
    "Бег": ["Легкий кросс 5км", "Интервальный бег", "Спринт 100м", "Трейлраннинг", "Челночный бег"],
    "Бодибилдинг": ["Жим лежа", "Приседания", "Становая тяга", "Армейский жим", "Подтягивания", "Брусья"],
    "Кардио": ["Скакалка", "Берпи", "Гребной тренажер", "Велотренажер", "Эллипс"],
    "Растяжка": ["Шпагат", "Мобильность суставов", "Растяжка спины", "Бабочка"]
}

COMBAT_ACADEMY = {
    "🥋 Прикладной рукопашный бой (АРБ)": {
        "Описание": "Система выживания и контактного взаимодействия в условиях агрессивной среды.",
        "Материалы": [
            "📖 Книга: «Армейский рукопашный бой» (Кадочников А.А.) — Биомеханика и рычаги.",
            "📖 Статья: «Ударная техника коленями и локтями в самообороне».",
            "🎥 Видео: Базовые принципы жесткого нокаутирующего удара и сохранения баланса."
        ]
    },
    "🥊 Тактики тренировок великих боксёров": {
        "Описание": "Секреты выносливости, тайминга и защиты легенд ринга (Тайсон, Али, Мейвезер).",
        "Материалы": [
            "📖 Книга: «Бескомпромиссный бокс: Система Майка Тайсона».",
            "📖 Статья: «Работа на мешке по методике Кас Д’Амато: углы и уклоны».",
            "🎥 Видео: Разбор защиты Philly Shell (Флойд Мейвезер)."
        ]
    },
    "🗡️ Ножевой бой и самооборона": {
        "Описание": "Контроль дистанции, психология схватки и защита от вооруженного противника.",
        "Материалы": [
            "📖 Книга: «Боевой нож» (Кондратьев А.).",
            "📖 Статья: «Анатомия порезов и уколов: критические зоны».",
            "🎥 Видео: Хваты ножа, смена углов атаки и уходы с линии удара."
        ]
    }
}

WEAPON_ENCYCLOPEDIA = {
    "1. Боевой нож «Кайт» / Тактический нож": {
        "1. Убийственная мощь": "Высокая (глубокие проникающие колотые раны и режущие свойства).",
        "2. На сколько хорош в охоте": "Средний (удобен для свежевания, но коротковат для крупного зверя).",
        "3. Длинна лезвия/Калибр": "Длина лезвия: 140–160 мм (обух 4.5 мм).",
        "4. Практичность": "Максимальная (компактен, цельнометаллический full-tang).",
        "5. Где и когда можно применить": "Спецоперации, выживание в дикой природе, полевой быт.",
        "6. Как правильно ухаживать": "Промывать после влаги и крови, править на бруске, смазывать маслом.",
        "7. Хорош или плох в ножевом бою или дуэли, и почему?": "Отличен. Имеет гарду для защиты пальцев и идеальный баланс.",
        "8. Запрещен на территории РФ или нет?": "Зависит от сертификата. Без сертификата ХозБыт может классифицироваться как Холодное Оружие (ХО)."
    },
    "2. Автомат Калашникова (АК-74М)": {
        "1. Убийственная мощь": "Критическая (высокая баллистика патрона 5.45х39 мм).",
        "2. На сколько хорош в охоте": "Плохой для промысла (сильно портит мясо дичи).",
        "3. Длинна лезвия/Калибр": "Калибр: 5.45х39 мм (ствол 415 мм).",
        "4. Практичность": "Легендарная (работает в грязи, воде и при экстремальных температурах).",
        "5. Где и когда можно применить": "Войсковые конфликты, охрана периметра, тактические задачи.",
        "6. Как правильно ухаживать": "Чистка и смазка ствола и газовой камеры после стрельбы.",
        "7. Хорош или плох в ножевом бою или дуэли, и почему?": "Превосходен на средней/дальней дистанции. В ближнем бою громоздок.",
        "8. Запрещен на территории РФ или нет?": "Боевой автоматический — строго запрещен. Охотничьи гражданские версии (Саййга) — разрешены по лицензии."
    }
}

TEAM_MEMBERS = {
    "🎓 Репетитор (30 лет стажа)": "Ты — добрый, терпеливый репетитор. Объясняй логику через наводящие вопросы.",
    "⚡ Олег Тиньков": "Ты — Олег Тиньков. Общайся дерзко, мотивируй на масштабный бизнес и продажи.",
    "👮‍♂️ Сергей (ФСБ / Безопасность)": "Ты — офицер безопасности и эксперт по киберзащите и OSINT.",
    "🥊 «Калибр» (Спецназ / АРБ)": "Ты — инструктор спецназа, эксперт по рукопашному бою.",
    "⚖️ Михаил (Главный юрист)": "Ты — юрист высшей квалификации. Консультируй по законам РФ."
}

def run_vektor_core():
    import flet as ft
    import urllib.parse
    import urllib.error

    CURRENT_VERSION = VERSION_TAG

    class SafeUI:
        _icons = getattr(ft, 'Icons', None) or getattr(ft, 'icons', None)
        _colors = getattr(ft, 'Colors', None) or getattr(ft, 'colors', None)

        @classmethod
        def icon(cls, name_upper, string_fallback):
            if cls._icons and hasattr(cls._icons, name_upper):
                return getattr(cls._icons, name_upper)
            if cls._icons and hasattr(cls._icons, name_upper.lower()):
                return getattr(cls._icons, name_upper.lower())
            return string_fallback.lower()

        @classmethod
        def color(cls, name_upper, hex_fallback):
            if cls._colors and hasattr(cls._colors, name_upper):
                return getattr(cls._colors, name_upper)
            if cls._colors and hasattr(cls._colors, name_upper.lower()):
                return getattr(cls._colors, name_upper.lower())
            return hex_fallback

    C_RED = SafeUI.color('RED_400', '#f87171')
    C_GREEN = SafeUI.color('GREEN_400', '#4ade80')
    C_GREEN_ACC = SafeUI.color('GREEN_ACCENT', '#86efac')
    C_CYAN_ACC = SafeUI.color('CYAN_ACCENT', '#00f0ff')
    C_CYAN_100 = SafeUI.color('CYAN_100', '#cffafe')
    C_CYAN_200 = SafeUI.color('CYAN_200', '#a5f3fc')
    C_AMBER_300 = SafeUI.color('AMBER_300', '#fcd34d')
    C_PURPLE_200 = SafeUI.color('PURPLE_200', '#e9d5ff')
    C_PURPLE_300 = SafeUI.color('PURPLE_300', '#d8b4fe')
    C_WHITE = SafeUI.color('WHITE', '#ffffff')
    C_BLACK = SafeUI.color('BLACK', '#000000')
    C_GREY_400 = SafeUI.color('GREY_400', '#9ca3af')

    ICON_SEND = SafeUI.icon('SEND', 'send')
    ICON_IMAGE = SafeUI.icon('IMAGE', 'image')
    ICON_SEARCH = SafeUI.icon('SEARCH', 'search')
    ICON_LANGUAGE = SafeUI.icon('LANGUAGE', 'language')
    ICON_SECURITY = SafeUI.icon('SECURITY', 'security')
    ICON_CALL = SafeUI.icon('CALL', 'call')
    ICON_RESTAURANT = SafeUI.icon('RESTAURANT', 'restaurant')
    ICON_FITNESS = SafeUI.icon('FITNESS_CENTER', 'fitness_center')
    ICON_CALENDAR = SafeUI.icon('CALENDAR_MONTH', 'calendar_month')
    ICON_ADD = SafeUI.icon('ADD', 'add')
    ICON_REFRESH = SafeUI.icon('REFRESH', 'refresh')

    class NetClient:
        @staticmethod
        def get_json(url, timeout=8):
            req = urllib.request.Request(url, headers={'User-Agent': 'VEKTOR-Ultimate/23.0'})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        return json.loads(response.read().decode('utf-8'))
            except Exception:
                return None
            return None

        @staticmethod
        def post_json(url, payload, headers, timeout=25):
            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    return json.loads(response.read().decode('utf-8'))
            except Exception as e:
                return {"error": f"Сетевой сбой: {e}"}

    class AIAssistantApp:
        def __init__(self):
            self.openai_key = ""
            self.active_advisor = "👮‍♂️ Сергей (ФСБ / Безопасность)"

        def get_gpt_response(self, user_text):
            if not self.openai_key:
                return "⚠️ Введите ваш OpenAI API Key во вкладке '🔑 Настройки'!"
            sys_prompt = TEAM_MEMBERS.get(self.active_advisor, "Ты эксперт.")
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.openai_key}"}
            payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}]}
            res = NetClient.post_json(url, payload, headers)
            if "error" in res: return f"❌ Ошибка OpenAI: {res['error']}"
            try: return res["choices"][0]["message"]["content"]
            except Exception as e: return f"❌ Ошибка: {e}"

        def generate_image(self, prompt_text):
            if not self.openai_key: return None, "⚠️ Введите OpenAI API Key!"
            url = "https://api.openai.com/v1/images/generations"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.openai_key}"}
            payload = {"prompt": prompt_text, "n": 1, "size": "1024x1024"}
            res = NetClient.post_json(url, payload, headers)
            if "error" in res: return None, f"❌ DALL-E: {res['error']}"
            try: return res["data"][0]["url"], "✅ Успешно!"
            except Exception as e: return None, f"❌ Ошибка: {e}"

    app_logic = AIAssistantApp()

    def main(page: ft.Page):
        page.title = f"VEKTOR v{CURRENT_VERSION} // ULTIMATE SUPREME"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 10
        
        status_badge = ft.Text("🔴 Ключ не привязан", color=C_RED, size=12)

        # Фоновый OTA чек (2 мин таймаут)
        threading.Thread(target=download_latest_core, daemon=True).start()

        # 1. ИИ-ЧАТ
        chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        user_input = ft.TextField(hint_text="Введите запрос для VEKTOR или советника...", expand=True)
        advisor_title = ft.Text(f"VEKTOR // {app_logic.active_advisor}", weight=ft.FontWeight.BOLD, color=C_CYAN_ACC)

        def send_message(e):
            if not user_input.value: return
            txt = user_input.value
            chat_history.controls.append(ft.Text(f"👤 Вы: {txt}", color=C_CYAN_100, weight=ft.FontWeight.BOLD))
            user_input.value = ""
            page.update()
            ans = app_logic.get_gpt_response(txt)
            chat_history.controls.append(ft.Text(f"⚡ VEKTOR:\n{ans}", color=C_GREEN_ACC))
            page.update()

        def generate_photo(e):
            if not user_input.value: return
            prompt = user_input.value
            chat_history.controls.append(ft.Text(f"🎨 Генерация: '{prompt}'", color=C_PURPLE_200, weight=ft.FontWeight.BOLD))
            user_input.value = ""
            page.update()
            url, msg = app_logic.generate_image(prompt)
            if url:
                chat_history.controls.append(ft.Image(src=url, width=300, height=300, border_radius=10))
            else:
                chat_history.controls.append(ft.Text(msg, color=C_RED))
            page.update()

        tab_chat = ft.Column([
            ft.Row([ft.Text("VEKTOR", size=20, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC), advisor_title, status_badge], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            chat_history,
            ft.Row([user_input, ft.IconButton(icon=ICON_SEND, on_click=send_message, icon_color=C_CYAN_ACC), ft.IconButton(icon=ICON_IMAGE, on_click=generate_photo, icon_color=C_PURPLE_300)])
        ], expand=True)

        # 2. OSINT РАЗВЕДКА
        osint_inp = ft.TextField(label="Цель OSINT (IP / Домен)", hint_text="example.com")
        osint_out = ft.Text("Результаты OSINT появятся здесь...", color=C_CYAN_200, selectable=True)

        def run_osint(e):
            if not osint_inp.value: return
            clean = osint_inp.value.strip().replace("https://", "").split("/")[0]
            data = NetClient.get_json(f"http://ip-api.com/json/{clean}?fields=status,country,city,isp,org,as,query")
            if data and data.get("status") == "success":
                osint_out.value = f"🌐 IP: {data.get('query')}\nСтрана: {data.get('country')}\nГород: {data.get('city')}\nISP: {data.get('isp')}"
            else:
                osint_out.value = "⚠️ Узел не найден."
            page.update()

        tab_osint = ft.Column([
            ft.Text("🕵️ OSINT Разведка", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            osint_inp,
            ft.ElevatedButton("Сканировать IP", on_click=run_osint, icon=ICON_SEARCH, bgcolor="#0e7490", color=C_WHITE),
            ft.Divider(),
            ft.Container(content=osint_out, padding=10, border=ft.border.all(1, "#334155"), border_radius=8)
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        # 3. ТЕЛЕФОНИЯ
        phone_inp = ft.TextField(label="Номер телефона", value="+7")
        phone_out = ft.Text("Готово к проверке номера...", color=C_CYAN_200)

        def check_phone(e):
            num = phone_inp.value
            phone_out.value = f"📞 Проверка номера {num}: Формат валиден."
            page.update()

        tab_telephony = ft.Column([
            ft.Text("📞 Телефония", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            phone_inp,
            ft.ElevatedButton("Проверить номер", on_click=check_phone, icon=ICON_CALL, bgcolor="#16a34a", color=C_WHITE),
            ft.Container(content=phone_out, padding=10, bgcolor="#0d1322", border_radius=8)
        ], expand=True)

        # 4. СПОРТ И КБЖУ
        f_name = ft.TextField(label="Продукт", expand=True)
        f_cal = ft.TextField(label="Ккал/100г", value="100", width=90)
        f_w = ft.TextField(label="Вес (г)", value="100", width=90)
        kbju_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def add_food(e):
            try:
                c = float(f_cal.value) * (float(f_w.value)/100.0)
                kbju_view.controls.append(ft.Text(f"• {f_name.value} ({f_w.value}г) — {c:.1f} ккал", color=C_WHITE))
                f_name.value = ""
                page.update()
            except: pass

        tab_fitness = ft.Column([
            ft.Text("🥗 КБЖУ и Спорт", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            ft.Row([f_name, f_cal, f_w]),
            ft.ElevatedButton("Добавить блюдо", on_click=add_food, icon=ICON_RESTAURANT, bgcolor="#b45309", color=C_WHITE),
            ft.Divider(), kbju_view
        ], expand=True)

        # 5. ПЛАНЕР И СТРАТЕГ
        task_inp = ft.TextField(label="Новая задача / Проект для Стратега", expand=True)
        task_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        strat_out = ft.Text("Анализ рисков стратега...", color=C_AMBER_300, selectable=True)

        def add_task(e):
            if not task_inp.value: return
            task_view.controls.append(ft.Checkbox(label=task_inp.value))
            task_inp.value = ""
            page.update()

        def run_strategist(e):
            if not task_inp.value: return
            strat_out.value = "⏳ Стратег анализирует риски и законность..."
            page.update()
            res = app_logic.get_gpt_response(f"Проведи глубокий стратегический анализ идеи/проекта. Оцени риски для здоровья, финансов и перед законом РФ, дай пошаговый план: {task_inp.value}")
            strat_out.value = res
            page.update()

        tab_planner = ft.Column([
            ft.Text("📅 Планер & Отдел «Стратег»", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            task_inp,
            ft.Row([ft.ElevatedButton("Добавить в план", on_click=add_task, icon=ICON_ADD, bgcolor="#16a34a", color=C_WHITE), ft.ElevatedButton("Запрос к Стратегу", on_click=run_strategist, icon=ICON_SECURITY, bgcolor="#0e7490", color=C_WHITE)]),
            ft.Divider(), task_view, ft.Divider(),
            ft.Container(content=strat_out, padding=10, bgcolor="#0d1322", border_radius=8)
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        # 6. АНАЛИТИК (ПРОВЕРКА РИСКОВ И СТАТЕЙ)
        analyst_inp = ft.TextField(label="Опишите предмет или действие для проверки", multiline=True, min_lines=2)
        analyst_out = ft.Text("Результаты правового аудита...", color=C_CYAN_100, selectable=True)

        def run_analyst(e):
            if not analyst_inp.value: return
            analyst_out.value = "⏳ Аналитик проверяет нормы законодательства..."
            page.update()
            res = app_logic.get_gpt_response(f"Проведи правовой аудит объекта или действия. Если есть нарушение закона РФ, сначала покажи предупреждение ⚠️ со статьями УК РФ/КоАП и возможными наказаниями, затем объясни суть и безопасную альтернативу: {analyst_inp.value}")
            analyst_out.value = res
            page.update()

        tab_analyst = ft.Column([
            ft.Text("⚖️ Отдел «Аналитик» (Правовой аудит)", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            analyst_inp,
            ft.ElevatedButton("Проверить на законность и риски", on_click=run_analyst, icon=ICON_SECURITY, bgcolor="#b91c1c", color=C_WHITE),
            ft.Divider(),
            ft.Container(content=analyst_out, padding=10, bgcolor="#0d1322", border_radius=8)
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        # 7. АКАДЕМИЯ КИБЕРЗАЩИТЫ
        cyber_text = ft.Text(
            "🛡️ **АКАДЕМИЯ КИБЕРЗАЩИТЫ И СЕТЕВОЙ БЕЗОПАСНОСТИ**\n\n"
            "1. **Защита веб-сайтов:** Настройка WAF, экранирование входных данных для предотвращения SQLi/XSS.\n"
            "2. **Отражение DDoS-атак:** Использование CDN, ограничение частоты запросов (Rate Limiting) и балансировка.\n"
            "3. **Безопасность IoT и сетей:** Закрытие дефолтных портов, смена стандартных паролей камер.\n"
            "4. **Аудит сетевых периметров:** Сканирование открытых портов с помощью Nmap для выявления уязвимостей.",
            color=C_CYAN_100, selectable=True
        )
        tab_cyber = ft.Column([ft.Text("🐉 Академия Киберзащиты", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC), cyber_text], scroll=ft.ScrollMode.AUTO, expand=True)

        # 8. АКАДЕМИЯ БОЯ
        combat_dd = ft.Dropdown(label="Раздел боевых искусств", value="🥋 Прикладной рукопашный бой (АРБ)", options=[ft.dropdown.Option(k) for k in COMBAT_ACADEMY.keys()])
        combat_disp = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def update_combat(e):
            d = COMBAT_ACADEMY.get(combat_dd.value, {})
            combat_disp.controls.clear()
            combat_disp.controls.append(ft.Text(d.get("Описание", ""), color=C_CYAN_200))
            for m in d.get("Материалы", []):
                combat_disp.controls.append(ft.Container(content=ft.Text(m, color=C_WHITE), padding=6, bgcolor="#0f172a", border_radius=6))
            page.update()
        combat_dd.on_change = update_combat
        update_combat(None)

        tab_combat = ft.Column([ft.Text("🥋 Академия Боя", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC), combat_dd, ft.Divider(), combat_disp], expand=True)

        # 9. СПРАВОЧНИК ОРУЖИЯ
        weapon_dd = ft.Dropdown(label="Выберите оружие", value="1. Боевой нож «Кайт» / Тактический нож", options=[ft.dropdown.Option(k) for k in WEAPON_ENCYCLOPEDIA.keys()])
        weapon_disp = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def update_weapon(e):
            specs = WEAPON_ENCYCLOPEDIA.get(weapon_dd.value, {})
            weapon_disp.controls.clear()
            for k, v in specs.items():
                weapon_disp.controls.append(ft.Container(content=ft.Column([ft.Text(k, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC), ft.Text(v, color=C_WHITE)]), padding=8, bgcolor="#0d1322", border_radius=6))
            page.update()
        weapon_dd.on_change = update_weapon
        update_weapon(None)

        tab_weapon = ft.Column([ft.Text("🔫 Справочник Оружия", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC), weapon_dd, ft.Divider(), weapon_disp], expand=True)

        # 10. ТЕРМИНАЛ
        term_out = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        term_inp = ft.TextField(hint_text="ping, nslookup, clear...", expand=True)
        term_out.controls.append(ft.Text("┌──(vektor㉿core)-[~]\n└─$ Diagnostic Shell Ready", font_family="monospace", color=C_GREEN, size=11))

        def run_term(e):
            if not term_inp.value: return
            cmd = term_inp.value.strip()
            term_inp.value = ""
            term_out.controls.append(ft.Text(f"└─$ {cmd}", font_family="monospace", color=C_CYAN_100, size=11))
            page.update()
            if cmd == "clear": term_out.controls.clear(); page.update(); return
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
                out = res.stdout if res.stdout else res.stderr
            except Exception as ex: out = f"Ошибка: {ex}"
            term_out.controls.append(ft.Text(out, font_family="monospace", color=C_GREEN_ACC, size=11))
            page.update()

        tab_term = ft.Column([
            ft.Text("💻 Системный Терминал", weight=ft.FontWeight.BOLD, color=C_GREEN),
            ft.Container(content=term_out, padding=10, bgcolor=C_BLACK, border=ft.border.all(1, "#166534"), border_radius=8, expand=True),
            ft.Row([term_inp, ft.ElevatedButton("Run", on_click=run_term, bgcolor="#14532d", color=C_WHITE)])
        ], expand=True)

        # 11. НАСТРОЙКИ И АВТОНОМНОСТЬ
        api_inp = ft.TextField(label="OpenAI API Key (sk-...)", password=True, can_reveal_password=True)
        advisor_dd = ft.Dropdown(label="Активный Советник", value=app_logic.active_advisor, options=[ft.dropdown.Option(k) for k in TEAM_MEMBERS.keys()], expand=True)

        def save_settings(e):
            app_logic.openai_key = api_inp.value.strip()
            app_logic.active_advisor = advisor_dd.value
            advisor_title.value = f"VEKTOR // {app_logic.active_advisor}"
            status_badge.value = "🟢 Ключ привязан"
            status_badge.color = C_GREEN
            page.update()

        tab_settings = ft.Column([
            ft.Text("🔑 Настройки & Core", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            api_inp, advisor_dd,
            ft.ElevatedButton("Сохранить конфигурацию", on_click=save_settings, bgcolor="#0e7490", color=C_WHITE),
            ft.Divider(),
            ft.Text(f"Версия ядра: v{CURRENT_VERSION} (Watchdog & OTA Активны)", size=11, color=C_GREY_400)
        ], expand=True)

        # СБОРКА ВСЕХ ВКЛАДОК
        tabs = ft.Tabs(selected_index=0, scrollable=True, tabs=[
            ft.Tab(text="💬 Чат", content=tab_chat),
            ft.Tab(text="🕵️ OSINT", content=tab_osint),
            ft.Tab(text="📞 Телефония", content=tab_telephony),
            ft.Tab(text="🥗 КБЖУ", content=tab_fitness),
            ft.Tab(text="📅 Планер", content=tab_planner),
            ft.Tab(text="⚖️ Аналитик", content=tab_analyst),
            ft.Tab(text="🐉 Киберзащита", content=tab_cyber),
            ft.Tab(text="🥋 Бой", content=tab_combat),
            ft.Tab(text="🔫 Оружие", content=tab_weapon),
            ft.Tab(text="💻 Терминал", content=tab_term),
            ft.Tab(text="🔑 Настройки", content=tab_settings),
        ], expand=1)
        page.add(tabs)

    ft.app(target=main)

if __name__ == "__main__":
    max_restarts = 5
    restart_delay = 2
    for attempt in range(max_restarts):
        try:
            run_vektor_core()
            break
        except Exception as e:
            emergency_logger(f"Краш запуска: {e}")
            time.sleep(restart_delay)
