import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# ID папки Google Drive
GOOGLE_DRIVE_FOLDER = "16zcel9KNI8VMqoMtexwCS5Z0ydN-Qy5T"

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
        "description": "Вы фокусируетесь на себе и защищаете свои границы. Вы ищете глубокий личный смысл в работе и оберегаете свою аутентичность."
    },
    "1B": {
        "name": "Строитель Системы",
        "description": "Вы фокусируетесь на системе и защищаете её стабильность. Вы создаёте надёжные структуры и поддерживаете порядок."
    },
    "1C": {
        "name": "Первопроходец",
        "description": "Вы фокусируетесь на себе и стремитесь к экспансии. Вы смело идёте вперёд, открываете новые горизонты и расширяете свои возможности."
    },
    "1D": {
        "name": "Катализатор Роста",
        "description": "Вы фокусируетесь на системе и стремитесь к её расширению. Вы помогаете организациям расти и развиваться."
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

# Функция для получения прямой ссылки на файл из Google Drive
def get_tale_link(archetype, level):
    """Генерирует ссылку на сказку в Google Drive"""
    # Формат имени файла: 1A-Миссия.pdf
    filename = f"{archetype}-{LEVEL_NAMES[level]}.pdf"
    # Возвращаем ссылку на папку с инструкцией
    return f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER}\n\n📄 Найдите файл: **{filename}**"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы с ботом"""
    user = update.effective_user
    
    welcome_text = f"""
Привет, {user.first_name}! 👋

Я помогу тебе составить **Карту внутреннего мира** и найти точки роста в карьере.

🎯 **Что тебя ждёт:**

1️⃣ **Базовый тест** (16 вопросов)
   → Определим твой архетип

2️⃣ **Детальный тест** (30 вопросов)
   → Найдём проблемный уровень

3️⃣ **Персональная сказка**
   → Получишь инструмент для работы над собой

⏱ Займёт 10-15 минут

Готов начать?
"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Начать тест", callback_data="start_base_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# Начало базового теста
async def start_base_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает базовый тест"""
    query = update.callback_query
    await query.answer()
    
    # Инициализация данных пользователя
    context.user_data['base_answers'] = []
    context.user_data['current_question'] = 0
    
    await send_base_question(query, context)

# Отправка вопроса базового теста
async def send_base_question(query, context):
    """Отправляет текущий вопрос базового теста"""
    question_num = context.user_data['current_question']
    
    if question_num >= len(BASE_QUESTIONS):
        # Тест завершён, подсчитываем результат
        await calculate_archetype(query, context)
        return
    
    question = BASE_QUESTIONS[question_num]
    
    text = f"**Вопрос {question_num + 1} из {len(BASE_QUESTIONS)}**\n\n{question['text']}"
    
    keyboard = [
        [InlineKeyboardButton(option[0], callback_data=f"base_{option[1]}")] 
        for option in question['options']
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Обработка ответа на базовый тест
async def handle_base_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ на вопрос базового теста"""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем ответ
    answer = query.data.replace("base_", "")
    context.user_data['base_answers'].append(answer)
    context.user_data['current_question'] += 1
    
    await send_base_question(query, context)

# Подсчёт архетипа
async def calculate_archetype(query, context):
    """Определяет архетип на основе ответов"""
    answers = context.user_data['base_answers']
    
    # Подсчёт I vs S (первые 8 вопросов)
    i_count = sum(1 for a in answers[:8] if a == 'I')
    focus = 'I' if i_count >= 4 else 'S'
    
    # Подсчёт D vs E (вопросы 9-16)
    d_count = sum(1 for a in answers[8:] if a == 'D')
    strategy = 'D' if d_count >= 4 else 'E'
    
    # Определение архетипа
    if focus == 'I' and strategy == 'D':
        archetype = '1A'
    elif focus == 'S' and strategy == 'D':
        archetype = '1B'
    elif focus == 'I' and strategy == 'E':
        archetype = '1C'
    else:  # focus == 'S' and strategy == 'E'
        archetype = '1D'
    
    context.user_data['archetype'] = archetype
    
    # Отправка результата
    arch_info = ARCHETYPES[archetype]
    
    result_text = f"""
✅ **Базовый тест завершён!**

🎭 **Твой архетип: {arch_info['name']}**

{arch_info['description']}

Теперь давай найдём, на каком уровне у тебя есть точки роста.

Готов к детальному тесту?
"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Пройти детальный тест", callback_data="start_detailed_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Начало детального теста
async def start_detailed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает детальный тест"""
    query = update.callback_query
    await query.answer()
    
    # Инициализация
    context.user_data['detailed_answers'] = {level: [] for level in LEVEL_NAMES.keys()}
    context.user_data['current_level'] = list(LEVEL_NAMES.keys())[0]
    context.user_data['current_level_question'] = 0
    
    await send_detailed_question(query, context)

# Отправка вопроса детального теста
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
    
    text = f"""**Уровень: {LEVEL_NAMES[current_level]}**
Вопрос {question_num + 1} из 5

Прогресс: {answered}/{total_questions}

{questions[question_num]}

*Оцените от 1 до 5:*
1 = Совсем не согласен
5 = Полностью согласен"""
    
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"detailed_{i}")] 
        for i in range(1, 6)
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Обработка ответа на детальный тест
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

# Определение проблемного уровня
async def calculate_problem_level(query, context):
    """Определяет уровень с наименьшим баллом"""
    answers = context.user_data['detailed_answers']
    
    # Подсчёт среднего балла по каждому уровню
    averages = {level: sum(scores) / len(scores) for level, scores in answers.items()}
    
    # Находим уровень с минимальным баллом
    problem_level = min(averages, key=averages.get)
    problem_score = averages[problem_level]
    
    context.user_data['problem_level'] = problem_level
    
    archetype = context.user_data['archetype']
    
    result_text = f"""
✅ **Детальный тест завершён!**

📊 **Твои результаты по уровням:**

"""
    
    for level, score in sorted(averages.items(), key=lambda x: x[1]):
        emoji = "🔴" if level == problem_level else "🟢" if score >= 4 else "🟡"
        result_text += f"{emoji} **{LEVEL_NAMES[level]}**: {score:.1f}/5\n"
    
    result_text += f"""

🎯 **Точка роста: {LEVEL_NAMES[problem_level]}**

Сейчас я подберу для тебя персональную сказку, которая поможет проработать этот уровень.
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Получить сказку", callback_data="get_tale")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# Отправка сказки
async def send_tale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ссылку на сказку"""
    query = update.callback_query
    await query.answer()
    
    archetype = context.user_data['archetype']
    problem_level = context.user_data['problem_level']
    
    tale_link = get_tale_link(archetype, problem_level)
    
    text = f"""
🎉 **Твоя персональная сказка готова!**

🎭 Архетип: **{ARCHETYPES[archetype]['name']}**
🎯 Уровень: **{LEVEL_NAMES[problem_level]}**

{tale_link}

📚 **Как работать со сказкой:**

1. Прочитай сказку внимательно
2. Обрати внимание на метафоры
3. Подумай, как это связано с твоей ситуацией
4. Запиши инсайты

Хочешь пройти тест заново?
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти заново", callback_data="start_base_test")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Обработчик всех callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на кнопки"""
    query = update.callback_query
    data = query.data
    
    if data == "start_base_test":
        await start_base_test(update, context)
    elif data.startswith("base_"):
        await handle_base_answer(update, context)
    elif data == "start_detailed_test":
        await start_detailed_test(update, context)
    elif data.startswith("detailed_"):
        await handle_detailed_answer(update, context)
    elif data == "get_tale":
        await send_tale(update, context)

# Главная функция
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
    
    # Запуск бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
