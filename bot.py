import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# ============================================
# ДАННЫЕ ТЕСТА
# ============================================

# Вопросы базового теста
BASE_QUESTIONS = [
    # Вопросы 1-8: Я vs Система
    {
        "text": "Когда вы думаете о своей карьере, что для вас важнее?",
        "options": [
            ("Мои личные цели и амбиции", "I"),
            ("Как я могу быть полезен команде/компании", "S")
        ]
    },
    {
        "text": "В сложной ситуации на работе вы скорее:",
        "options": [
            ("Полагаетесь на свои силы и опыт", "I"),
            ("Ищете поддержку у коллег и руководства", "S")
        ]
    },
    {
        "text": "Что вас больше мотивирует?",
        "options": [
            ("Личные достижения и рост", "I"),
            ("Вклад в общее дело", "S")
        ]
    },
    {
        "text": "При выборе проекта вы ориентируетесь на:",
        "options": [
            ("Свои интересы и развитие", "I"),
            ("Потребности организации", "S")
        ]
    },
    {
        "text": "Успех для вас — это когда:",
        "options": [
            ("Вы достигли своих целей", "I"),
            ("Команда достигла результата", "S")
        ]
    },
    {
        "text": "В конфликте на работе вы:",
        "options": [
            ("Отстаиваете свою позицию", "I"),
            ("Ищете компромисс для команды", "S")
        ]
    },
    {
        "text": "Вы чувствуете себя лучше, когда:",
        "options": [
            ("Работаете независимо", "I"),
            ("Работаете в команде", "S")
        ]
    },
    {
        "text": "Ваша карьера — это:",
        "options": [
            ("Мой личный путь", "I"),
            ("Часть большой системы", "S")
        ]
    },
    # Вопросы 9-16: Защита vs Экспансия
    {
        "text": "Когда появляется новая возможность, вы:",
        "options": [
            ("Осторожно оцениваете риски", "D"),
            ("Сразу хватаетесь за шанс", "E")
        ]
    },
    {
        "text": "В работе вы предпочитаете:",
        "options": [
            ("Стабильность и предсказуемость", "D"),
            ("Новые вызовы и эксперименты", "E")
        ]
    },
    {
        "text": "Когда что-то идёт не так:",
        "options": [
            ("Анализирую, что пошло не так", "D"),
            ("Быстро перехожу к новому плану", "E")
        ]
    },
    {
        "text": "Ваш подход к карьере:",
        "options": [
            ("Укреплять текущие позиции", "D"),
            ("Постоянно расширять горизонты", "E")
        ]
    },
    {
        "text": "В сложной ситуации вы:",
        "options": [
            ("Защищаете то, что имеете", "D"),
            ("Ищете новые пути", "E")
        ]
    },
    {
        "text": "Изменения на работе вы воспринимаете как:",
        "options": [
            ("Потенциальную угрозу", "D"),
            ("Возможность для роста", "E")
        ]
    },
    {
        "text": "Ваша стратегия:",
        "options": [
            ("Сохранять и улучшать", "D"),
            ("Захватывать и расширять", "E")
        ]
    },
    {
        "text": "Вы чувствуете себя комфортно, когда:",
        "options": [
            ("Всё под контролем", "D"),
            ("Есть пространство для роста", "E")
        ]
    }
]

# Детальные вопросы по уровням (по 5 на каждый)
DETAILED_QUESTIONS = {
    "mission": [
        "Я чётко понимаю свою миссию в карьере",
        "Моя работа наполнена смыслом",
        "Я знаю, ради чего я работаю",
        "Моя карьера связана с моим предназначением",
        "Я чувствую, что моя работа важна"
    ],
    "identity": [
        "Я знаю, кто я как профессионал",
        "Моя профессиональная идентичность чёткая",
        "Я понимаю свою роль в карьере",
        "Я уверен в своей профессиональной личности",
        "Моя работа отражает, кто я есть"
    ],
    "values": [
        "Мои ценности совпадают с моей работой",
        "Я не иду на компромисс с важными для меня вещами",
        "Моя работа соответствует моим принципам",
        "Я чувствую целостность в карьере",
        "Мои ценности поддерживают мою карьеру"
    ],
    "abilities": [
        "У меня есть нужные навыки для моей работы",
        "Я уверен в своих способностях",
        "Я развиваю свои компетенции",
        "Мои таланты используются в работе",
        "Я знаю свои сильные стороны"
    ],
    "behavior": [
        "Мои действия ведут к результатам",
        "Я регулярно делаю шаги к целям",
        "Моё поведение эффективно",
        "Я действую, а не откладываю",
        "Мои привычки поддерживают карьеру"
    ],
    "environment": [
        "Моё окружение поддерживает мою карьеру",
        "Условия работы мне подходят",
        "Люди вокруг меня помогают расти",
        "Среда способствует моему развитию",
        "Внешние условия благоприятны"
    ]
}

# Описания архетипов
ARCHETYPES = {
    "1A": {
        "name": "Искатель Смысла",
        "emoji": "🔍",
        "description": "Вы фокусируетесь на себе и защищаете свои границы. Вы ищете глубокий личный смысл в работе и оберегаете свою аутентичность.",
        "strengths": "Глубокая рефлексия, аутентичность, верность себе",
        "challenges": "Может быть сложно адаптироваться к внешним требованиям"
    },
    "1B": {
        "name": "Строитель Системы",
        "emoji": "🏗",
        "description": "Вы фокусируетесь на системе и защищаете её стабильность. Вы создаёте надёжные структуры и поддерживаете порядок.",
        "strengths": "Надёжность, системность, создание стабильности",
        "challenges": "Может быть сложно принимать быстрые изменения"
    },
    "1C": {
        "name": "Первопроходец",
        "emoji": "🚀",
        "description": "Вы фокусируетесь на себе и стремитесь к экспансии. Вы смело идёте вперёд, открываете новые горизонты и расширяете свои возможности.",
        "strengths": "Смелость, инициативность, готовность к риску",
        "challenges": "Может быть сложно учитывать интересы других"
    },
    "1D": {
        "name": "Катализатор Роста",
        "emoji": "🌱",
        "description": "Вы фокусируетесь на системе и стремитесь к её расширению. Вы помогаете организациям расти и развиваться.",
        "strengths": "Видение возможностей, развитие других, масштабирование",
        "challenges": "Может быть сложно сохранять баланс роста и стабильности"
    }
}

# Названия уровней
LEVEL_NAMES = {
    "mission": "Миссия",
    "identity": "Идентичность",
    "values": "Ценности",
    "abilities": "Способности",
    "behavior": "Поведение",
    "environment": "Окружение"
}

# Описания уровней
LEVEL_DESCRIPTIONS = {
    "mission": "Ваше предназначение и смысл в карьере",
    "identity": "Кто вы как профессионал",
    "values": "Что для вас важно в работе",
    "abilities": "Ваши навыки и компетенции",
    "behavior": "Ваши действия и привычки",
    "environment": "Ваше окружение и условия работы"
}

# Словарь с ID файлов сказок
TALE_FILES = {
    "1A": {
        "mission": "1WWmcf5t8aaUA_oIl0DR_xN_UKFwbIjp2",
        "identity": "1n39knulPxkqgmlnvuhajAJ_fZLYkq8iE",
        "values": "1rv36hmFDKOFB30ba-jETlsREwAIeS1ea",
        "abilities": "1jy2bN6zplfDrUAyGwbB3NwGCmh7qRE3Y",
        "behavior": "1qa4-krpY27m_q4ljtN4yH_TjH8mkp78-",
        "environment": "1dUcN3FCEtnXjKkzzUtslGbMrxDkcltgQ"
    },
    "1B": {
        "mission": "1QYVwcl_sWf-Ntpbp5En7lph1Sb-4v6R-",
        "identity": "1xcm7d8yPNB0e_fFucvVubpsKS6ZP7d-N",
        "values": "1OX2M-WODASA9RiwTosP97KrnWY-kdAOj",
        "abilities": "1nH8mls_DaiyZlNZU8m4tuS8zKjBYS14o",
        "behavior": "1_0tvaXMgH9aJ2xGM96WFT-14RPYpAlRs",
        "environment": "1iQKqlR2P_D4Dxqt4kbnRpER9gkgEdKRN"
    },
    "1C": {
        "mission": "1l1zH2nY4Ogd7QTU-uANU0v5FL6fReiCS",
        "identity": "1CP9GBpKwVJey8bteztJ0z1nrk8pLChzu",
        "values": "1ZSMGbKftI6mCIJGhBWEc-q0k8QBqpDAu",
        "abilities": "1UH7uvFvEtJG8h0J_ti0XUrEjprvqQ7bD",
        "behavior": "1JwVoO3MMl8rRaRttqJWqKHepJUdvbGWC",
        "environment": "13HRqpPfdToOGZHWodrnNt6xvfuhExRPL"
    },
    "1D": {
        "mission": "1jpJUSNO5Or2qdx2OxRMgBz2JkmVshlIz",
        "identity": "1DcaKOKK429QqUVJnlRb6K5fWkkICpJYr",
        "values": "1oZ5gT9Lh7OWGn8XR9LIrMxPV0z_ZuNnz",
        "abilities": "1uphOmKRdH3ga5sbTN18XlLJg6Gevx77b",
        "behavior": "1ccdEJaLoVxalnPMZPbd8UpqN3DeASGzo",
        "environment": "1SI8msDuxFRQRuDZouNxoi_jlCvi_FFu7"
    }
}

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_tale_link(archetype, level):
    """Генерирует прямую ссылку на сказку в Google Drive"""
    file_id = TALE_FILES[archetype][level]
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

def get_progress_bar(current, total, length=10):
    """Создаёт визуальную полосу прогресса"""
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {current}/{total}"

def escape_markdown(text):
    """Экранирует специальные символы для Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

# ============================================
# КОМАНДЫ БОТА
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы с ботом"""
    user = update.effective_user
    
    # Сброс данных пользователя
    context.user_data.clear()
    
    welcome_text = f"""Привет, {user.first_name}! 👋

Я помогу тебе составить Карту внутреннего мира и найти точки роста в карьере.

🎯 Что тебя ждёт:

1️⃣ Базовый тест (16 вопросов)
   → Определим твой архетип

2️⃣ Детальный тест (30 вопросов)
   → Найдём проблемный уровень

3️⃣ Персональная сказка
   → Получишь инструмент для работы над собой

⏱ Займёт 10-15 минут

Готов начать?"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Начать тест", callback_data="start_base_test")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о боте"""
    query = update.callback_query
    await query.answer()
    
    about_text = """📚 О боте

Этот бот основан на модели логических уровней Роберта Дилтса и помогает:

🔍 Определить ваш карьерный архетип
📊 Найти уровень, требующий развития
📖 Получить персональную сказку для работы над собой

Модель включает 6 уровней:
1. Миссия - ваше предназначение
2. Идентичность - кто вы
3. Ценности - что важно
4. Способности - ваши навыки
5. Поведение - ваши действия
6. Окружение - внешние условия

Готовы начать?"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Начать тест", callback_data="start_base_test")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(about_text, reply_markup=reply_markup)

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к стартовому экрану"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    welcome_text = f"""Привет, {user.first_name}! 👋

Я помогу тебе составить Карту внутреннего мира и найти точки роста в карьере.

🎯 Что тебя ждёт:

1️⃣ Базовый тест (16 вопросов)
   → Определим твой архетип

2️⃣ Детальный тест (30 вопросов)
   → Найдём проблемный уровень

3️⃣ Персональная сказка
   → Получишь инструмент для работы над собой

⏱ Займёт 10-15 минут

Готов начать?"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Начать тест", callback_data="start_base_test")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)

# ============================================
# БАЗОВЫЙ ТЕСТ
# ============================================

async def start_base_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает базовый тест"""
    query = update.callback_query
    await query.answer()
    
    # Инициализация данных пользователя
    context.user_data['base_answers'] = []
    context.user_data['current_question'] = 0
    context.user_data['test_start_time'] = update.callback_query.message.date
    
    intro_text = """🎯 БАЗОВЫЙ ТЕСТ

Сейчас я задам тебе 16 вопросов.

Отвечай честно, не думай долго - выбирай то, что ближе именно тебе.

Здесь нет правильных или неправильных ответов!

Готов?"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Начать", callback_data="begin_base_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

async def begin_base_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает задавать вопросы базового теста"""
    query = update.callback_query
    await query.answer()
    
    await send_base_question(query, context)

async def send_base_question(query, context):
    """Отправляет текущий вопрос базового теста"""
    question_num = context.user_data['current_question']
    
    if question_num >= len(BASE_QUESTIONS):
        await calculate_archetype(query, context)
        return
    
    question = BASE_QUESTIONS[question_num]
    
    # Прогресс-бар
    progress = get_progress_bar(question_num, len(BASE_QUESTIONS))
    
    # Определяем категорию вопроса
    if question_num < 8:
        category = "Фокус: Я vs Система"
    else:
        category = "Стратегия: Защита vs Экспансия"
    
    text = f"""📊 {category}

{progress}

❓ Вопрос {question_num + 1}:

{question['text']}"""
    
    keyboard = [
        [InlineKeyboardButton(option[0], callback_data=f"base_{option[1]}")] 
        for option in question['options']
    ]
    
    # Добавляем кнопку "Назад" (кроме первого вопроса)
    if question_num > 0:
        keyboard.append([InlineKeyboardButton("◀️ Предыдущий вопрос", callback_data="base_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_base_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на вопрос базового теста"""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем ответ
    answer = query.data.replace("base_", "")
    context.user_data['base_answers'].append(answer)
    context.user_data['current_question'] += 1
    
    await send_base_question(query, context)

async def handle_base_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к предыдущему вопросу базового теста"""
    query = update.callback_query
    await query.answer()
    
    if context.user_data['current_question'] > 0:
        context.user_data['current_question'] -= 1
        context.user_data['base_answers'].pop()
        await send_base_question(query, context)

async def calculate_archetype(query, context):
    """Определяет архетип на основе ответов"""
    answers = context.user_data['base_answers']
    
    # Подсчёт I vs S (первые 8 вопросов)
    i_count = sum(1 for a in answers[:8] if a == 'I')
    s_count = 8 - i_count
    focus = 'I' if i_count >= 4 else 'S'
    
    # Подсчёт D vs E (вопросы 9-16)
    d_count = sum(1 for a in answers[8:] if a == 'D')
    e_count = 8 - d_count
    strategy = 'D' if d_count >= 4 else 'E'
    
    # Определение архетипа
    if focus == 'I' and strategy == 'D':
        archetype = '1A'
    elif focus == 'S' and strategy == 'D':
        archetype = '1B'
    elif focus == 'I' and strategy == 'E':
        archetype = '1C'
    else:
        archetype = '1D'
    
    context.user_data['archetype'] = archetype
    context.user_data['focus_scores'] = {'I': i_count, 'S': s_count}
    context.user_data['strategy_scores'] = {'D': d_count, 'E': e_count}
    
    # Отправка результата
    arch_info = ARCHETYPES[archetype]
    
    result_text = f"""✅ БАЗОВЫЙ ТЕСТ ЗАВЕРШЁН!

{arch_info['emoji']} Твой архетип: {arch_info['name']}

{arch_info['description']}

📊 Твои результаты:

Фокус:
  • Я: {i_count}/8
  • Система: {s_count}/8

Стратегия:
  • Защита: {d_count}/8
  • Экспансия: {e_count}/8

💪 Твои сильные стороны:
{arch_info['strengths']}

⚠️ Зоны внимания:
{arch_info['challenges']}

Теперь давай найдём, на каком уровне у тебя есть точки роста.

Готов к детальному тесту?"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Пройти детальный тест", callback_data="start_detailed_test")],
        [InlineKeyboardButton("🔄 Пройти базовый тест заново", callback_data="start_base_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup)

# ============================================
# ДЕТАЛЬНЫЙ ТЕСТ
# ============================================

async def start_detailed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает детальный тест"""
    query = update.callback_query
    await query.answer()
    
    intro_text = """🎯 ДЕТАЛЬНЫЙ ТЕСТ

Сейчас я задам тебе 30 вопросов по 6 уровням (по 5 вопросов на каждый).

Оценивай каждое утверждение по шкале от 1 до 5:

1️⃣ - Совсем не согласен
2️⃣ - Скорее не согласен
3️⃣ - Нейтрально
4️⃣ - Скорее согласен
5️⃣ - Полностью согласен

Отвечай честно, как есть сейчас, а не как хотелось бы.

Готов?"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Начать", callback_data="begin_detailed_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

async def begin_detailed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает задавать вопросы детального теста"""
    query = update.callback_query
    await query.answer()
    
    # Инициализация
    context.user_data['detailed_answers'] = {level: [] for level in LEVEL_NAMES.keys()}
    context.user_data['current_level'] = list(LEVEL_NAMES.keys())[0]
    context.user_data['current_level_question'] = 0
    
    await send_detailed_question(query, context)

async def send_detailed_question(query, context):
    """Отправляет текущий вопрос детального теста"""
    current_level = context.user_data['current_level']
    question_num = context.user_data['current_level_question']
    
    questions = DETAILED_QUESTIONS[current_level]
    
    if question_num >= len(questions):
        # Переход к следующему уровню
        levels = list(LEVEL_NAMES.keys())
        current_index = levels.index(current_level)
        
        if current_index + 1 >= len(levels):
            # Все уровни пройдены
            await calculate_problem_level(query, context)
            return
        
        context.user_data['current_level'] = levels[current_index + 1]
        context.user_data['current_level_question'] = 0
        await send_detailed_question(query, context)
        return
    
    # Общий прогресс
    total_questions = len(LEVEL_NAMES) * 5
    answered = sum(len(answers) for answers in context.user_data['detailed_answers'].values())
    
    progress = get_progress_bar(answered, total_questions)
    
    text = f"""📊 Уровень: {LEVEL_NAMES[current_level]}

{LEVEL_DESCRIPTIONS[current_level]}

{progress}

❓ Вопрос {question_num + 1} из 5:

{questions[question_num]}

Оцените от 1 до 5:
1 = Совсем не согласен
5 = Полностью согласен"""
    
    keyboard = [
        [
            InlineKeyboardButton("1️⃣", callback_data="detailed_1"),
            InlineKeyboardButton("2️⃣", callback_data="detailed_2"),
            InlineKeyboardButton("3️⃣", callback_data="detailed_3"),
            InlineKeyboardButton("4️⃣", callback_data="detailed_4"),
            InlineKeyboardButton("5️⃣", callback_data="detailed_5")
        ]
    ]
    
    # Добавляем кнопку "Назад" (если не первый вопрос)
    if answered > 0:
        keyboard.append([InlineKeyboardButton("◀️ Предыдущий вопрос", callback_data="detailed_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_detailed_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на вопрос детального теста"""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем ответ
    score = int(query.data.replace("detailed_", ""))
    current_level = context.user_data['current_level']
    context.user_data['detailed_answers'][current_level].append(score)
    context.user_data['current_level_question'] += 1
    
    await send_detailed_question(query, context)

async def handle_detailed_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к предыдущему вопросу детального теста"""
    query = update.callback_query
    await query.answer()
    
    current_level = context.user_data['current_level']
    question_num = context.user_data['current_level_question']
    
    if question_num > 0:
        # Возврат в пределах текущего уровня
        context.user_data['current_level_question'] -= 1
        context.user_data['detailed_answers'][current_level].pop()
    else:
        # Возврат к предыдущему уровню
        levels = list(LEVEL_NAMES.keys())
        current_index = levels.index(current_level)
        
        if current_index > 0:
            prev_level = levels[current_index - 1]
            context.user_data['current_level'] = prev_level
            context.user_data['current_level_question'] = len(DETAILED_QUESTIONS[prev_level]) - 1
            context.user_data['detailed_answers'][prev_level].pop()
    
    await send_detailed_question(query, context)

async def calculate_problem_level(query, context):
    """Определяет уровень с наименьшим баллом"""
    answers = context.user_data['detailed_answers']
    
    # Подсчёт среднего балла по каждому уровню
    averages = {level: sum(scores) / len(scores) for level, scores in answers.items()}
    
    # Находим уровень с минимальным баллом
    problem_level = min(averages, key=averages.get)
    problem_score = averages[problem_level]
    
    context.user_data['problem_level'] = problem_level
    context.user_data['level_averages'] = averages
    
    archetype = context.user_data['archetype']
    
    result_text = f"""✅ ДЕТАЛЬНЫЙ ТЕСТ ЗАВЕРШЁН!

📊 Твои результаты по уровням:

"""
    
    # Сортируем уровни по баллу (от худшего к лучшему)
    for level, score in sorted(averages.items(), key=lambda x: x[1]):
        if level == problem_level:
            emoji = "🔴"
            status = "← ТОЧКА РОСТА"
        elif score >= 4.0:
            emoji = "🟢"
            status = "Отлично!"
        elif score >= 3.0:
            emoji = "🟡"
            status = "Хорошо"
        else:
            emoji = "🟠"
            status = "Требует внимания"
        
        result_text += f"{emoji} {LEVEL_NAMES[level]}: {score:.1f}/5 {status}\n"
    
    result_text += f"""

🎯 ТОЧКА РОСТА: {LEVEL_NAMES[problem_level]}

{LEVEL_DESCRIPTIONS[problem_level]}

Твой балл: {problem_score:.1f}/5

Сейчас я подберу для тебя персональную сказку, которая поможет проработать этот уровень.

Готов получить сказку?"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Получить сказку", callback_data="get_tale")],
        [InlineKeyboardButton("📊 Посмотреть детальную статистику", callback_data="show_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup)

# ============================================
# СТАТИСТИКА
# ============================================

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детальную статистику"""
    query = update.callback_query
    await query.answer()
    
    archetype = context.user_data['archetype']
    arch_info = ARCHETYPES[archetype]
    averages = context.user_data['level_averages']
    focus_scores = context.user_data['focus_scores']
    strategy_scores = context.user_data['strategy_scores']
    
    stats_text = f"""📊 ДЕТАЛЬНАЯ СТАТИСТИКА

{arch_info['emoji']} Архетип: {arch_info['name']}

📈 Базовый тест:

Фокус:
  • Я: {focus_scores['I']}/8 ({focus_scores['I']/8*100:.0f}%)
  • Система: {focus_scores['S']}/8 ({focus_scores['S']/8*100:.0f}%)

Стратегия:
  • Защита: {strategy_scores['D']}/8 ({strategy_scores['D']/8*100:.0f}%)
  • Экспансия: {strategy_scores['E']}/8 ({strategy_scores['E']/8*100:.0f}%)

📊 Детальный тест:

"""
    
    for level, score in sorted(averages.items(), key=lambda x: -x[1]):
        bar = "█" * int(score) + "░" * (5 - int(score))
        stats_text += f"{LEVEL_NAMES[level]}: {bar} {score:.1f}/5\n"
    
    overall_avg = sum(averages.values()) / len(averages)
    stats_text += f"\n📈 Общий балл: {overall_avg:.1f}/5"
    
    keyboard = [
        [InlineKeyboardButton("📖 Получить сказку", callback_data="get_tale")],
        [InlineKeyboardButton("◀️ Назад к результатам", callback_data="back_to_results")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup)

async def back_to_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к результатам теста"""
    query = update.callback_query
    await query.answer()
    
    await calculate_problem_level(query, context)

# ============================================
# СКАЗКА
# ============================================

async def send_tale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ссылку на сказку"""
    query = update.callback_query
    await query.answer()
    
    archetype = context.user_data['archetype']
    problem_level = context.user_data['problem_level']
    arch_info = ARCHETYPES[archetype]
    
    tale_link = get_tale_link(archetype, problem_level)
    
    text = f"""🎉 ТВОЯ ПЕРСОНАЛЬНАЯ СКАЗКА ГОТОВА!

{arch_info['emoji']} Архетип: {arch_info['name']}
🎯 Уровень: {LEVEL_NAMES[problem_level]}

📖 Читать сказку:
{tale_link}

📚 КАК РАБОТАТЬ СО СКАЗКОЙ:

1️⃣ Прочитай сказку внимательно, не спеша

2️⃣ Обрати внимание на:
   • Героев и их качества
   • Препятствия и способы их преодоления
   • Метафоры и символы

3️⃣ Задай себе вопросы:
   • Что в этой сказке про меня?
   • Какой герой мне ближе?
   • Какой урок я могу извлечь?

4️⃣ Запиши свои инсайты

5️⃣ Подумай о конкретных действиях

💡 Совет: перечитай сказку через неделю - ты увидишь новые смыслы!

Хочешь пройти тест заново или посмотреть статистику?"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Открыть сказку", url=tale_link)],
        [InlineKeyboardButton("📊 Посмотреть статистику", callback_data="show_stats")],
        [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="start_base_test")],
        [InlineKeyboardButton("💬 Оставить отзыв", callback_data="feedback")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

# ============================================
# ОБРАТНАЯ СВЯЗЬ
# ============================================

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос обратной связи"""
    query = update.callback_query
    await query.answer()
    
    feedback_text = """💬 ОБРАТНАЯ СВЯЗЬ

Мне важно твоё мнение!

Напиши, пожалуйста:
• Что тебе понравилось?
• Что можно улучшить?
• Помогла ли тебе сказка?

Просто напиши сообщение в чат, я его получу 📝"""
    
    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data="get_tale")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['waiting_for_feedback'] = True
    
    await query.edit_message_text(feedback_text, reply_markup=reply_markup)

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового отзыва"""
    if context.user_data.get('waiting_for_feedback'):
        user = update.effective_user
        feedback_text = update.message.text
        
        # Логируем отзыв
        logger.info(f"Feedback from {user.id} ({user.username}): {feedback_text}")
        
        # Благодарим пользователя
        thank_you_text = """🙏 Спасибо за отзыв!

Твоё мнение очень важно для улучшения бота.

Хочешь что-то ещё?"""
        
        keyboard = [
            [InlineKeyboardButton("📖 Вернуться к сказке", callback_data="get_tale")],
            [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="start_base_test")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['waiting_for_feedback'] = False
        
        await update.message.reply_text(thank_you_text, reply_markup=reply_markup)

# ============================================
# ОБРАБОТЧИК CALLBACK
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки"""
    query = update.callback_query
    data = query.data
    
    # Базовый тест
    if data == "start_base_test":
        await start_base_test(update, context)
    elif data == "begin_base_test":
        await begin_base_test(update, context)
    elif data.startswith("base_") and data != "base_back":
        await handle_base_answer(update, context)
    elif data == "base_back":
        await handle_base_back(update, context)
    
    # Детальный тест
    elif data == "start_detailed_test":
        await start_detailed_test(update, context)
    elif data == "begin_detailed_test":
        await begin_detailed_test(update, context)
    elif data.startswith("detailed_") and data != "detailed_back":
        await handle_detailed_answer(update, context)
    elif data == "detailed_back":
        await handle_detailed_back(update, context)
    
    # Результаты и сказка
    elif data == "get_tale":
        await send_tale(update, context)
    elif data == "show_stats":
        await show_stats(update, context)
    elif data == "back_to_results":
        await back_to_results(update, context)
    
    # Прочее
    elif data == "about":
        await about(update, context)
    elif data == "back_to_start":
        await back_to_start(update, context)
    elif data == "feedback":
        await feedback(update, context)

# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Запуск бота"""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    # Создание приложения
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_message))
    
    # Запуск бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
