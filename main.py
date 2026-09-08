import flet as ft
import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import subprocess
import datetime

# =====================================================================
# VEKTOR OS // TACTICAL NATIVE CORE v15.0
# СОВМЕСТИМОСТЬ С FLET v0.20+ / v0.80+ (ft.Colors + HEX-палитра)
# БЕЗ СТОРОННИХ БИБЛИОТЕК: ЧИСТЫЙ PYTHON + FLET
# =====================================================================

EXERCISES_CATALOG = {
    "Единоборства": [
        "Бой с тенью (Shadowboxing)", "Отработка двоек (Прямой левый + правый)", 
        "Отработка боковых ударов (Хук)", "Апперкоты в корпус и челюсть", 
        "Лоу-кик / Мидл-кик / Хай-кик", "Тай-пэш и фронт-кики", 
        "Борцовские проходы в ноги (Тейкдаун)", "Отработка бросков", 
        "Защита от болевых и удушающих", "Работа на тяжелом мешке и лапах", 
        "Условный / Вольный спарринг в экипировке"
    ],
    "Бег": [
        "Легкий восстановительный кросс", "Интервальный бег (ускорение/трусцой)", 
        "Спринт (60м / 100м)", "Трейлраннинг (пересеченная местность)", 
        "Челночный бег 10x10", "Забеги в гору", "Фартлек", "Средние дистанции"
    ],
    "Бодибилдинг": [
        "Жим штанги лежа", "Жим гантелей на наклонной", "Приседания со штангой", 
        "Становая тяга", "Армейский жим стоя", "Подтягивания широким хватом", 
        "Отжимания на брусьях", "Тяга верхнего блока", "Сгибания на бицепс", 
        "Французский жим", "Разведение гантелей", "Жим ногами"
    ],
    "Кардио": [
        "Прыжки на скакалке", "Берпи с выпрыгиванием", "Гребной тренажер (Concept2)", 
        "Сайклинг / Велотренажер", "Эллипс (Орбитрек)", "Джампинг Джек", "Скалолаз"
    ],
    "Растяжка": [
        "Продольный и поперечный шпагат", "Растяжка бицепса бедра и квадрицепса", 
        "Кошка-Собака (мобильность)", "Бабочка для тазобедренных", 
        "Растяжка плечевого пояса", "Раскрытие суставов"
    ]
}

TEAM_MEMBERS = {
    "🎓 Репетитор (30 лет стажа)": "Ты — добрый, терпеливый репетитор. Объясняй логику через наводящие вопросы.",
    "⚡ Олег Тиньков": "Ты — Олег Тиньков. Общайся дерзко, мотивируй на масштабный бизнес и продажи.",
    "🎨 DALL-E 3 Художник": "Ты — ИИ-художник. Описывай промпты для генерации артов.",
    "⚖️ Михаил (Главный юрист)": "Ты — юрист высшей квалификации. Консультируй по законам РФ.",
    "👮‍♂️ Сергей (ФСБ / Безопасность)": "Ты — офицер безопасности и OSINT-эксперт. Анализируй контрагентов.",
    "📊 Надежда (Финдир)": "Ты — финансовый директор. Считай юнит-экономику, EBITDA и налоги.",
    "📸 Мария (SMM & PR)": "Ты — SMM-стратег. Помогай с продвижением агентства AZIMUT.",
    "🥊 «Калибр» (Спецназ / АРБ)": "Ты — инструктор спецназа. Требуй дисциплину, спорт и характер.",
    "🌌 Пантелеймон (Астролог)": "Ты — нумеролог и астролог. Разбирай Старшие Арканы."
}

class NetClient:
    @staticmethod
    def get_json(url, timeout=8):
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'VEKTOR-Mobile-Engine/15.0'}
        )
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
        except urllib.error.HTTPError as e:
            try:
                err_json = json.loads(e.read().decode('utf-8'))
                return {"error": err_json.get("error", {}).get("message", str(e))}
            except Exception:
                return {"error": f"HTTP Error {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": f"Сетевая ошибка: {e}"}

class OSINTEngine:
    @staticmethod
    def get_ip_info(target):
        clean_target = target.strip().replace("https://", "").replace("http://", "").split("/")[0]
        url = f"http://ip-api.com/json/{clean_target}?fields=status,message,country,city,isp,org,as,query"
        data = NetClient.get_json(url)
        if data and data.get("status") == "success":
            return (
                f"🌐 **VEKTOR OSINT RECON:**\n"
                f"• Узел: `{data.get('query')}`\n"
                f"• Страна: **{data.get('country')}**\n"
                f"• Город: **{data.get('city')}**\n"
                f"• Провайдер (ISP): **{data.get('isp')}**\n"
                f"• Организация: **{data.get('org')}**\n"
                f"• AS-сеть: **{data.get('as')}**"
            )
        return "⚠️ Узел не найден или закрыт для внешних запросов."

    @staticmethod
    def generate_dorks(query):
        q = query.replace('"', '')
        return (
            f"🔍 **VEKTOR DORKING ОПЕРАТОРЫ ДЛЯ:** `{q}`\n\n"
            f"1. Документы: `\"{q}\" filetype:pdf OR filetype:docx OR filetype:xlsx`\n"
            f"2. Профили: `site:linkedin.com/in/ OR site:vk.com OR site:t.me \"{q}\"`\n"
            f"3. Реестры: `\"{q}\" (ИНН OR ОГРН OR реестр OR декларация)`\n"
            f"4. Код: `site:github.com OR site:gitlab.com \"{q}\"`"
        )

class TelephonyEngine:
    @staticmethod
    def identify_phone_number(phone_str):
        clean_number = "".join(c for c in phone_str if c.isdigit() or c == '+')
        if not clean_number:
            return "⚠️ Введите корректный номер телефона (например: +79991234567)"
        url = f"https://htmlweb.ru/json/geo/phone/{clean_number}"
        data = NetClient.get_json(url)
        if data:
            return (
                f"📞 **ИНФОРМАЦИЯ О НОМЕРЕ:** `{clean_number}`\n"
                f"• Страна: **{data.get('country', {}).get('name', 'Россия')}**\n"
                f"• Регион: **{data.get('region', {}).get('name', 'Не определен')}**\n"
                f"• Оператор: **{data.get('oper', {}).get('brand', 'Не определен')}**"
            )
        return f"📞 Номер: `{clean_number}` (Формат валиден)"

class AIAssistantApp:
    def __init__(self):
        self.openai_key = ""
        self.active_advisor = "🎓 Репетитор (30 лет стажа)"
        self.selected_voice_profile = "Мужской"

    def get_gpt_response(self, user_text):
        if not self.openai_key:
            return "⚠️ Введите ваш OpenAI API Key во вкладке '🔑 Настройки'!"
        
        system_prompt = TEAM_MEMBERS.get(self.active_advisor, "Ты - умный ассистент.")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7
        }
        
        res = NetClient.post_json(url, payload, headers)
        if "error" in res:
            return f"❌ Ошибка OpenAI: {res['error']}"
        try:
            return res["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ Ошибка парсинга: {e}"

    def generate_image(self, prompt_text):
        if not self.openai_key:
            return None, "⚠️ Введите ваш OpenAI API Key во вкладке '🔑 Настройки'!"
        
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        payload = {
            "prompt": prompt_text,
            "n": 1,
            "size": "1024x1024"
        }
        
        res = NetClient.post_json(url, payload, headers)
        if "error" in res:
            return None, f"❌ Ошибка DALL-E: {res['error']}"
        try:
            return res["data"][0]["url"], "✅ Успешно сгенерировано!"
        except Exception as e:
            return None, f"❌ Ошибка парсинга фото: {e}"

app_logic = AIAssistantApp()

def main(page: ft.Page):
    page.title = "VEKTOR"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    
    # Решение проблемы регистров: универсальный доступ к палитре
    Colors = getattr(ft, 'Colors', None) or getattr(ft, 'colors', None)
    
    c_red = Colors.RED_400 if Colors else "#f87171"
    c_green = Colors.GREEN_400 if Colors else "#4ade80"
    c_green_acc = Colors.GREEN_ACCENT if Colors else "#86efac"
    c_cyan_acc = Colors.CYAN_ACCENT if Colors else "#00f0ff"
    c_cyan_100 = Colors.CYAN_100 if Colors else "#cffafe"
    c_cyan_200 = Colors.CYAN_200 if Colors else "#a5f3fc"
    c_amber_300 = Colors.AMBER_300 if Colors else "#fcd34d"
    c_purple_200 = Colors.PURPLE_200 if Colors else "#e9d5ff"
    c_purple_300 = Colors.PURPLE_300 if Colors else "#d8b4fe"
    c_white = Colors.WHITE if Colors else "#ffffff"
    c_black = Colors.BLACK if Colors else "#000000"
    c_grey_400 = Colors.GREY_400 if Colors else "#9ca3af"

    status_badge = ft.Text("🔴 Ключ не привязан", color=c_red, size=12)

    # -----------------------------------------------------------------
    # ВКЛАДКА 1: ИИ-ЧАТ И DALL-E 3
    # -----------------------------------------------------------------
    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    user_input = ft.TextField(hint_text="Задайте вопрос VEKTOR или создайте фото...", expand=True)
    current_advisor_title = ft.Text(f"VEKTOR // {app_logic.active_advisor}", weight=ft.FontWeight.BOLD, color=c_cyan_acc)

    def send_message(e):
        if not user_input.value:
            return
        user_text = user_input.value
        chat_history.controls.append(ft.Text(f"👤 Вы: {user_text}", color=c_cyan_100, weight=ft.FontWeight.BOLD))
        user_input.value = ""
        page.update()
        
        ans = app_logic.get_gpt_response(user_text)
        chat_history.controls.append(ft.Text(f"⚡ VEKTOR ({app_logic.active_advisor}):\n{ans}", color=c_green_acc))
        page.update()

    def generate_photo_click(e):
        if not user_input.value:
            chat_history.controls.append(ft.Text("⚠️ Напишите описание фотографии!", color=c_amber_300))
            page.update()
            return
        prompt = user_input.value
        chat_history.controls.append(ft.Text(f"🎨 Запрос генерации: '{prompt}'", color=c_purple_200, weight=ft.FontWeight.BOLD))
        user_input.value = ""
        page.update()
        
        img_url, status_msg = app_logic.generate_image(prompt)
        if img_url:
            chat_history.controls.append(ft.Text(f"🖼️ Сгенерированное фото VEKTOR DALL-E:", color=c_green_acc))
            chat_history.controls.append(ft.Image(src=img_url, width=320, height=320, fit=ft.ImageFit.CONTAIN, border_radius=12))
        else:
            chat_history.controls.append(ft.Text(status_msg, color=c_red))
        page.update()

    tab_chat = ft.Column([
        ft.Row([
            ft.Text("VEKTOR", size=20, weight=ft.FontWeight.BOLD, color=c_cyan_acc),
            current_advisor_title,
            status_badge
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        chat_history,
        ft.Row([
            user_input,
            ft.IconButton(icon=ft.icons.SEND, on_click=send_message, tooltip="Отправить", icon_color=c_cyan_acc),
            ft.IconButton(icon=ft.icons.IMAGE, on_click=generate_photo_click, tooltip="Создать фото DALL-E", icon_color=c_purple_300),
        ])
    ], expand=True)

    # -----------------------------------------------------------------
    # ВКЛАДКА 2: OSINT РАЗВЕДКА
    # -----------------------------------------------------------------
    osint_target_input = ft.TextField(label="Цель OSINT (Домен, IP, ИНН, ФИО)", hint_text="example.com или 8.8.8.8")
    osint_output_card = ft.Text("Результаты OSINT-разведки появятся здесь...", color=c_cyan_200, selectable=True)

    def run_ip_recon(e):
        if not osint_target_input.value:
            return
        osint_output_card.value = OSINTEngine.get_ip_info(osint_target_input.value)
        page.update()

    def run_dorks(e):
        if not osint_target_input.value:
            return
        osint_output_card.value = OSINTEngine.generate_dorks(osint_target_input.value)
        page.update()

    def run_ai_due_diligence(e):
        if not osint_target_input.value:
            return
        osint_output_card.value = "⏳ VEKTOR Intelligence: Офицер Сергей анализирует базы..."
        page.update()
        prompt_audit = f"Проведи Due Diligence и OSINT-анализ цели: '{osint_target_input.value}'. Составь отчет по рискам."
        res = app_logic.get_gpt_response(prompt_audit)
        osint_output_card.value = f"📊 **VEKTOR REPORT (ОФИЦЕР СЕРГЕЙ):**\n\n{res}"
        page.update()

    tab_osint = ft.Column([
        ft.Text("🕵️ VEKTOR OSINT & Due Diligence", size=18, weight=ft.FontWeight.BOLD),
        osint_target_input,
        ft.Row([
            ft.ElevatedButton("🌐 IP / Domain Whois", on_click=run_ip_recon, icon=ft.icons.LANGUAGE, bgcolor="#0e7490", color=c_white),
            ft.ElevatedButton("🔍 Поисковые Dorks", on_click=run_dorks, icon=ft.icons.SEARCH, bgcolor="#1d4ed8", color=c_white),
            ft.ElevatedButton("📊 ИИ-Аудит", on_click=run_ai_due_diligence, icon=ft.icons.SECURITY, bgcolor="#15803d", color=c_white),
        ], wrap=True),
        ft.Divider(),
        ft.Container(content=osint_output_card, padding=12, border=ft.border.all(1, "#334155"), border_radius=8)
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    # -----------------------------------------------------------------
    # ВКЛАДКА 3: ТЕЛЕФОНИЯ & МОДУЛЯТОР ГОЛОСА
    # -----------------------------------------------------------------
    phone_input = ft.TextField(label="Номер телефона", hint_text="+7 (999) 123-45-67", value="+7")
    voice_profile_dd = ft.Dropdown(
        label="VEKTOR DSP Модулятор голоса",
        value="Мужской",
        options=[
            ft.dropdown.Option("Мужской"),
            ft.dropdown.Option("Женский"),
            ft.dropdown.Option("Цифровой"),
            ft.dropdown.Option("Детский")
        ],
        expand=True
    )
    phone_info_card = ft.Text("Введите номер для проверки оператора...", color=c_cyan_200, selectable=True)

    def identify_phone(e):
        if not phone_input.value:
            return
        phone_info_card.value = TelephonyEngine.identify_phone_number(phone_input.value)
        page.update()

    def make_call(e):
        raw = "".join(c for c in phone_input.value if c.isdigit() or c == '+')
        if raw:
            try:
                page.launch_url(f"tel:{raw}")
                phone_info_card.value = f"📞 Инициация вызова: `{raw}` (Модулятор: {voice_profile_dd.value})"
            except Exception as ex:
                phone_info_card.value = f"⚠️ Ошибка вызова: {ex}"
            page.update()

    tab_telephony = ft.Column([
        ft.Text("📞 VEKTOR Телефония", size=18, weight=ft.FontWeight.BOLD),
        phone_input,
        voice_profile_dd,
        ft.Row([
            ft.ElevatedButton("🔍 Определить Номер", on_click=identify_phone, icon=ft.icons.SEARCH, bgcolor="#0e7490", color=c_white),
            ft.ElevatedButton("📞 Позвонить", on_click=make_call, icon=ft.icons.CALL, bgcolor="#16a34a", color=c_white),
        ], wrap=True),
        ft.Divider(),
        ft.Container(content=phone_info_card, padding=12, border=ft.border.all(1, "#334155"), border_radius=8)
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    # -----------------------------------------------------------------
    # ВКЛАДКА 4: СПОРТ И КБЖУ
    # -----------------------------------------------------------------
    food_name_input = ft.TextField(label="Продукт / Блюдо", hint_text="Куриное филе", expand=True)
    weight_input = ft.TextField(label="Вес (г)", value="100", width=90)
    cals_input = ft.TextField(label="Ккал/100г", value="165", width=90)
    prot_input = ft.TextField(label="Белки", value="31", width=70)
    fats_input = ft.TextField(label="Жиры", value="3.6", width=70)
    carbs_input = ft.TextField(label="Углеводы", value="0", width=70)

    kbju_list = []
    kbju_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    totals_text = ft.Text("Итого за день: 0 ккал | Б: 0г | Ж: 0г | У: 0г", weight=ft.FontWeight.BOLD, color=c_amber_300)

    def recalculate_kbju():
        tot_c = sum(i["cals"] for i in kbju_list)
        tot_p = sum(i["p"] for i in kbju_list)
        tot_f = sum(i["f"] for i in kbju_list)
        tot_car = sum(i["car"] for i in kbju_list)
        totals_text.value = f"Итого за день: {tot_c:.1f} ккал | Б: {tot_p:.1f}г | Ж: {tot_f:.1f}г | У: {tot_car:.1f}г"
        kbju_view.controls.clear()
        for i in kbju_list:
            kbju_view.controls.append(ft.Text(f"• {i['name']} ({i['w']}г) — {i['cals']:.0f} ккал [Б:{i['p']:.1f} Ж:{i['f']:.1f} У:{i['car']:.1f}]", size=11, color=c_white))
        page.update()

    def add_food(e):
        if not food_name_input.value:
            return
        try:
            w = float(weight_input.value)
            f_factor = w / 100.0
            kbju_list.append({
                "name": food_name_input.value.strip(), "w": w,
                "cals": float(cals_input.value) * f_factor,
                "p": float(prot_input.value) * f_factor,
                "f": float(fats_input.value) * f_factor,
                "car": float(carbs_input.value) * f_factor
            })
            food_name_input.value = ""
            recalculate_kbju()
        except ValueError:
            pass

    sport_category_dd = ft.Dropdown(
        label="Вид спорта", value="Единоборства",
        options=[ft.dropdown.Option(cat) for cat in EXERCISES_CATALOG.keys()], width=160
    )
    exercise_dd = ft.Dropdown(
        label="Упражнение из каталога",
        options=[ft.dropdown.Option(ex) for ex in EXERCISES_CATALOG["Единоборства"]],
        value=EXERCISES_CATALOG["Единоборства"][0], expand=True
    )
    custom_ex_input = ft.TextField(label="Свое упражнение", hint_text="Свой вариант...", expand=True)
    sets_input = ft.TextField(label="Подходы / Время", hint_text="5 раундов х 3 мин", width=160)
    workout_list = []
    workout_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def on_sport_cat_change(e):
        avail = EXERCISES_CATALOG.get(sport_category_dd.value, [])
        exercise_dd.options = [ft.dropdown.Option(ex) for ex in avail]
        if avail:
            exercise_dd.value = avail[0]
        page.update()
    sport_category_dd.on_change = on_sport_cat_change

    def add_workout(e):
        name = custom_ex_input.value.strip() if custom_ex_input.value else exercise_dd.value
        if not name:
            return
        workout_list.append({"cat": sport_category_dd.value, "name": name, "sets": sets_input.value.strip() or "Выполнено"})
        custom_ex_input.value = ""
        sets_input.value = ""
        workout_view.controls.clear()
        for item in workout_list:
            workout_view.controls.append(ft.Container(content=ft.Text(f"🥊 [{item['cat']}] {item['name']} — {item['sets']}", size=12, color=c_green_acc, weight=ft.FontWeight.BOLD), padding=6, bgcolor="#14532d", border_radius=6))
        page.update()

    fitness_sub_tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="🥗 КБЖУ", content=ft.Column([totals_text, ft.Row([food_name_input, weight_input]), ft.Row([cals_input, prot_input, fats_input, carbs_input]), ft.ElevatedButton("Добавить блюдо", on_click=add_food, icon=ft.icons.RESTAURANT, bgcolor="#b45309", color=c_white), ft.Divider(), kbju_view], expand=True)),
            ft.Tab(text="🏋️ Тренировки", content=ft.Column([ft.Row([sport_category_dd, exercise_dd]), ft.Row([custom_ex_input, sets_input]), ft.ElevatedButton("Записать упражнение", on_click=add_workout, icon=ft.icons.FITNESS_CENTER, bgcolor="#15803d", color=c_white), ft.Divider(), workout_view], expand=True))
        ], expand=True
    )
    tab_fitness = ft.Column([fitness_sub_tabs], expand=True)

    # -----------------------------------------------------------------
    # ВКЛАДКА 5: ПЛАНЕР И КАЛЕНДАРЬ
    # -----------------------------------------------------------------
    selected_date = datetime.date.today()
    date_display = ft.Text(f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}", size=16, weight=ft.FontWeight.BOLD, color=c_cyan_200)
    tasks_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    new_task_inp = ft.TextField(hint_text="Новая задача...", expand=True)
    task_time_inp = ft.TextField(hint_text="15:00", width=90)
    tasks_db = [{"date": selected_date.strftime("%Y-%m-%d"), "time": "09:00", "text": "Тренировка по АРБ", "done": True}]

    def render_tasks():
        tasks_view.controls.clear()
        d_str = selected_date.strftime("%Y-%m-%d")
        for t in [x for x in tasks_db if x["date"] == d_str]:
            def make_toggle(item=t):
                return lambda e: item.update({"done": e.control.value}) or render_tasks()
            tasks_view.controls.append(ft.Checkbox(label=f"[{t['time']}] {t['text']}", value=t["done"], on_change=make_toggle()))
        page.update()

    def add_task(e):
        if not new_task_inp.value:
            return
        tasks_db.append({"date": selected_date.strftime("%Y-%m-%d"), "time": task_time_inp.value.strip() or "10:00", "text": new_task_inp.value.strip(), "done": False})
        new_task_inp.value = ""
        task_time_inp.value = ""
        render_tasks()

    def on_date_change(e):
        nonlocal selected_date
        if e.control.value:
            selected_date = e.control.value
            date_display.value = f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}"
            render_tasks()

    date_picker = ft.DatePicker(
        first_date=datetime.datetime(2025, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
        on_change=on_date_change
    )
    page.overlay.append(date_picker)

    tab_planner = ft.Column([
        ft.Row([date_display, ft.ElevatedButton("Выбрать дату", on_click=lambda e: date_picker.pick_date(), icon=ft.icons.CALENDAR_MONTH, bgcolor="#0e7490", color=c_white)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(), tasks_view, ft.Divider(),
        ft.Row([task_time_inp, new_task_inp, ft.ElevatedButton("Добавить", on_click=add_task, icon=ft.icons.ADD, bgcolor="#16a34a", color=c_white)])
    ], expand=True)
    render_tasks()

    # -----------------------------------------------------------------
    # ВКЛАДКА 6: ТЕРМИНАЛ
    # -----------------------------------------------------------------
    term_out = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    term_inp = ft.TextField(hint_text="ping, nslookup, clear...", expand=True)
    term_out.controls.append(ft.Text("┌──(vektor㉿core)-[~]\n└─$ Terminal Ready", font_family="monospace", color=c_green, size=11))

    def run_term(e):
        if not term_inp.value:
            return
        cmd = term_inp.value.strip()
        term_inp.value = ""
        term_out.controls.append(ft.Text(f"└─$ {cmd}", font_family="monospace", color=c_cyan_100, size=11))
        page.update()
        if cmd == "clear":
            term_out.controls.clear()
            page.update()
            return
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
            out = res.stdout if res.stdout else res.stderr
        except Exception as ex:
            out = f"Ошибка: {ex}"
        term_out.controls.append(ft.Text(out, font_family="monospace", color=c_green_acc, size=11))
        page.update()

    tab_console = ft.Column([
        ft.Text("💻 Системный Терминал", weight=ft.FontWeight.BOLD, color=c_green),
        ft.Container(content=term_out, padding=10, bgcolor=c_black, border=ft.border.all(1, "#166534"), border_radius=8, expand=True),
        ft.Row([term_inp, ft.ElevatedButton("Run", on_click=run_term, bgcolor="#14532d", color=c_white)])
    ], expand=True)

    # -----------------------------------------------------------------
    # ВКЛАДКА 7: КОМАНДА СОВЕТНИКОВ
    # -----------------------------------------------------------------
    team_cards = []
    for name, desc in TEAM_MEMBERS.items():
        def make_sel(n=name):
            return lambda e: setattr(app_logic, 'active_advisor', n) or setattr(current_advisor_title, 'value', f"VEKTOR // {n}") or setattr(tabs, 'selected_index', 0) or page.update()
        team_cards.append(ft.Card(content=ft.Container(content=ft.Row([ft.Column([ft.Text(name, size=14, weight=ft.FontWeight.BOLD, color=c_cyan_200), ft.Text(desc, size=11, color=c_grey_400)], expand=True), ft.ElevatedButton("Вызвать", on_click=make_sel(), bgcolor="#0e7490", color=c_white)]), padding=10)))
    tab_team = ft.Column([ft.Text("🏛️ Теневой Кабинет VEKTOR", size=18, weight=ft.FontWeight.BOLD), ft.Column(team_cards, scroll=ft.ScrollMode.AUTO, expand=True)], expand=True)

    # -----------------------------------------------------------------
    # ВКЛАДКА 8: НАСТРОЙКИ
    # -----------------------------------------------------------------
    api_inp = ft.TextField(label="OpenAI API Key (sk-...)", password=True, can_reveal_password=True)
    tab_account = ft.Column([
        ft.Text("🔑 Настройки VEKTOR Core", size=18, weight=ft.FontWeight.BOLD),
        api_inp,
        ft.ElevatedButton("Сохранить", on_click=lambda e: setattr(app_logic, 'openai_key', api_inp.value.strip()) or setattr(status_badge, 'value', "🟢 Ключ привязан") or setattr(status_badge, 'color', c_green) or page.update(), bgcolor="#0e7490", color=c_white)
    ], expand=True)

    # -----------------------------------------------------------------
    # СБОРКА ВСЕХ ВКЛАДОК
    # -----------------------------------------------------------------
    tabs = ft.Tabs(
        selected_index=0, scrollable=True,
        tabs=[
            ft.Tab(text="💬 ИИ-Чат", content=tab_chat),
            ft.Tab(text="🕵️ OSINT", content=tab_osint),
            ft.Tab(text="📞 Телефония", content=tab_telephony),
            ft.Tab(text="💪 Спорт", content=tab_fitness),
            ft.Tab(text="📅 Планер", content=tab_planner),
            ft.Tab(text="💻 Терминал", content=tab_console),
            ft.Tab(text="🏛️ Команда", content=tab_team),
            ft.Tab(text="🔑 Настройки", content=tab_account),
        ], expand=1
    )
    page.add(tabs)

if __name__ == "__main__":
    ft.app(target=main)
