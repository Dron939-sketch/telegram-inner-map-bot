import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

# Состояния
HRB, STAGE1, STAGE2, DETAILED_TEST = range(4)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния
HRB, STAGE1, STAGE2, ЭТАП3, ПОДРОБНОЕ_ТЕСТИРОВАНИЕ = диапазон(4)

# Архетипы
ARCHETYPES = {
    '1A': {'name': '🛡️ ФИЛОСОФ-ОТШЕЛЬНИК', 'description': 'Вы ищете ответы внутри себя и стремитесь к внутренней гармонии.'},
    '1B': {'name': '🌟 ВОИН-АТЛЕТ', 'description': 'Вы сосредоточены на себе и стремитесь к росту и достижениям.'},
    '1C': {'name': '🔮 ДИПЛОМАТ-ЦЕЛИТЕЛЬ', 'description': 'Вы ищете своё место в системе и стремитесь к гармонии с миром.'},
    '1D': {'name': '🚀 ЛИДЕР-РЕВОЛЮЦИОНЕР', 'description': 'Вы видите несовершенство системы и стремитесь её изменить.'}
}

# Вопросы этап 1
STAGE1_QUESTIONS = [
    "Когда у вас возникает проблема, вы в первую очередь:\nА) анализируете свои чувства и мысли\nВ) думаете о том, как это влияет на окружающих",
    "В конфликтной ситуации вы склонны:\nА) уйти в себя и обдумать происходящее\nВ) активно искать решение, вовлекая других",
    "Ваши решения чаще всего основаны на:\nА) личных убеждениях и внутренних ценностях\nВ) внешних обязанностях и общественных нормах",
    "Когда вы думаете о будущем, вы представляете:\nА) свой личностный рост и развитие\nВ) своё место в обществе и влияние на мир",
    "В трудные моменты вы обращаетесь к:\nА) себе (размышления, медитация)\nВ) другим (совет, поддержка)",
    "Ваша главная мотивация:\nА) понять себя и обрести внутреннюю гармонию\nВ) изменить мир вокруг себя"
]

# Вопросы этап 2
STAGE2_QUESTIONS = {
    'A': [
        "Когда вы думаете о будущем, вы представляете:\nА) свой личностный рост и развитие как личности\nВ) свои достижения и влияние на мир",
        "Когда вы думаете о будущем, вы представляете:\nА) свой личностный рост и развитие как личности\nВ) свои достижения и влияние на мир",
        "Ваши цели связаны с:\nА) самосовершенствованием и внутренним миром\nВ) внешними достижениями и объективными результатами"
    ],
    'B': [
        "С сложной ситуации вы склонны:\nА) искать безопасность и стабильность\nВ) идти на риск ради новых возможностей",
        "Вы чувствуете себя лучше, когда:\nА) остаётесь наедине с собой\nВ) общаетесь с людьми",
        "В трудные моменты вы:\nА) обращаетесь за поддержкой к другим\nВ) справляетесь самостоятельно"
    ]
}

# Подробные вопросы (30 вопросов по 6 уровням)
DETAILED_QUESTIONS = {
    'МИССИЯ': [
        "Я чётко понимаю свою главную цель в жизни",
        "Моя жизнь имеет глубокий смысл и направление",
        "Я знаю, какой след хочу оставить в мире",
        "Мои ежедневные действия связаны с моей главной целью",
        "Я чувствую, что моя жизнь служит чему-то большему"
    ],
    'ИДЕНТИЧНОСТЬ': [
        "Я хорошо понимаю, кто я на самом деле",
        "Я принимаю себя таким, какой я есть",
        "Мои действия соответствуют моим внутренним убеждениям",
        "Я чувствую целостность и согласованность в себе",
        "Я знаю свои сильные и слабые стороны"
    ],
    'ЦЕННОСТИ': [
        "Я чётко знаю, что для меня действительно важно",
        "Мои решения основаны на моих ценностях",
        "Я не иду на компромисс с моими главными принципами",
        "Мои ценности помогают мне делать выбор",
        "Я живу в соответствии со своими убеждениями"
    ],
    'СПОСОБНОСТИ': [
        "Я знаю свои таланты и умения",
        "Я постоянно развиваю свои навыки",
        "Я уверен в своих способностях",
        "Я эффективно использую свои сильные стороны",
        "Я легко осваиваю новые навыки"
    ],
    'ПОВЕДЕНИЕ': [
        "Мои действия последовательны и предсказуемы",
        "Я делаю то, что говорю",
        "Мои привычки поддерживают мои цели",
        "Я контролирую своё поведение",
        "Я легко меняю неэффективные привычки"
    ],
    'ОКРУЖЕНИЕ': [
        "Моё окружение поддерживает мои цели",
        "Я окружён людьми, которые меня вдохновляют",
        "Моя среда способствует моему росту",
        "Я чувствую себя комфортно в своём окружении",
        "Люди вокруг меня разделяют мои ценности"
    ]
}

# Ссылки на сказки в Google Drive
FAIRY_TALES = {
    '1A_МИССИЯ': 'https://drive.google.com/file/d/1WWmcf5t8aaUA_oIl0DR_xN_UKFwbIjp2/view?usp=sharing',
    '1A_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1n39knulPxkqgmlnvuhajAJ_fZLYkq8iE/view?usp=sharing',
    '1A_ЦЕННОСТИ': 'https://drive.google.com/file/d/1lDSe6Uo3xNvU2dXbSGdWJcTKZHhRZyze/view?usp=sharing',
    '1A_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1e8NhQPuWUGhxZX2y_gqVOKNQpYqvhqIm/view?usp=sharing',
    '1A_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1qsHLxwUmCjC3Lxdh6oWMsNQYGFCmVlJi/view?usp=sharing',
    '1A_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1pNXqVjKzYfhWHXuXVJfVYPJrYRJqfaWt/view?usp=sharing',
    '1B_МИССИЯ': 'https://drive.google.com/file/d/1rQcWlZJGxJNyLqXqKzXqYzXqYzXqYzXq/view?usp=sharing',
    '1B_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1sRdXmAKHyKOzMrYrLzYrMzYrMzYrMzYr/view?usp=sharing',
    '1B_ЦЕННОСТИ': 'https://drive.google.com/file/d/1tSeYnBLIzLPANsZsMzZsNzZsNzZsNzZs/view?usp=sharing',
    '1B_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1uTfZoCMJAMQBOtAtNzAtOzAtOzAtOzAt/view?usp=sharing',
    '1B_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1vUgApDNKBNRCPuBuOzBuPzBuPzBuPzBu/view?usp=sharing',
    '1B_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1wVhBqEOLCOSDQvCvPzCvQzCvQzCvQzCv/view?usp=sharing',
    '1C_МИССИЯ': 'https://drive.google.com/file/d/1xWiCrFPMDPTERwDwQzDwRzDwRzDwRzDw/view?usp=sharing',
    '1C_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1yXjDsGQNEQUFSxExRzExSzExSzExSzEx/view?usp=sharing',
    '1C_ЦЕННОСТИ': 'https://drive.google.com/file/d/1zYkEtHRPFRVGTyFySzFyTzFyTzFyTzFy/view?usp=sharing',
    '1C_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1AZlFuISQGSWHUzGzTzGzUzGzUzGzUzGz/view?usp=sharing',
    '1C_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1BAmGvJTRHTXIVAHAUzHAVzHAVzHAVzHA/view?usp=sharing',
    '1C_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1CBnHwKUSIUYJWBIBVzIBWzIBWzIBWzIB/view?usp=sharing',
    '1D_МИССИЯ': 'https://drive.google.com/file/d/1DCoIxLVTJVZKXCJCWzJCXzJCXzJCXzJC/view?usp=sharing',
    '1D_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1EDpJyMWUKWALYDKDXzKDYzKDYzKDYzKD/view?usp=sharing',
    '1D_ЦЕННОСТИ': 'https://drive.google.com/file/d/1FEqKzNXVLXBMZELEYzLEZzLEZzLEZzLE/view?usp=sharing',
    '1D_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1GFrLAOYWMYCNAFMFZzMFAzMFAzMFAzMF/view?usp=sharing',
    '1D_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1HGsMBPZXNZDOBGNGAzNGBzNGBzNGBzNG/view?usp=sharing',
    '1D_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1IHtNCQAYOAEPCHOHBzOHCzOHCzOHCzOH/view?usp=sharing',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['stage1_answers'] = []
    context.user_data['stage2_answers'] = []
    context.user_data['current_question'] = 0
    
    keyboard = [[InlineKeyboardButton("🚀 Начать тест", callback_data='start_test')]]
    
    await update.message.reply_text(
        "👋 *Добро пожаловать в тест внутренней карты!*\n\n"
        "Этот тест поможет:\n"
        "✅ Определить ваш архетип\n"
        "✅ Найти слабое звено в вашей системе\n"
        "✅ Получить персональную сказку-терапию\n\n"
        "📊 Тест состоит из 36 вопросов\n"
        "⏱ Займёт около 5 минут\n\n"
        "Готовы начать?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return HRB

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    question = STAGE1_QUESTIONS[0]
    keyboard = [[
        InlineKeyboardButton("А", callback_data='stage1_A'),
        InlineKeyboardButton("В", callback_data='stage1_B')
    ]]
    
    await query.message.edit_text(
        f"*Вопрос 1/6:*\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return STAGE1

async def stage1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    answer = query.data.split('_')[1]
    context.user_data['stage1_answers'].append(answer)
    context.user_data['current_question'] += 1
    q_num = context.user_data['current_question']
    
    if q_num >= len(STAGE1_QUESTIONS):
        a_count = context.user_data['stage1_answers'].count('A')
        b_count = context.user_data['stage1_answers'].count('B')
        context.user_data['stage1_result'] = 'A' if a_count > b_count else 'B'
        context.user_data['current_question'] = 0
        
        question = STAGE2_QUESTIONS[context.user_data['stage1_result']][0]
        keyboard = [[
            InlineKeyboardButton("А", callback_data='stage2_A'),
            InlineKeyboardButton("В", callback_data='stage2_B')
        ]]
        
        await query.message.edit_text(
            f"*Вопрос 7/9:*\n\n{question}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return STAGE2
    
    question = STAGE1_QUESTIONS[q_num]
    keyboard = [[
        InlineKeyboardButton("А", callback_data='stage1_A'),
        InlineKeyboardButton("В", callback_data='stage1_B')
    ]]
    
    await query.message.edit_text(
        f"*Вопрос {q_num + 1}/6:*\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return STAGE1

async def stage2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    answer = query.data.split('_')[1]
    context.user_data['stage2_answers'].append(answer)
    context.user_data['current_question'] += 1
    q_num = context.user_data['current_question']
    
    if q_num >= len(STAGE2_QUESTIONS[context.user_data['stage1_result']]):
        a_count = context.user_data['stage2_answers'].count('A')
        b_count = context.user_data['stage2_answers'].count('B')
        stage2_result = 'A' if a_count > b_count else 'B'
        
        stage1 = context.user_data['stage1_result']
        archetype = f"1{stage1.upper()}" if stage2_result == 'A' else f"1{chr(ord(stage1.upper()) + 1)}"
        
        if archetype not in ARCHETYPES:
            archetype = '1A'
        
        context.user_data['archetype'] = archetype
        context.user_data['detailed_answers'] = {level: [] for level in DETAILED_QUESTIONS.keys()}
        context.user_data['current_level'] = 0
        context.user_data['current_question'] = 0
        
        await query.message.edit_text(
            f"✅ *Ваш архетип: {ARCHETYPES[archetype]['name']}*\n\n"
            f"{ARCHETYPES[archetype]['description']}\n\n"
            f"Теперь пройдём детальное тестирование по 6 уровням (30 вопросов).\n\n"
            f"Оценивайте каждое утверждение от 1 до 5:\n"
            f"1 - Совсем не согласен\n"
            f"5 - Полностью согласен",
            parse_mode='Markdown'
        )
        
        level = list(DETAILED_QUESTIONS.keys())[0]
        question = DETAILED_QUESTIONS[level][0]
        keyboard = [[
            InlineKeyboardButton("1", callback_data='detailed_1'),
            InlineKeyboardButton("2", callback_data='detailed_2'),
            InlineKeyboardButton("3", callback_data='detailed_3'),
            InlineKeyboardButton("4", callback_data='detailed_4'),
            InlineKeyboardButton("5", callback_data='detailed_5')
        ]]
        
        await query.message.reply_text(
            f"🎯 *{level}*\n\n*Вопрос 1/30:*\n\n{question}\n\n1 - Не согласен | 5 - Согласен",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return DETAILED_TEST
    
    question = STAGE2_QUESTIONS[context.user_data['stage1_result']][q_num]
    keyboard = [[
        InlineKeyboardButton("А", callback_data='stage2_A'),
        InlineKeyboardButton("В", callback_data='stage2_B')
    ]]
    
    await query.message.edit_text(
        f"*Вопрос {7 + q_num}/9:*\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return STAGE2

async def detailed_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    score = int(query.data.split('_')[1])
    
    levels = list(DETAILED_QUESTIONS.keys())
    level_num = context.user_data['current_level']
    q_num = context.user_data['current_question']
    
    level = levels[level_num]
    context.user_data['detailed_answers'][level].append(score)
    context.user_data['current_question'] += 1
    
    await query.message.delete()
    
    if context.user_data['current_question'] >= len(DETAILED_QUESTIONS[level]):
        context.user_data['current_level'] += 1
        context.user_data['current_question'] = 0
        level_num = context.user_data['current_level']
    
    if level_num >= len(levels):
        answers = context.user_data['detailed_answers']
        level_scores = {lvl: sum(scores) for lvl, scores in answers.items()}
        min_level = min(level_scores, key=level_scores.get)
        archetype = context.user_data['archetype']
        
        message = f"✅ *РЕЗУЛЬТАТ*\n\n🎯 {ARCHETYPES[archetype]['name']}\n\n📊 *Баллы:*\n\n"
        for lvl, score in level_scores.items():
            emoji = '🔴' if lvl == min_level else '🟢'
            message += f"{emoji} {lvl}: {score}/25\n"
        
        message += f"\n🎯 *Узел: {min_level}* ({level_scores[min_level]}/25)\n\n"
        
        file_key = f"{archetype}_{min_level}"
        file_url = FAIRY_TALES.get(file_key)
        
        if file_url:
            file_id = file_url.split('/d/')[1].split('/')[0]
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            message += f"📖 Отправляю твою персональную сказку..."
            await query.message.reply_text(message, parse_mode='Markdown')
            
            try:
                await query.message.reply_document(
                    document=direct_url,
                    caption=f"📖 *Твоя сказка*\n\n🎯 {ARCHETYPES[archetype]['name']}\n🔴 Узел: {min_level}",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка отправки PDF: {e}")
                keyboard = [[InlineKeyboardButton("📥 Открыть сказку", url=file_url)]]
                await query.message.reply_text(
                    "⚠️ Не удалось отправить файл автоматически.\nОткрой по кнопке ниже:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            message += f"📖 Сказка `{file_key}.pdf` скоро будет доступна"
            await query.message.reply_text(message, parse_mode='Markdown')
        
        return ConversationHandler.END
    
    level = levels[level_num]
    q_num = context.user_data['current_question']
    question = DETAILED_QUESTIONS[level][q_num]
    total = context.user_data['current_level'] * 5 + q_num + 1
    
    keyboard = [[
        InlineKeyboardButton("1", callback_data='detailed_1'),
        InlineKeyboardButton("2", callback_data='detailed_2'),
        InlineKeyboardButton("3", callback_data='detailed_3'),
        InlineKeyboardButton("4", callback_data='detailed_4'),
        InlineKeyboardButton("5", callback_data='detailed_5')
    ]]
    
    await query.message.reply_text(
        f"🎯 *{level}*\n\n*Вопрос {total}/30:*\n\n{question}\n\n1 - Не согласен | 5 - Согласен",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return DETAILED_TEST

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Тест отменён. Напиши /start чтобы начать заново.")
    return ConversationHandler.END

def main():
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
    
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
