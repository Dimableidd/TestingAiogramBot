from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3 as sq

storage=MemoryStorage()
bot=Bot(token='5447587625:AAGDRTk_TtwihLhepN5qpzz-EjnhxzQXkUk', parse_mode=types.ParseMode.HTML)
dp=Dispatcher(bot, storage=storage)

def sql_start():
    global base,cur
    base=sq.connect('database.pb')
    cur=base.cursor()
    if base:
        print ('Data base connected')
    base.execute('CREATE TABLE IF NOT EXISTS menu(img TEXT, name TEXT PRIMARY KEY, description TEXT)')
    base.commit()

async def sql_read2():
    return cur.execute('SELECT * FROM menu').fetchall()

async def sql_delete_command(data):
    cur.execute('DELETE FROM menu WHERE name == ?',(data,))
    base.commit()

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()
b1=KeyboardButton('/help')
b2=KeyboardButton('/wtf')
b3=KeyboardButton('/Links')
b4=KeyboardButton('/You')
b5=KeyboardButton('/Delete')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.row(b1,b2,b3,b4).add(b5)
@dp.message_handler(commands = ['start'])
async def send(message: types.Message):
    await message.answer('<b>Start</b>',reply_markup=kb_client)

class FSMAdmin (StatesGroup):
    photo = State()
    name = State()
    description = State()

@dp.message_handler(commands=['wtf'],state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.photo.set()
    await message.reply('Load photo')

@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['photo']=message.photo[0].file_id
    await FSMAdmin.next()
    await message.reply("Name please")

@dp.message_handler(state=FSMAdmin.name)
async def load_photo(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['name']=message.text
    await FSMAdmin.next()
    await message.reply("Description please")

@dp.message_handler(state=FSMAdmin.description)
async def load_photo(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['description']=message.text
    await sql_add_command(state)
    await state.finish()

@dp.message_handler(commands='help')
async def menus(message: types.Message):
    for ret in cur.execute('SELECT * FROM menu').fetchall():
        await bot.send_photo(message.from_user.id, ret[0],f'<b>{ret[1]}</b>\n<b>Description</b>: {ret[2]}')

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} delate.',show_alert=True)

@dp.message_handler(commands='Delete')
async def delete_item(message: types.Message):
    read = await sql_read2()
    for ret in read:
        await bot.send_photo(message.from_user.id, ret[0],f'<b>{ret[1]}</b>\n<b>Description</b>: {ret[2]}')
        await bot.send_message(message.from_user.id,text='^^^', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Delete {ret[1]}', callback_data=f'del {ret[1]}')))

Inkey = InlineKeyboardMarkup(row_width=1)
urlButton1 = InlineKeyboardButton(text='Link Vk',url='https://vk.com/dimableidd')
urlButton2 = InlineKeyboardButton(text='Link YouTube',url='https://www.youtube.com')
Inkey.add(urlButton1, urlButton2) 

@dp.message_handler(commands='Links')
async def url_command(message: types.Message):
    await message.answer('Links:',reply_markup=Inkey)

Inkeys = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Problem?',callback_data='problem'))

@dp.message_handler(commands='You')
async def help_command(message:types.Message):
    await message.answer('Inline button', reply_markup=Inkeys)

@dp.callback_query_handler(text='problem')
async def problem_to_mee(callback: types.CallbackQuery):
    await callback.message.answer('Call my phone')
    await callback.answer('Call my phone', show_alert=True)
sql_start()
executor.start_polling(dp,skip_updates=True)