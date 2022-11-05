from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()
b1=KeyboardButton('/help')
b2=KeyboardButton('/wtf')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.row(b1,b2)
@dp.message_handler(commands = ['start'])
async def send(message: types.Message):
    await message.answer('<b>Start</b>',reply_markup=kb_client)

#@dp.message_handler()
#async def send(message: types.Message):
 #   if message.text == '/help':
 #       await message.answer('<b>HELP</b>')
   # elif message.text =='/wtf':
  #      await message.answer('<b>WTF</b>')

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

sql_start()
executor.start_polling(dp,skip_updates=True)