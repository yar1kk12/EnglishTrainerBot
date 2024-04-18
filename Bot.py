from random import choice, randint
import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import time, schedule
from DataBase import *
import os
import Get_data

if not 'Bot_DB.db' in os.listdir():
    print('Creating DataBase....')
    with open('DataBase.py') as code:
        eval(code.read())
    print('DataBase were succesfully created')

if not Words.select().execute():
    print('Feeling DataBase....')
    Get_data.fill_words()
    Get_data.fill_synonyms()
    Get_data.fill_irregullar()
    print('Data were succesfully filled')



# bot = Bot('*') / Your bot token
dp = Dispatcher(bot = bot)

'''Global variables'''
isStarted = False

# Home menu status
Words_started = False
IrrW_started = False


Add_words_mode = False

# TG pooling variables
correctAnswer_id = None
correctWord_id = None

# ReplyKB
Home_kb = ReplyKeyboardMarkup()
Home_kb.add('Words', 'Irregular verbs')
Home_kb.add('Settings', 'My progress')

back_keyb = ReplyKeyboardMarkup()
back_keyb.add('Back to home page')

Words_kb = ReplyKeyboardMarkup()
Words_kb.add('Learn words', 'Start Test')
Words_kb.add('Edit my words', 'Add words')
Words_kb.add('Back to home page')



# InlineKB
def Words_count_kb(): #клавіатура що викликається у меню Words
    keyb = types.InlineKeyboardMarkup()
    button_2 = types.InlineKeyboardButton('2', callback_data='Words_2')
    button_4 = types.InlineKeyboardButton('4', callback_data='Words_4')
    button_6 = types.InlineKeyboardButton('6', callback_data='Words_6')
    keyb.add(button_2,button_4)
    keyb.add(button_6)
    return keyb


# functions
def get_word(status: str = 'not used'):
    '''This functions send query to Words Db and get random word which have never used.
    :return
            it depends on is any User Words DB has
    '''
    list_userW = UserWords.select(UserWords.Word, UserWords.ID, UserWords.Word_Translation).where(UserWords.Status == status).execute()
    if not list_userW:
        list_allW = Words.select(Words.Word, Words.ID, Words.Word_Translation, Words.Synonyms).where(Words.Status == status).execute()
        if list_allW:
            word = choice(list_allW)
            translation = word.Word_Translation
            syn = word.Synonyms
            Words.update(Status = 'learning').where(Words.ID == word.ID).execute() #оновлюємо статус слова в бд
            return word, translation, syn
        else:
            return 'На цьому поки все. Ти вивчив всі мої слова.'
    else:
        syn = None
        word = choice(list_userW)
        translation = word.Word_Translation
        UserWords.update(Status='learning').where(UserWords.ID == word.ID).execute()
        return word, translation, syn


def get_progress():
    """This fun return count of words which were learned and count of all words"""
    studied_words = Words.select().where(Words.Status == 'studied').execute()
    all_words = Words.select().execute()

    return f'''Ваш прогресс:

Ви вивчили {len(studied_words)} з {len(all_words)} слів'''


@dp.message_handler(commands=['start', 'add_word'])
async def cmd_start(message: types.Message):
    global isStarted
    if message.text == '/start':
        if not isStarted:
            isStarted = True
            await message.answer(f'Вітаю тебе у навчальному боті EnglishFriend. З його допомогою ти матимєш можливість'
                                 f' прокачати свої знання з англійської лексики.', reply_markup=Home_kb)
    elif message.text[:9] == '/add_word':
        sp_word = message.text.strip().replace('/add_word', '').split(',')
        word = sp_word[0]
        trans = sp_word[1]
        ob = UserWords(Word=word, Word_Translation=trans, UserID=message.from_user.id)
        ob.save()
        await message.answer(f'Слово успішно додано')


@dp.message_handler(text = ['Words','Irregular verbs', 'My progress'])
async def Menu(message: types.Message):
    global Words_started, isStarted, IrrW_started
    if isStarted:
        if message.text == 'Words':
            await message.answer('Оберіть дію нижче:', reply_markup=Words_kb)
            Words_started = True
        elif message.text == 'Irregular verbs':
            await message.answer('Введіть слово у форматі( to *слово* ), а я надішлю вам його форми',
                                 reply_markup=back_keyb)
            IrrW_started = True
        elif message.text == 'My progress':
            await message.answer(get_progress(), reply_markup=Home_kb)
    else:
        await message.answer('Спочатку треба розпочати /start')


@dp.poll_answer_handler()
async def handle_poll_answer(quiz: types.PollAnswer):
    global correctAnswer_id, correctWord_id
    user_id = quiz.user.id
    chosen_option_id = quiz.option_ids[0]
    correct_option_id = correctAnswer_id
    Translation = Words.get(Words.ID == correctWord_id).Word_Translation

    if chosen_option_id == correct_option_id:
        print(correctWord_id)
        Words.update(Status='studied').where(Words.ID ==  correctWord_id).execute()
        response_text = "Правильно✅"
    else:
        response_text = f"Не правильно❌\n\nПравильна відповідь: {Translation}"

    await bot.send_message(user_id, response_text)


@dp.message_handler(content_types=['text'])
async def Words_panel(message: types.Message):
    global Words_started, isStarted, Add_words_mode, IrrW_started, correctAnswer_id, correctWord_id
    if isStarted:
        if message.text == 'Back to home page':
            await message.answer('Оберіть дію нижче:', reply_markup=Home_kb)
            Words_started = False
            IrrW_started = False
        elif Words_started:
            if message.text == 'Learn words':
                await message.answer('Оберіть кількість слів яку бажаєте вивчити:', reply_markup=Words_count_kb())
            elif message.text == 'Add words':
                await message.answer('Введіть слово яке бажаєте додати у форматі: \n\n/add_word *your word*, *translation*')
            elif message.text == 'Edit my words':
                list_userW = UserWords.select(UserWords.Word, UserWords.ID, UserWords.Word_Translation).execute()
                for el in list_userW:
                    keyb_d = types.InlineKeyboardMarkup()
                    del_button = types.InlineKeyboardButton('Видалити🗑', callback_data=f'{el.ID}_delete')
                    keyb_d.add(del_button)
                    await message.answer(f'{el.Word} - {el.Word_Translation}', reply_markup=keyb_d)
            elif message.text == 'Start Test':
                l_words = Words.select(Words.Word, Words.Word_Translation, Words.ID).where(Words.Status == 'learning') #слова які можна використовувати для питання
                q_word = choice(l_words) #обране слово
                Incorrect_words = Words.select(Words.Word, Words.Word_Translation, Words.ID).where(Words.Word != q_word) #слова які можна використовувати як варіанти відповіді
                question = f"{q_word.Word}"
                correct_option_id = randint(0, 2)#індекс правильної відповіді
                options = [] #варіанти відповідей
                for i in range(3):
                    if i == correct_option_id:
                        options.append(q_word.Word_Translation)
                    else:
                        options.append(choice(Incorrect_words).Word_Translation)

                poll = await bot.send_poll(
                    message.chat.id,
                    question,
                    correct_option_id=correct_option_id,
                    options=options,
                    is_anonymous=True,
                    allows_multiple_answers=False
                )
                correctAnswer_id = correct_option_id
                correctWord_id = q_word.ID
        elif IrrW_started:
            word = IrregularVerbs.select().where(message.text == IrregularVerbs.form_1)
            if word:
                word = choice(word)
                await message.answer(f'<b>{word.form_1} - {word.Translation}</b>\n\n'
                                        f'1. {word.form_1}\n'
                                        f'2. {word.form_2}\n'
                                        f'3. {word.form_3}', parse_mode='html', reply_markup=back_keyb)
            else:
                await message.answer('Я не знаю такого слова')
    else:
        await message.answer('Спочатку треба розпочати /start')


@dp.callback_query_handler(lambda a: True)
async def get_query(callback: types.CallbackQuery):
    if Words_started:
        if callback.data[:5] == 'Words': #обробка запитів на калькість слів
            for i in range(int(callback.data[-1:])):
                el = get_word()
                if el[2] != None:
                    await callback.message.answer(f'<b>{el[0]} - {el[1]}</b>\n\nМожливі синоніми:\n'
                                                f'{el[2].replace("/",", ")}', parse_mode='html')
                else: await callback.message.answer(f'{el[0]} - {el[1]}')
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        elif callback.data[-7:] == '_delete':#обробка запитів на видалення слова
            UserWords.delete().where(UserWords.ID == callback.data[:-7]).execute()
            await callback.message.answer('Дані успішно видалено')
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

    else: await callback.message.answer('Error')




if __name__ == '__main__':
    executor.start_polling(dp)