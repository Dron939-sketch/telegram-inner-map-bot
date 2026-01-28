import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

NAME, STAGE1, STAGE2, DETAILED_TEST = range(4)

ARCHETYPES = {
    '1A': {'name': '🛡️ ФИЛОСОФ-ОТШЕЛЬНИК', 'description': 'Вы ищете ответы внутри себя и стремитесь к внутренней гармонии.'},
    '1B': {'name': '⚔️ ВОИН-АТЛЕТ', 'description': 'Вы фокусируетесь на себе и стремитесь к росту и достижениям.'},
    '1C': {'name': '💰 ДИПЛОМАТ-ЦЕЛИТЕЛЬ', 'description': 'Вы ищете своё место в системе и стремитесь к гармонии с миром.'},
    '1D': {'name': '🔥 ЛИДЕР-РЕВОЛЮЦИОНЕР', 'description': 'Вы видите несовершенство системы и стремитесь её изменить.'}
}

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

FAIRY_TALES = {
    '1A_МИССИЯ': 'https://drive.google.com/file/d/1WWmcf5t8aaUA_oIl0DR_xN_UKFwbIjp2/view?usp=sharing',
    '1A_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1n39knulPxkqgmlnvuhajAJ_fZLYkq8iE/view?usp=sharing',
    '1A_ЦЕННОСТИ': 'https://drive.google.com/file/d/1rv36hmFDKOFB30ba-jETlsREwAIeS1ea/view?usp=sharing',
    '1A_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1jy2bN6zplfDrUAyGwbB3NwGCmh7qRE3Y/view?usp=sharing',
    '1A_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1qa4-krpY27m_q4ljtN4yH_TjH8mkp78-/view?usp=sharing',
    '1A_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1dUcN3FCEtnXjKkzzUtslGbMrxDkcltgQ/view?usp=sharing',
    '1B_МИССИЯ': 'https://drive.google.com/file/d/1QYVwcl_sWf-Ntpbp5En7lph1Sb-4v6R-/view?usp=sharing',
    '1B_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1xcm7d8yPNB0e_fFucvVubpsKS6ZP7d-N/view?usp=sharing',
    '1B_ЦЕННОСТИ': 'https://drive.google.com/file/d/1OX2M-WODASA9RiwTosP97KrnWY-kdAOj/view?usp=sharing',
    '1B_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1nH8mls_DaiyZlNZU8m4tuS8zKjBYS14o/view?usp=sharing',
    '1B_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1_0tvaXMgH9aJ2xGM96WFT-14RPYpAlRs/view?usp=sharing',
    '1B_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1iQKqlR2P_D4Dxqt4kbnRpER9gkgEdKRN/view?usp=sharing',
    '1C_МИССИЯ': 'https://drive.google.com/file/d/1l1zH2nY4Ogd7QTU-uANU0v5FL6fReiCS/view?usp=sharing',
    '1C_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1CP9GBpKwVJey8bteztJ0z1nrk8pLChzu/view?usp=sharing',
    '1C_ЦЕННОСТИ': 'https://drive.google.com/file/d/1ZSMGbKftI6mCIJGhBWEc-q0k8QBqpDAu/view?usp=sharing',
    '1C_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1UH7uvFvEtJG8h0J_ti0XUrEjprvqQ7bD/view?usp=sharing',
    '1C_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1JwVoO3MMl8rRaRttqJWqKHepJUdvbGWC/view?usp=sharing',
    '1C_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/13HRqpPfdToOGZHWodrnNt6xvfuhExRPL/view?usp=sharing',
    '1D_МИССИЯ': 'https://drive.google.com/file/d/1jpJUSNO5Or2qdx2OxRMgBz2JkmVshlIz/view?usp=sharing',
    '1D_ИДЕНТИЧНОСТЬ': 'https://drive.google.com/file/d/1DcaKOKK429QqUVJnlRb6K5fWkkICpJYr/view?usp=sharing',
    '1D_ЦЕННОСТИ': 'https://drive.google.com/file/d/1oZ5gT9Lh7OWGn8XR9LIrMxPV0z_ZuNnz/view?usp=sharing',
    '1D_СПОСОБНОСТИ': 'https://drive.google.com/file/d/1uphOmKRdH3ga5sbTN18XlLJg6Gevx77b/view?usp=sharing',
    '1D_ПОВЕДЕНИЕ': 'https://drive.google.com/file/d/1ccdEJaLoVxalnPMZPbd8UpqN3DeASGzo/view?usp=sharing',
    '1D_ОКРУЖЕНИЕ': 'https://drive.google.com/file/d/1SI8msDuxFRQRuDZouNxoi_jlCvi_FFu7/view?usp=sharing',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 Начать тест", callback_data='start_test')],
        [InlineKeyboardButton("ℹ️ Узнать больше", callback_data='info')]
    ]
    await update.message.reply_text(
        "👋 *Привет!*\n\nЯ помогу найти твой внутренний архетип.\n\n🎯 *Тест:*\n1️⃣ Базовое сканирование (16 вопросов)\n2️⃣ Углублённое сканирование (30 вопросов)\n\n⏱ ~10 минут.\n\nГотов?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_test':
        await query.edit_message_text("📝 *Как тебя зовут?*", parse_mode='Markdown')
        return NAME
    elif query.data == 'info':
        await query.edit_message_text("ℹ️ *О тесте*\n\nОснован на модели Дилтса.\n\nПоможет:\n• Определить архетип\n• Найти \"узел\"\n• Получить сказку", parse_mode='Markdown')
        keyboard = [[InlineKeyboardButton("🎯 Начать", callback_data='start_test')]]
        await query.message.reply_text("Готов?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    context.user_data['stage1_answers'] = []
    context.user_data['stage1_question'] = 0
    
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}! 😊\n\n🎯 *ЭТАП 1: ФОКУС*\n\n8 вопросов.",
        parse_mode='Markdown'
    )
    
    q_num = context.user_data['stage1_question']
    keyboard = [[InlineKeyboardButton("A", callback_data='stage1_A')], [InlineKeyboardButton("B", callback_data='stage1_B')]]
    await update.message.reply_text(
        f"*Вопрос {q_num + 1}/8:*\n\n{STAGE1_QUESTIONS[q_num]}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return STAGE1

async def stage1_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['stage1_answers'].append(query.data.split('_')[1])
    context.user_data['stage1_question'] += 1
    
    await query.message.delete()
    
    q_num = context.user_data['stage1_question']
    
    if q_num >= len(STAGE1_QUESTIONS):
        context.user_data['stage2_answers'] = []
        context.user_data['stage2_question'] = 0
        
        await query.message.reply_text(
            "✅ *Этап 1 завершён!*\n\n🎯 *ЭТАП 2: СТРАТЕГИЯ*\n\n8 вопросов.",
            parse_mode='Markdown'
        )
        
        keyboard = [[InlineKeyboardButton("A", callback_data='stage2_A')], [InlineKeyboardButton("B", callback_data='stage2_B')]]
        await query.message.reply_text(
            f"*Вопрос 1/8:*\n\n{STAGE2_QUESTIONS[0]}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return STAGE2
    
    keyboard = [[InlineKeyboardButton("A", callback_data='stage1_A')], [InlineKeyboardButton("B", callback_data='stage1_B')]]
    await query.message.reply_text(
        f"*Вопрос {q_num + 1}/8:*\n\n{STAGE1_QUESTIONS[q_num]}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return STAGE1

async def stage2_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['stage2_answers'].append(query.data.split('_')[1])
    context.user_data['stage2_question'] += 1
    
    await query.message.delete()
    
    q_num = context.user_data['stage2_question']
    
    if q_num >= len(STAGE2_QUESTIONS):
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
            f"✅ *РЕЗУЛЬТАТ*\n\n"
            f"🎯 {ARCHETYPES[archetype]['name']}\n\n"
            f"{ARCHETYPES[archetype]['description']}\n\n"
            f"📊 *Баллы:*\n"
            f"• Фокус на себе: {score_A}/8\n"
            f"• Фокус на системе: {score_B}/8\n"
            f"• Защита: {score_C}/8\n"
            f"• Экспансия: {score_D}/8\n\n"
            f"🔍 Узнать \"узел\"?"
        )
        
        keyboard = [[InlineKeyboardButton("🔬 Углублённое сканирование", callback_data='detailed_test')]]
        await query.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return STAGE2
    
    keyboard = [[InlineKeyboardButton("A", callback_data='stage2_A')], [InlineKeyboardButton("B", callback_data='stage2_B')]]
    await query.message.reply_text(
        f"*Вопрос {q_num + 1}/8:*\n\n{STAGE2_QUESTIONS[q_num]}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return STAGE2

async def start_detailed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['detailed_answers'] = {level: [] for level in DETAILED_QUESTIONS.keys()}
    context.user_data['current_level'] = 0
    context.user_data['current_question'] = 0
    
    await query.edit_message_text(
        "🔬 *УГЛУБЛЁННОЕ СКАНИРОВАНИЕ*\n\n30 вопросов по 6 уровням.\nОцени от 1 до 5.",
        parse_mode='Markdown'
    )
    
    levels = list(DETAILED_QUESTIONS.keys())
    level = levels[0]
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
    await update.message.reply_text("Отменено. /start для начала.")
    return ConversationHandler.END

def main():
    TOKEN = os.environ.get('BOT_TOKEN')
    if not TOKEN:
        logger.error("❌ BOT_TOKEN не найден!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(button_handler, pattern='^(start_test|info)$')
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            STAGE1: [CallbackQueryHandler(stage1_answer, pattern='^stage1_')],
            STAGE2: [
                CallbackQueryHandler(stage2_answer, pattern='^stage2_'),
                CallbackQueryHandler(start_detailed_test, pattern='^detailed_test$')
            ],
            DETAILED_TEST: [CallbackQueryHandler(detailed_answer, pattern='^detailed_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    
    logger.info("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
