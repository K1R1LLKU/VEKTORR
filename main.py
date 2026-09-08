import os
import sys
import time
import subprocess
import threading
import urllib.request
import urllib.parse
import json
import datetime
import traceback

# =====================================================================
# VEKTOR OS // ULTIMATE SUPREME TACTICAL & OSINT CORE v24.0
# ПОЛНЫЙ КОМПЛЕКС СО ВСЕМИ МОДУЛЯМИ, ИИ, OSINT, ЗАЩИТОЙ И OTA ОБНОВЛЕНИЕМ
# =====================================================================

VERSION_TAG = "24.0.0"
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
        req = urllib.request.Request(GITHUB_RAW_URL, headers={'User-Agent': 'VEKTOR-Watchdog/24.0'})
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
    "Единоборства": ["Бой с тенью (Shadowboxing)", "Отработка двоек", "Хуки", "Апперкоты", "Лоу-кик", "Тейкдаун", "Броски", "Спарринг"],
    "Бег": ["Легкий кросс", "Интервальный бег", "Спринт 100м", "Трейлраннинг", "Челночный бег"],
    "Бодибилдинг": ["Жим лежа", "Приседания", "Становая тяга", "Армейский жим", "Подтягивания", "Брусья"],
    "Кардио": ["Скакалка", "Берпи", "Гребля", "Велотренажер", "Эллипс"],
    "Растяжка": ["Шпагат", "Растяжка ног", "Мобильность", "Бабочка"]
}

COMBAT_ACADEMY = {
    "🥋 Прикладной рукопашный бой (АРБ)": {
        "Описание": "Система выживания и нейтрализации противника в контактном столкновении.",
        "Материалы": ["📖 Книга: «Армейский рукопашный бой» (Кадочников А.А.)", "📖 Статья: Ударная техника коленями и локтями", "🎥 Видео: Базовые принципы нокаутирующего удара"]
    },
    "🥊 Тактики тренировок великих боксёров": {
        "Описание": "Секреты выносливости и работы ног легенд ринга (Тайсон, Али, Мейвезер).",
        "Материалы": ["📖 Книга: «Бескомпромиссный бокс: Система Майка Тайсона»", "📖 Статья: Работа на тяжелом мешке по методике Кас Д’Амато", "🎥 Видео: Разбор защиты Philly Shell"]
    },
    "🗡️ Ножевой бой и самооборона": {
        "Описание": "Тактика ближней дистанции, психология схватки и защита от угроз.",
        "Материалы": ["📖 Книга: «Боевой нож» (Кондратьев А.)", "📖 Статья: Анатомия порезов и уколов", "🎥 Видео: Хваты ножа и уходы с линии атаки"]
    }
}

WEAPON_ENCYCLOPEDIA = {
    "1. Боевой нож «Кайт» / Тактический нож": {
        "1. Убийственная мощь": "Высокая (глубокие проникающие колотые раны).",
        "2. На сколько хорош в охоте": "Средний (удобен для разделки туш, но коротковат).",
        "3. Длинна лезвия/Калибр": "Длина лезвия: 140–160 мм.",
        "4. Практичность": "Максимальная (компактен, крепится на разгрузку).",
        "5. Где и когда можно применить": "В спецоперациях, выживании, полевом быту.",
        "6. Как правильно ухаживать": "Промывать после влаги, править на бруске, смазывать маслом.",
        "7. Хорош или плох в ножевом бою или дуэли, и почему?": "Отличен (имеет гарду, цельнометаллический full-tang).",
        "8. Запрещен на территории РФ или нет?": "Зависит от сертификата ХозБыт (толщина обуха и гарда)."
    },
    "2. Автомат Калашникова (АК-74М)": {
        "1. Убийственная мощь": "Критическая (высокая энергия пули 5.45х39 мм).",
        "2. На сколько хорош в охоте": "Плохой (слишком мощный патрон портит дичь).",
        "3. Длинна лезвия/Калибр": "Калибр: 5.45х39 мм.",
        "4. Практичность": "Легендарная (работает в грязи, воде и при экстремальных температурах).",
        "5. Где и когда можно применить": "В войсковых конфликтах, охране периметра.",
        "6. Как правильно ухаживать": "Чистка и смазка ствола после стрельбы.",
        "7. Хорош или плох в ножевом бою или дуэли, и почему?": "На дальней дистанции — абсолютное превосходство.",
        "8. Запрещен на территории РФ или нет?": "Боевой запрещен. Гражданские карабины (Сайга) разрешены по лицензии."
    }
}

TEAM_MEMBERS = {
    "👮‍♂️ Сергей (ФСБ / Безопасность & OSINT)": "Ты — офицер безопасности и эксперт по легальному Due Diligence и защите систем.",
    "⚖️ Михаил (Главный юрист РФ)": "Ты — корпоративный юрист. Консультируй по законам РФ, арбитражу и ответственности.",
    "🥊 «Калибр» (Спецназ / АРБ)": "Ты — инструктор спецназа, эксперт по рукопашному бою и тактике.",
    "⚡ Олег Тиньков": "Ты — Олег Тиньков. Мотивируй на масштабный бизнес и продажи.",
    "🎓 Репетитор (30 лет стажа)": "Ты — терпеливый репетитор. Объясняй логику через наводящие вопросы."
}

# --- МОДУЛЬ ЛЕГАЛЬНОЙ РАЗВЕДКИ (LEGAL OSINT) ---
class LegalOSINTEngine:
    @staticmethod
    def get_ip_dns_intel(target):
        clean = target.strip().replace("https://", "").replace("http://", "").split("/")[0]
        url = f"http://ip-api.com/json/{clean}?fields=status,message,country,city,isp,org,as,query"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'VEKTOR-OSINT/24.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("status") == "success":
                    return (
                        f"🌐 **СЕТЕВОЙ ИНФРАСТРУКТУРНЫЙ ПАСПОРТ:** `{data.get('query')}`\n\n"
                        f"• **Страна:** {data.get('country')}\n"
                        f"• **Город:** {data.get('city')}\n"
                        f"• **Провайдер (ISP):** {data.get('isp')}\n"
                        f"• **Организация:** {data.get('org')}\n"
                        f"• **Автономная система (AS):** {data.get('as')}\n"
                        f"• **Архив версий (Wayback):** `https://web.archive.org/web/*/{clean}`\n"
                        f"• **Сертификаты SSL (crt.sh):** `https://crt.sh/?q={clean}`"
                    )
        except Exception as ex:
            return f"❌ Ошибка сетевого запроса: {ex}"
        return "⚠️ Узел не найден или закрыт для внешних запросов."

    @staticmethod
    def get_company_due_diligence_links(inn_or_name):
        q = inn_or_name.strip()
        return (
            f"🏛️ **ОФИЦИАЛЬНЫЕ РЕЕСТРЫ ДЛЯ ПРОВЕРКИ КОНТРАГЕНТА:** `{q}`\n\n"
            f"1. **ФНС РФ (ЕГРЮЛ/ЕГРИП):** https://egrul.nalog.ru/\n"
            f"2. **Арбитражные суды РФ:** https://kad.arbitr.ru/\n"
            f"3. **Банкротства (Федресурс):** https://bankrot.fedresurs.ru/\n"
            f"4. **ФССП (Исполнительные производства):** https://fssp.gov.ru/iss/ip/\n"
            f"5. **Госзакупки:** https://zakupki.gov.ru/"
        )

    @staticmethod
    def generate_advanced_dorks(query):
        q = query.replace('"', '').strip()
        return (
            f"🔍 **ПОИСКОВЫЕ СВЯЗКИ (DORKS) ДЛЯ:** `{q}`\n\n"
            f"• Документы: `\"{q}\" filetype:pdf OR filetype:xlsx (отчет OR договор)`\n"
            f"• Реестры: `\"{q}\" (ИНН OR ОГРН OR арбитраж)`\n"
            f"• Профили: `site:linkedin.com/in/ OR site:vk.com \"{q}\"`"
        )

# --- ГЛАВНОЕ ПРИЛОЖЕНИЕ ---
def run_vektor_core():
    import flet as ft

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
    C_PURPLE_300 = SafeUI.color('PURPLE_300', '#d8b4fe')
    C_WHITE = SafeUI.color('WHITE', '#ffffff')
    C_BLACK = SafeUI.color('BLACK', '#000000')
    C_GREY_400 = SafeUI.color('GREY_400', '#9ca3af')

    ICON_SEND = SafeUI.icon('SEND', 'send')
    ICON_IMAGE = SafeUI.icon('IMAGE', 'image')
    ICON_SEARCH = SafeUI.icon('SEARCH', 'search')
    ICON_SECURITY = SafeUI.icon('SECURITY', 'security')
    ICON_LANGUAGE = SafeUI.icon('LANGUAGE', 'language')
    ICON_CALL = SafeUI.icon('CALL', 'call')
    ICON_RESTAURANT = SafeUI.icon('RESTAURANT', 'restaurant')
    ICON_FITNESS = SafeUI.icon('FITNESS_CENTER', 'fitness_center')
    ICON_CALENDAR = SafeUI.icon('CALENDAR_MONTH', 'calendar_month')
    ICON_ADD = SafeUI.icon('ADD', 'add')
    ICON_REFRESH = SafeUI.icon('REFRESH', 'refresh')

    class NetClient:
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
            self.active_advisor = "👮‍♂️ Сергей (ФСБ / Безопасность & OSINT)"

        def get_gpt_response(self, user_text):
            if not self.openai_key:
                return "⚠️ Введите ваш OpenAI API Key во вкладке '🔑 Настройки'!"
            sys_prompt = TEAM_MEMBERS.get(self.active_advisor, "Ты помощник.")
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

        # Фоновый OTA чекер
        def background_ota():
            if download_latest_core():
                try:
                    page.snack_bar = ft.SnackBar(ft.Text("✅ Успешное OTA обновление VEKTOR!"), open=True)
                    page.update()
                except Exception:
                    pass
        threading.Thread(target=background_ota, daemon=True).start()

        # 1. ЧАТ И DALL-E
        chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        user_input = ft.TextField(hint_text="Задайте вопрос VEKTOR или создайте картинку...", expand=True)
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
            p = user_input.value
            chat_history.controls.append(ft.Text(f"🎨 Запрос генерации: '{p}'", color=C_PURPLE_300, weight=ft.FontWeight.BOLD))
            user_input.value = ""
            page.update()
            url, msg = app_logic.generate_image(p)
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

        # 2. OSINT & РЕЕСТРЫ
        target_inp = ft.TextField(label="Цель (Домен, IP, ИНН или Название)", hint_text="8.8.8.8 или 7707083893", expand=True)
        osint_out = ft.Text("Результаты легальной разведки появятся здесь...", color=C_CYAN_200, selectable=True)

        def run_net_recon(e):
            if not target_inp.value: return
            osint_out.value = LegalOSINTEngine.get_ip_dns_intel(target_inp.value)
            page.update()

        def run_reg_check(e):
            if not target_inp.value: return
            osint_out.value = LegalOSINTEngine.get_company_due_diligence_links(target_inp.value)
            page.update()

        def run_dorks(e):
            if not target_inp.value: return
            osint_out.value = LegalOSINTEngine.generate_advanced_dorks(target_inp.value)
            page.update()

        def run_ai_dd(e):
            if not target_inp.value: return
            osint_out.value = "⏳ Офицер Сергей проводит Due Diligence анализ..."
            page.update()
            res = app_logic.get_gpt_response(f"Проведи легальный Due Diligence аудит цели: '{target_inp.value}'. Оцени риски и надежность.")
            osint_out.value = f"📊 **ОТЧЕТ АУДИТА:**\n\n{res}"
            page.update()

        tab_osint = ft.Column([
            ft.Text("🌐 Легальная Разведка & Реестры", size=18, weight=ft.FontWeight.BOLD, color=C_CYAN_ACC),
            target_inp,
            ft.Row([
                ft.ElevatedButton("🌐 Сеть & DNS", on_click=run_net_recon, icon=ICON_LANGUAGE, bgcolor="#0e7490", color=C_WHITE),
                ft.ElevatedButton("🏛️ Реестры РФ", on_click=run_reg_check, icon=ICON_SECURITY, bgcolor="#1d4ed8", color=C_WHITE),
                ft.ElevatedButton("🔍 Dorks", on_click=run_dorks, icon=ICON_SEARCH, bgcolor="#0891b2", color=C_WHITE),
                ft.ElevatedButton("📊 ИИ Due Diligence", on_click=run_ai_dd, icon=ICON_SECURITY, bgcolor="#15803d", color=C_WHITE),
            ], wrap=True),
            ft.Divider(),
            ft.Container(content=osint_out, padding=10, bgcolor="#060913", border=ft.border.all(1, "#1e293b"), border_radius=8, expand=True)
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        # 3. КБЖУ И СПОРТ
        food_inp = ft.TextField(label="Продукт", hint_text="Куриная грудка", expand=True)
        w_inp = ft.TextField(label="Вес (г)", value="100", width=80)
        cals_inp = ft.TextField(label="Ккал", value="165", width=80)
        kbju_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        kbju_list = []

        def add_food(e):
            if not food_inp.value: return
            try:
                w = float(w_inp.value)
                c = float(cals_inp.value) * (w / 100.0)
                kbju_list.append(f"• {food_inp.value} ({w}г) — {c:.0f} ккал")
                food_inp.value = ""
                kbju_view.controls.clear()
                for item in kbju_list: kbju_view.controls.append(ft.Text(item, color=C_WHITE, size=12))
                page.update()
            except ValueError: pass

        sport_cat_dd = ft.Dropdown(label="Спорт", value="Единоборства", options=[ft.dropdown.Option(k) for k in EXERCISES_CATALOG.keys()], width=150)
        ex_dd = ft.Dropdown(label="Упражнение", options=[ft.dropdown.Option(x) for x in EXERCISES_CATALOG["Единоборства"]], value=EXERCISES_CATALOG["Единоборства"][0], expand=True)
        workout_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        workout_list = []

        def add_workout(e):
            workout_list.append(f"🥊 [{sport_cat_dd.value}] {ex_dd.value}")
            workout_view.controls.clear()
            for w in workout_list: workout_view.controls.append(ft.Text(w, color=C_GREEN_ACC, size=12))
            page.update()

        tab_fitness = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="🥗 КБЖУ", content=ft.Column([ft.Row([food_inp, w_inp, cals_inp]), ft.ElevatedButton("Добавить", on_click=add_food, icon=ICON_RESTAURANT, bgcolor="#b45309", color=C_WHITE), ft.Divider(), kbju_view], expand=True)),
            ft.Tab(text="🏋️ Тренировки", content=ft.Column([ft.Row([sport_cat_dd, ex_dd]), ft.ElevatedButton("Записать", on_click=add_workout, icon=ICON_FITNESS, bgcolor="#15803d", color=C_WHITE), ft.Divider(), workout_view], expand=True))
        ], expand=True)

        # 4. АКАДЕМИЯ БОЯ И ОРУЖИЕ
        combat_dd = ft.Dropdown(label="Раздел боя", value="🥋 Прикладной рукопашный бой (АРБ)", options=[ft.dropdown.Option(k) for k in COMBAT_ACADEMY.keys()], expand=True)
        combat_txt = ft.Text(COMBAT_ACADEMY["🥋 Прикладной рукопашный бой (АРБ)"]["Описание"], color=C_CYAN_100, size=13)
        weapon_dd = ft.Dropdown(label="Справочник оружия", value="1. Боевой нож «Кайт» / Тактический нож", options=[ft.dropdown.Option(k) for k in WEAPON_ENCYCLOPEDIA.keys()], expand=True)
        weapon_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def render_weapon(e):
            weapon_view.controls.clear()
            for k, v in WEAPON_ENCYCLOPEDIA.get(weapon_dd.value, {}).items():
                weapon_view.controls.append(ft.Text(f"• {k}: {v}", color=C_WHITE, size=12))
            page.update()
        weapon_dd.on_change = render_weapon
        render_weapon(None)

        tab_combat_weapon = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="🥋 Академия Боя", content=ft.Column([combat_dd, combat_txt], expand=True)),
            ft.Tab(text="🔫 Оружие", content=ft.Column([weapon_dd, ft.Divider(), weapon_view], expand=True))
        ], expand=True)

        # 5. ТЕРМИНАЛ И НАСТРОЙКИ
        term_out = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        term_inp = ft.TextField(hint_text="ping, nslookup, clear...", expand=True)
        term_out.controls.append(ft.Text("┌──(vektor㉿core)-[~]\n└─$ Terminal Ready", font_family="monospace", color=C_GREEN, size=11))

        def run_term(e):
            if not term_inp.value: return
            cmd = term_inp.value.strip()
            term_inp.value = ""
            term_out.controls.append(ft.Text(f"└─$ {cmd}", font_family="monospace", color=C_CYAN_100, size=11))
            page.update()
            if cmd == "clear":
                term_out.controls.clear()
                page.update()
                return
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
                out = res.stdout if res.stdout else res.stderr
            except Exception as ex: out = f"Ошибка: {ex}"
            term_out.controls.append(ft.Text(out, font_family="monospace", color=C_GREEN_ACC, size=11))
            page.update()

        tab_terminal = ft.Column([
            ft.Text("💻 Системный Терминал", weight=ft.FontWeight.BOLD, color=C_GREEN),
            ft.Container(content=term_out, padding=10, bgcolor=C_BLACK, border=ft.border.all(1, "#166534"), border_radius=8, expand=True),
            ft.Row([term_inp, ft.ElevatedButton("Run", on_click=run_term, bgcolor="#14532d", color=C_WHITE)])
        ], expand=True)

        api_inp = ft.TextField(label="OpenAI API Key (sk-...)", password=True, can_reveal_password=True)
        tab_settings = ft.Column([
            ft.Text("🔑 Настройки VEKTOR Core", size=18, weight=ft.FontWeight.BOLD),
            api_inp,
            ft.ElevatedButton("Сохранить ключ", on_click=lambda e: setattr(app_logic, 'openai_key', api_inp.value.strip()) or setattr(status_badge, 'value', "🟢 Ключ привязан") or setattr(status_badge, 'color', C_GREEN) or page.update(), bgcolor="#0e7490", color=C_WHITE),
            ft.Divider(),
            ft.ElevatedButton("🔄 Принудительное OTA обновление", on_click=lambda e: download_latest_core() and page.update(), icon=ICON_REFRESH, bgcolor="#1e293b", color=C_CYAN_ACC),
            ft.Text(f"Версия ядра: v{CURRENT_VERSION} (Ultimate Supreme Core)", size=11, color=C_GREY_400)
        ], expand=True)

        # СБОРКА ВСЕХ ВКЛАДОК
        tabs = ft.Tabs(selected_index=0, scrollable=True, tabs=[
            ft.Tab(text="💬 ИИ-Чат", content=tab_chat),
            ft.Tab(text="🌐 Разведка", content=tab_osint),
            ft.Tab(text="🥗 Спорт & КБЖУ", content=tab_fitness),
            ft.Tab(text="🥋 Бой & Оружие", content=tab_combat_weapon),
            ft.Tab(text="💻 Терминал", content=tab_terminal),
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
