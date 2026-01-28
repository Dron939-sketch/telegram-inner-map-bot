import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
HRB, STAGE1, STAGE2, DETAILED_TEST = range(4)

# Вопросы для первого этапа (ХРБ)
STAGE1_QUESTIONS = [
    {
        'text': '1. Вам нравится работать с людьми?',
        'options': [
            ('Да, очень нравится', 5),
            ('Скорее да', 3),
            ('Не знаю', 0),
            ('Скорее нет', -3),
            ('Нет, не нравится', -5)
        ]
    },
    {
        'text': '2. Вы предпочитаете работать с данными и цифрами?',
        'options': [
            ('Да, очень нравится', 5),
            ('Скорее да', 3),
            ('Не знаю', 0),
            ('Скорее нет', -3),
            ('Нет, не нравится', -5)
        ]
    },
    {
        'text': '3. Вам интересно создавать что-то своими руками?',
        'options': [
            ('Да, очень интересно', 5),
            ('Скорее да', 3),
            ('Не знаю', 0),
            ('Скорее нет', -3),
            ('Нет, не интересно', -5)
        ]
    },
    {
        'text': '4. Вы любите исследовать и анализировать?',
        'options': [
            ('Да, очень люблю', 5),
            ('Скорее да', 3),
            ('Не знаю', 0),
            ('Скорее нет', -3),
            ('Нет, не люблю', -5)
        ]
    },
    {
        'text': '5. Вам нравится творческая работа?',
        'options': [
            ('Да, очень нравится', 5),
            ('Скорее да', 3),
            ('Не знаю', 0),
            ('Скорее нет', -3),
            ('Нет, не нравится', -5)
        ]
    }
]

# Вопросы для второго этапа
STAGE2_QUESTIONS = [
    {
        'text': '6. Как вы относитесь к рутинной работе?',
        'options': [
            ('Положительно, мне нравится стабильность', 5),
            ('Нейтрально', 0),
            ('Отрицательно, предпочитаю разнообразие', -5)
        ]
    },
    {
        'text': '7. Вы предпочитаете работать в команде или индивидуально?',
        'options': [
            ('В команде', 5),
            ('Зависит от ситуации', 0),
            ('Индивидуально', -5)
        ]
    },
    {
        'text': '8. Насколько важна для вас высокая зарплата?',
        'options': [
            ('Очень важна', 5),
            ('Важна, но не главное', 3),
            ('Не очень важна', -3)
        ]
    }
]

# Детальный тест по типам Холланда
DETAILED_QUESTIONS = {
    'realistic': [
        'Вам нравится работать с инструментами и механизмами?',
        'Вы предпочитаете физическую активность умственной?',
        'Вам интересна работа на открытом воздухе?'
    ],
    'investigative': [
        'Вам нравится решать сложные задачи?',
        'Вы любите проводить исследования?',
        'Вам интересна научная деятельность?'
    ],
    'artistic': [
        'Вам нравится создавать что-то новое и оригинальное?',
        'Вы цените красоту и эстетику?',
        'Вам интересна творческая работа?'
    ],
    'social': [
        'Вам нравится помогать другим людям?',
        'Вы легко находите общий язык с людьми?',
        'Вам интересна работа в сфере образования или здравоохранения?'
    ],
    'enterprising': [
        'Вам нравится руководить и организовывать?',
        'Вы готовы рисковать ради успеха?',
        'Вам интересна предпринимательская деятельность?'
    ],
    'conventional': [
        'Вам нравится работать с документами и данными?',
        'Вы цените порядок и систематичность?',
        'Вам комфортно следовать установленным правилам?'
    ]
}

# Профессии по типам Холланда
PROFESSIONS = {
    'realistic': [
        'Инженер',
        'Механик',
        'Электрик',
        'Строитель',
        'Водитель',
        'Фермер'
    ],
    'investigative': [
        'Учёный',
        'Программист',
        'Аналитик',
        'Исследователь',
        'Врач',
        'Химик'
    ],
    'artistic': [
        'Дизайнер',
        'Художник',
        'Музыкант',
        'Писатель',
        'Актёр',
        'Фотограф'
    ],
    'social': [
        'Учитель',
        'Психолог',
        'Социальный работник',
        'Медсестра',
        'Консультант',
        'Тренер'
    ],
    'enterprising': [
        'Менеджер',
        'Предприниматель',
        'Продавец',
        'Маркетолог',
        'Юрист',
        'Политик'
    ],
    'conventional': [
        'Бухгалтер',
        'Секретарь',
        'Библиотекарь',
        'Администратор',
        'Экономист',
        'Банковский служащий'
    ]
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало разговора"""
    keyboard = [
        [InlineKeyboardButton("🎯 Начать тест", callback_data='start_test')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Добро пожаловать! 👋\n\n"
        "Я помогу вам пройти тест на профориентацию по методике Холланда (ХРБ).\n\n"
        "Тест состоит из нескольких этапов:\n"
        "1️⃣ Базовые вопросы (5 вопросов)\n"
        "2️⃣ Дополнительные вопросы (3 вопроса)\n"
        "3️⃣ Детальный анализ\n\n"
        "Готовы начать?",
        reply_markup=reply_markup
    )
    return HRB


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало первого этапа"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['stage1_answers'] = []
    context.user_data['current_question'] = 0
    
    await send_stage1_question(query, context)
    return STAGE1


async def send_stage1_question(query, context: ContextTypes.DEFAULT_TYPE):
    """Отправка вопроса первого этапа"""
    question_num = context.user_data['current_question']
    
    if question_num >= len(STAGE1_QUESTIONS):
        await finish_stage1(query, context)
        return STAGE2
    
    question = STAGE1_QUESTIONS[question_num]
    keyboard = []
    
    for i, (option_text, score) in enumerate(question['options']):
        keyboard.append([InlineKeyboardButton(
            option_text,
            callback_data=f'stage1_{i}'
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 Этап 1/3\n\n{question['text']}",
        reply_markup=reply_markup
    )


async def stage1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа первого этапа"""
    query = update.callback_query
    await query.answer()
    
    answer_index = int(query.data.split('_')[1])
    question_num = context.user_data['current_question']
    question = STAGE1_QUESTIONS[question_num]
    score = question['options'][answer_index][1]
    
    context.user_data['stage1_answers'].append(score)
    context.user_data['current_question'] += 1
    
    await send_stage1_question(query, context)
    return STAGE1


async def finish_stage1(query, context: ContextTypes.DEFAULT_TYPE):
    """Завершение первого этапа"""
    context.user_data['stage2_answers'] = []
    context.user_data['current_question'] = 0
    
    await send_stage2_question(query, context)


async def send_stage2_question(query, context: ContextTypes.DEFAULT_TYPE):
    """Отправка вопроса второго этапа"""
    question_num = context.user_data['current_question']
    
    if question_num >= len(STAGE2_QUESTIONS):
        await finish_stage2(query, context)
        return DETAILED_TEST
    
    question = STAGE2_QUESTIONS[question_num]
    keyboard = []
    
    for i, (option_text, score) in enumerate(question['options']):
        keyboard.append([InlineKeyboardButton(
            option_text,
            callback_data=f'stage2_{i}'
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📝 Этап 2/3\n\n{question['text']}",
        reply_markup=reply_markup
    )


async def stage2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа второго этапа"""
    query = update.callback_query
    await query.answer()
    
    answer_index = int(query.data.split('_')[1])
    question_num = context.user_data['current_question']
    question = STAGE2_QUESTIONS[question_num]
    score = question['options'][answer_index][1]
    
    context.user_data['stage2_answers'].append(score)
    context.user_data['current_question'] += 1
    
    await send_stage2_question(query, context)
    return STAGE2


async def finish_stage2(query, context: ContextTypes.DEFAULT_TYPE):
    """Завершение второго этапа и начало детального теста"""
    context.user_data['detailed_answers'] = {}
    context.user_data['current_type'] = 'realistic'
    context.user_data['current_detailed_question'] = 0
    
    await send_detailed_question(query, context)


async def send_detailed_question(query, context: ContextTypes.DEFAULT_TYPE):
    """Отправка детального вопроса"""
    current_type = context.user_data['current_type']
    question_num = context.user_data['current_detailed_question']
    
    types_list = list(DETAILED_QUESTIONS.keys())
    
    if current_type not in types_list:
        await show_results(query, context)
        return ConversationHandler.END
    
    questions = DETAILED_QUESTIONS[current_type]
    
    if question_num >= len(questions):
        # Переход к следующему типу
        current_index = types_list.index(current_type)
        if current_index + 1 < len(types_list):
            context.user_data['current_type'] = types_list[current_index + 1]
            context.user_data['current_detailed_question'] = 0
            await send_detailed_question(query, context)
        else:
            await show_results(query, context)
            return ConversationHandler.END
        return DETAILED_TEST
    
    question_text = questions[question_num]
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='detailed_yes')],
        [InlineKeyboardButton("Скорее да", callback_data='detailed_rather_yes')],
        [InlineKeyboardButton("Не знаю", callback_data='detailed_neutral')],
        [InlineKeyboardButton("Скорее нет", callback_data='detailed_rather_no')],
        [InlineKeyboardButton("Нет", callback_data='detailed_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    type_names = {
        'realistic': 'Реалистический',
        'investigative': 'Исследовательский',
        'artistic': 'Артистический',
        'social': 'Социальный',
        'enterprising': 'Предпринимательский',
        'conventional': 'Конвенциональный'
    }
    
    await query.edit_message_text(
        f"📝 Этап 3/3 - {type_names[current_type]} тип\n\n{question_text}",
        reply_markup=reply_markup
    )


async def detailed_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка детального ответа"""
    query = update.callback_query
    await query.answer()
    
    answer = query.data.split('_')[1]
    score_map = {
        'yes': 5,
        'rather': 3,
        'neutral': 0,
        'no': -5
    }
    
    if 'rather' in answer:
        if 'yes' in answer:
            score = 3
        else:
            score = -3
    else:
        score = score_map.get(answer, 0)
    
    current_type = context.user_data['current_type']
    
    if current_type not in context.user_data['detailed_answers']:
        context.user_data['detailed_answers'][current_type] = []
    
    context.user_data['detailed_answers'][current_type].append(score)
    context.user_data['current_detailed_question'] += 1
    
    await send_detailed_question(query, context)
    return DETAILED_TEST


async def show_results(query, context: ContextTypes.DEFAULT_TYPE):
    """Показ результатов"""
    # Подсчёт баллов по типам
    type_scores = {}
    
    for type_name, answers in context.user_data['detailed_answers'].items():
        type_scores[type_name] = sum(answers)
    
    # Сортировка типов по баллам
    sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Формирование результата
    type_names = {
        'realistic': 'Реалистический (R)',
        'investigative': 'Исследовательский (I)',
        'artistic': 'Артистический (A)',
        'social': 'Социальный (S)',
        'enterprising': 'Предпринимательский (E)',
        'conventional': 'Конвенциональный (C)'
    }
    
    result_text = "🎯 Результаты теста:\n\n"
    
    for i, (type_code, score) in enumerate(sorted_types[:3], 1):
        result_text += f"{i}. {type_names[type_code]}: {score} баллов\n"
    
    result_text += "\n📋 Рекомендуемые профессии:\n\n"
    
    top_type = sorted_types[0][0]
    professions = PROFESSIONS[top_type]
    
    for profession in professions:
        result_text += f"• {profession}\n"
    
    result_text += "\n💡 Хотите пройти тест заново? Нажмите /start"
    
    keyboard = [[InlineKeyboardButton("🔄 Пройти заново", callback_data='start_test')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена теста"""
    await update.message.reply_text(
        "Тест отменён. Чтобы начать заново, нажмите /start"
    )
    return ConversationHandler.END


def main():
    """Запуск бота"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
    
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            HRB: [CallbackQueryHandler(start_test, pattern='^start_test$')],
            STAGE1: [CallbackQueryHandler(stage1_answer, pattern='^stage1_')],
            STAGE2: [CallbackQueryHandler(stage2_answer, pattern='^stage2_')],
            DETAILED_TEST: [CallbackQueryHandler(detailed_answer, pattern='^detailed_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Определяем режим работы
    port = int(os.getenv('PORT', 10000))
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if webhook_url:
        # Режим webhook для Render
        logger.info(f"🌐 Запуск в режиме webhook: {webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}",
            drop_pending_updates=True
        )
    else:
        # Режим polling для локального запуска
        logger.info("🤖 Запуск в режиме polling")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )


if __name__ == '__main__':
    main()
