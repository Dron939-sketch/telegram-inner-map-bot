import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
NAME, STAGE1, STAGE2, DETAILED_TEST = range(4)

# Конфигурация архетипов
ARCHETYPES = {
    '1A': {
        'name': '🛡️ ФИЛОСОФ-ОТШЕЛЬНИК',
        'description': 'Вы ищете ответы внутри себя и стремитесь к внутренней гармонии.',
        'emoji': '🛡️'
    },
    '1B': {
        'name': '⚔️ ВОИН-АТЛЕТ',
        'description': 'Вы фокусируетесь на себе и стремитесь к росту и достижениям.',
        'emoji': '⚔️'
    },
    '1C': {
        'name': '💰 ДИПЛОМАТ-ЦЕЛИТЕЛЬ',
        'description': 'Вы ищете своё место в системе и стремитесь к гармонии с миром.',
        'emoji': '💰'
    },
    '1D': {
        'name': '🔥 ЛИДЕР-РЕВОЛЮЦИОНЕР',
        'description': 'Вы видите несовершенство системы и стремитесь её изменить.',
        'emoji': '🔥'
    }
}

# Вопросы базового теста
STAGE1_QUESTIONS = [
    "Когда у вас возникает проблема, вы в первую очередь:\nA) Анализируете свои чувства и мысли\nB) Думаете, как это влияет на окружающих",
    "В конфликтной ситуации вы склонны:\nA) Уйти в себя и обдумать происходящее\nB) Активно искать решение, вовлекая других",
    "Ваши решения чаще основаны на:\nA) Личных убеждениях и внутреннем голосе\nB) Мнении окружающих и общепринятых нормах",
    "Когда вы думаете о будущем, вы представляете:\nA) Свой личный рост и развитие\nB) Своё место в обществе и влияние на мир",
    "В трудные моменты вы:\nA) Ищете ответы внутри себя\nB) Обращаетесь за поддержкой к другим",
    "Ваша главная мотивация:\nA) Понять себя и найти внутреннюю гармонию\nB) Изменить мир вокруг себя",
    "Вы чувствуете себя лучше, когда:\nA) Находитесь наедине с собой\nB) Взаимодействуете с людьми",
    "Ваши цели связаны с:\nA) Личным совершенствованием\nB) Влиянием на систему или общество"
]

STAGE2_QUESTIONS = [
    "В сложной ситуации вы склонны:\nA) Искать безопасность и стабильность\nB) Идти на риск ради возможностей",
    "Ваша стратегия в жизни:\nA) Сохранить то, что имею\nB) Завоевать новое",
    "Когда возникает угроза, вы:\nA) Защищаетесь и укрепляете границы\nB) Атакуете и расширяете влияние",
    "Ваши действия чаще направлены на:\nA) Сохранение ресурсов и энергии\nB) Активное использование возможностей",
    "В отношениях вы:\nA) Осторожны и избирательны\nB) Открыты и активны",
    "Ваш подход к изменениям:\nA) Принимаю только необходимые\nB) Активно инициирую новое",
    "Вы предпочитаете:\nA) Углублять существующее\nB) Расширять горизонты",
    "Ваша энергия направлена на:\nA) Защиту своего пространства\nB) Завоевание нового пространства"
]

# Вопросы детального теста
DETAILED_QUESTIONS = {
    'МИССИЯ': [
        "Я чувствую, что моя жизнь имеет глубокий смысл",
        "Я знаю, зачем я живу",
        "Моя жизненная цель ясна и вдохновляет меня",
        "Я чувствую связь с чем-то большим, чем я сам",
        "Мои действия соответствуют моему предназначению"
    ],
    'ИДЕНТИЧНОСТЬ': [
        "Я точно знаю, кто я",
        "Мне комфортно быть собой",
        "Я принимаю все свои стороны",
        "Моя самооценка стабильна",
        "Я чувствую целостность своей личности"
    ],
    'ЦЕННОСТИ': [
        "Мои ценности чётко определены",
        "Я живу в соответствии со своими ценностями",
        "Мои решения отражают то, что для меня важно",
        "Я не иду на компромисс с главными ценностями",
        "Мои ценности дают мне опору в жизни"
    ],
    'СПОСОБНОСТИ': [
        "Я знаю свои сильные стороны",
        "Я уверен в своих способностях",
        "Я эффективно использую свои навыки",
        "Я постоянно развиваю свои таланты",
        "Мои способности помогают мне достигать целей"
    ],
    'ПОВЕДЕНИЕ': [
        "Моё поведение соответствует моим целям",
        "Я действую последовательно",
        "Мои привычки поддерживают меня",
        "Я легко меняю поведение, когда нужно",
        "Мои действия приносят желаемые результаты"
    ],
    'ОКРУЖЕНИЕ': [
        "Моё окружение поддерживает меня",
        "Я нахожусь в правильном месте",
        "Люди вокруг меня вдохновляют",
        "Моя среда способствует моему росту",
        "Я чувствую себя на своём месте"
    ]
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 Начать тест", callback_data='start_test')],
        [InlineKeyboardButton("ℹ️ Узнать больше", callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 *Привет!*\n\n"
        "Я помогу найти твой внутренний архетип и \"узел\", где застряла твоя энергия.\n\n"
        "🎯 *Тест состоит из двух этапов:*\n"
        "1️⃣ Базовое сканирование (16 вопросов)\n"
        "2️⃣ Углублённое сканирование (30 вопросов)\n\n"
        "⏱ Займёт около 10 минут.\n\n"
        "Готов начать?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_test':
        await query.edit_message_text("📝 *Как тебя зовут?*", parse_mode='Markdown')
        return NAME
    
    elif query.data == 'info':
        await query.edit_message_text(
            "ℹ️ *О тесте*\n\n"
            "Этот тест основан на модели логических уровней Дилтса.\n\n"
            "Он поможет:\n"
            "• Определить твой внутренний архетип\n"
            "• Найти \"узел\" — уровень, где застряла энергия\n"
            "• Получить персональную терапевтическую сказку\n\n"
            "Отвечай честно — здесь нет правильных ответов.",
            parse_mode='Markdown'
        )
        
        keyboard = [[InlineKeyboardButton("🎯 Начать тест", callback_data='start_test')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Готов начать?", reply_markup=reply_markup)
        return ConversationHandler.END

# Получение имени
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    context.user_data['stage1_answers'] = []
    context.user_data['stage1_question'] = 0
    
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}! 😊\n\n"
        "🎯 *ЭТАП 1: ФОКУС*\n\n"
        "Сейчас будет 8 вопросов.\n"
        "Выбирай вариант, который ближе тебе.",
        parse_mode='Markdown'
    )
    
    return await ask_stage1_question(update, context)

# Задать вопрос этапа 1
async def ask_stage1_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_num = context.user_data['stage1_question']
    
    if question_num >= len(STAGE1_QUESTIONS):
        context.user_data['stage2_answers'] = []
        context.user_data['stage2_question'] = 0
        
        await update.message.reply_text(
            "✅ *Этап 1 завершён!*\n\n"
            "🎯 *ЭТАП 2: СТРАТЕГИЯ*\n\n"
            "Ещё 8 вопросов.",
            parse_mode='Markdown'
        )
        return await ask_stage2_question(update, context)
    
    keyboard = [
        [InlineKeyboardButton("A", callback_data='stage1_A')],
        [InlineKeyboardButton("B", callback_data='stage1_B')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"*Вопрос {question_num + 1} из 8:*\n\n{STAGE1_QUESTIONS[question_num]}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return STAGE1

# Обработка ответа этапа 1
async def stage1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    answer = query.data.split('_')[1]
    context.user_data['stage1_answers'].append(answer)
    context.user_data['stage1_question'] += 1
    
    await query.message.delete()
    
    # ИСПРАВЛЕНИЕ: создаём фейковый update для продолжения
    class FakeMessage:
        async def reply_text(self, text, reply_markup=None, parse_mode=None):
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    class FakeUpdate:
        def __init__(self):
            self.message = FakeMessage()
    
    fake_update = FakeUpdate()
    return await ask_stage1_question(fake_update, context)

# Задать вопрос этапа 2
async def ask_stage2_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_num = context.user_data['stage2_question']
    
    if question_num >= len(STAGE2_QUESTIONS):
        return await calculate_archetype(update, context)
    
    keyboard = [
        [InlineKeyboardButton("A", callback_data='stage2_A')],
        [InlineKeyboardButton("B", callback_data='stage2_B')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"*Вопрос {question_num + 1} из 8:*\n\n{STAGE2_QUESTIONS[question_num]}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return STAGE2

# Обработка ответа этапа 2
async def stage2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    answer = query.data.split('_')[1]
    context.user_data['stage2_answers'].append(answer)
    context.user_data['stage2_question'] += 1
    
    await query.message.delete()
    
    # ИСПРАВЛЕНИЕ: создаём фейковый update для продолжения
    class FakeMessage:
        async def reply_text(self, text, reply_markup=None, parse_mode=None):
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    class FakeUpdate:
        def __init__(self):
            self.message = FakeMessage()
    
    fake_update = FakeUpdate()
    return await ask_stage2_question(fake_update, context)

# Подсчёт архетипа
async def calculate_archetype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage1 = context.user_data['stage1_answers']
    stage2 = context.user_data['stage2_answers']
    
    score_A = stage1.count('A')
    score_B = stage1.count('B')
    score_C = stage2.count('A')
    score_D = stage2.count('B')
    
    if score_A > score_B and score_C > score_D:
        archetype = '1A'
    elif score_A > score_B and score_D > score_C:
        archetype = '1B'
    elif score_B > score_A and score_C > score_D:
        archetype = '1C'
    else:
        archetype = '1D'
    
    context.user_data['archetype'] = archetype
    
    message = (
        "✅ *РЕЗУЛЬТАТ БАЗОВОГО ТЕСТА*\n\n"
        f"🎯 Ваш архетип:\n*{ARCHETYPES[archetype]['name']}*\n\n"
        f"{ARCHETYPES[archetype]['description']}\n\n"
        f"📊 *Ваши баллы:*\n"
        f"• Фокус на себе: {score_A}/8\n"
        f"• Фокус на системе: {score_B}/8\n"
        f"• Защита: {score_C}/8\n"
        f"• Экспансия: {score_D}/8\n\n"
        f"🔍 *Хотите узнать ваш \"внутренний узел\"?*"
    )
    
    keyboard = [[InlineKeyboardButton("🔬 Углублённое сканирование", callback_data='detailed_test')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END

# Начало детального теста
async def start_detailed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['detailed_answers'] = {}
    context.user_data['current_level'] = 0
    context.user_data['current_question'] = 0
    
    levels = list(DETAILED_QUESTIONS.keys())
    for level in levels:
        context.user_data['detailed_answers'][level] = []
    
    await query.edit_message_text(
        "🔬 *УГЛУБЛЁННОЕ СКАНИРОВАНИЕ*\n\n"
        "30 вопросов по 6 уровням.\n"
        "Оцените каждое утверждение от 1 до 5.",
        parse_mode='Markdown'
    )
    
    # ИСПРАВЛЕНИЕ: создаём фейковый update
    class FakeMessage:
        async def reply_text(self, text, reply_markup=None, parse_mode=None):
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    class FakeUpdate:
        def __init__(self):
            self.message = FakeMessage()
    
    fake_update = FakeUpdate()
    return await ask_detailed_question(fake_update, context)

# Задать вопрос детального теста
async def ask_detailed_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    levels = list(DETAILED_QUESTIONS.keys())
    level_num = context.user_data['current_level']
    question_num = context.user_data['current_question']
    
    if level_num >= len(levels):
        return await calculate_detailed_results(update, context)
    
    level = levels[level_num]
    questions = DETAILED_QUESTIONS[level]
    
    if question_num >= len(questions):
        context.user_data['current_level'] += 1
        context.user_data['current_question'] = 0
        return await ask_detailed_question(update, context)
    
    total_question = level_num * 5 + question_num + 1
    
    keyboard = [
        [InlineKeyboardButton("1", callback_data='detailed_1'),
         InlineKeyboardButton("2", callback_data='detailed_2'),
         InlineKeyboardButton("3", callback_data='detailed_3'),
         InlineKeyboardButton("4", callback_data='detailed_4'),
         InlineKeyboardButton("5", callback_data='detailed_5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎯 *{level}*\n\n"
        f"*Вопрос {total_question}/30:*\n\n"
        f"{questions[question_num]}\n\n"
        f"1 - Не согласен | 5 - Согласен",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return DETAILED_TEST

# Обработка ответа детального теста
async def detailed_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    score = int(query.data.split('_')[1])
    
    levels = list(DETAILED_QUESTIONS.keys())
    level = levels[context.user_data['current_level']]
    
    context.user_data['detailed_answers'][level].append(score)
    context.user_data['current_question'] += 1
    
    await query.message.delete()
    
    # ИСПРАВЛЕНИЕ: создаём фейковый update
    class FakeMessage:
        async def reply_text(self, text, reply_markup=None, parse_mode=None):
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    class FakeUpdate:
        def __init__(self):
            self.message = FakeMessage()
    
    fake_update = FakeUpdate()
    return await ask_detailed_question(fake_update, context)

# Подсчёт результатов детального теста
async def calculate_detailed_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answers = context.user_data['detailed_answers']
    
    level_scores = {}
    for level, scores in answers.items():
        level_scores[level] = sum(scores)
    
    min_level = min(level_scores, key=level_scores.get)
    min_score = level_scores[min_level]
    
    archetype = context.user_data['archetype']
    
    message = "✅ *РЕЗУЛЬТАТ*\n\n"
    message += f"🎯 {ARCHETYPES[archetype]['name']}\n\n"
    message += "📊 *Баллы по уровням:*\n\n"
    
    for level, score in level_scores.items():
        emoji = '🔴' if level == min_level else '🟢'
        message += f"{emoji} {level}: {score}/25\n"
    
    message += f"\n🎯 *Ваш \"узел\": {min_level}* ({min_score}/25)\n\n"
    message += f"Это уровень, где застряла ваша энергия.\n\n"
    message += f"📖 Ваша персональная сказка: `{archetype}_{min_level}.pdf`"
    
    await update.message.reply_text(message, parse_mode='Markdown')
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменён. /start для начала.")
    return ConversationHandler.END

# Главная функция
def main():
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ BOT_TOKEN не найден!")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(button_handler, pattern='^(start_test|info)$')
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            STAGE1: [CallbackQueryHandler(stage1_answer, pattern='^stage1_')],
            STAGE2: [CallbackQueryHandler(stage2_answer, pattern='^stage2_')],
            DETAILED_TEST: [CallbackQueryHandler(detailed_answer, pattern='^detailed_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(start_detailed_test, pattern='^detailed_test$'))
    
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
