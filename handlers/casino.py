from aiogram import types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from create_bot import dp,bot
from aiogram.dispatcher.filters import Text
import random
import time
import psycopg2

DB_URL = 'postgres://zivescggovndkf:3c1f9b3b3646a5df732fbf4358fdc2c7a6985418891be785fed9780d5d89d656@ec2-99-81-16-126.eu-west-1.compute.amazonaws.com:5432/d2ja87rob9ne3l'

db_connection = psycopg2.connect(DB_URL, sslmode='require')
db_object = db_connection.cursor()
	

table_casino = InlineKeyboardMarkup()
red_inlinebtn = InlineKeyboardButton('Red',callback_data='Red')
black_inlinebtn = InlineKeyboardButton('Black',callback_data='Black')
st1_inlinebtn = InlineKeyboardButton('1st',callback_data='1st')
nd2_inlinebtn = InlineKeyboardButton('2nd',callback_data='2nd')
rd3_inlinebtn = InlineKeyboardButton('3rd',callback_data='3rd')
on_number_inlinebtn = InlineKeyboardButton('Zero',callback_data='Zero')
next_inlinebtn = InlineKeyboardButton('Продолжить',callback_data='Next')
info_bet_inlinebtn = InlineKeyboardButton('Информация про ставки',callback_data='info_for_bet')
info_money_inline_btn = InlineKeyboardButton('Как получить деньги?',callback_data='how_get_money')
info_markup = InlineKeyboardMarkup()
info_markup.add(info_bet_inlinebtn).add(info_money_inline_btn)
table_casino.row(red_inlinebtn,black_inlinebtn).row(st1_inlinebtn,nd2_inlinebtn,rd3_inlinebtn).row(on_number_inlinebtn)


class FSMcasino(StatesGroup):
	Choise = State()
	bet = State()

async def start_command(message : types.Message):
	global data_connection,data_object
	await message.answer(f'Привет {message.from_user.first_name}!\nЯ казино бот, введи /casino чтобы начать играть\nВведи /bank чтобы проверить свой банковский счёт')
	ID = message.from_user.id
	print(ID)
	db_object.execute(f'SELECT user_id FROM casino_player WHERE user_id={ID}')
	check_id = db_object.fetchone()
	if not check_id:
		db_object.execute('INSERT INTO casino_player(user_id,money_casino) VALUES(%s,%s)', (ID,100))
		db_connection.commit()
		await message.answer('Если хочешь узнать информацию о боте введи /info')
	else:
		db_object.execute(f'SELECT money_casino FROM casino_player WHERE user_id = {ID}')
		money = db_object.fetchone()
		await message.answer(f'У тебя на счёту = ${money[0]}')
		await message.answer('Если хочешь узнать информацию о ставках, введи /info')

async def wallet_func(message : types.Message):
	global db_object
	ID = message.from_user.id
	db_object.execute(f'SELECT money_casino FROM casino_player WHERE user_id = {ID}')
	money = db_object.fetchone() 
	if not money:
		await message.answer('Сначало введите /start')
	else:
		await message.answer(f'У тебя в кошельке - ${money[0]}')

async def admin(message : types.Message):
	await message.answer('Увидели ошибку?\nНапиши сюда:https://t.me/julyqpe')

async def lose(arg1):
	number_lose = random.randint(1,5)
	if number_lose == 1:
		await arg1.answer('Ха лох')
		await bot.send_sticker(arg1.from_user.id,sticker='CAACAgIAAxkBAAEFnHZi_7o9ZOEiICCCmSM40_bAqrKUxwACXxMAApofyEm95m3JEvU0WSkE')
	elif number_lose == 2:
		await arg1.answer('Ты проиграл\nУра!')
		await bot.send_sticker(arg1.from_user.id,sticker='CAACAgIAAxkBAAEFtLdjC7p14YIUsdgelxqU_cymdcxwbAACyxQAAn0eIEg4cZHFhqYkwikE')
	elif number_lose == 3:
		await arg1.answer('Ты проиграл, но не растраивайся повезёт в следующий раз!')
	elif number_lose == 4:
		await arg1.answer('Твоя ставка проиграла...')
		await bot.send_sticker(arg1.from_user.id,sticker='CAACAgIAAxkBAAEFtLljC7r_--zgyIKD1ycyBO8ObliXoAACfRQAAiGk0EkLAprTyyvxxykE')								
	elif number_lose == 5:
		await arg1.answer('Ох..')
		time.sleep(1)
		await arg1.answer('Не повезло')

async def info(message : types.Message):
	await message.answer('Что хочешь узнать?',reply_markup=info_markup)

async def info_bet(callback : types.CallbackQuery):
	await callback.message.answer('Ставка на red - Выиграешь если число парное\nСтавка на black - Выиграешь если число не парное\nСтавка 1st - Выигрaешь если число в диапазоне от 1 до 12\nСтавка 2nd - Выиграешь если число в диапазоне от 12 до 24\nСтавка 3rd - Выиграешь если число в диапазоне от 24 до 36\nСтавка Zero - Выиграешь если выпало число 0')

async def info_money(callback : types.CallbackQuery):
	await callback.message.answer('Есть только два способа получить деньги:\n1. Взять кредит в банке\n2. Перевод денег с одной банковской карты на другую')

async def casino(message : types.Message,state = None):
	await message.answer('На что ставить будем?',reply_markup=table_casino)
	await message.answer('Если хотите отменить ставку, введите Отмена')
	await FSMcasino.Choise.set()

async def cancel_handler(message : types.Message,state : FSMContext):
	await message.answer('Как пожелаете!')
	await state.finish()

async def next_handler(callback : types.CallbackQuery,state = None):
	await message.answer('На что ставить будем?',reply_markup=table_casino)
	await FSMcasino.Choice.set()			

async def cb_choice_red(callback : types.CallbackQuery,state : FSMContext):
	async with state.proxy() as data:
		await callback.message.answer('Хорошо, теперь введи сколько хочешь поставить')
		data['Choise'] = 'Red'
		await FSMcasino.next()

async def cb_choice_black(callback : types.CallbackQuery,state : FSMContext):
	async with state.proxy() as data:
		await callback.message.answer('Хорошо, теперь введи сколько хочешь поставить')
		data['Choise'] = 'Black'
		await FSMcasino.next()

async def cb_choice_1st(callback : types.CallbackQuery,state : FSMContext):
	async with state.proxy() as data:
		await callback.message.answer('Хорошо, теперь введи сколько хочешь поставить')
		data['Choise'] = '1st'
		await FSMcasino.next()

async def cb_choice_2nd(callback : types.CallbackQuery,state : FSMContext):
	async with state.proxy() as data:
		await callback.message.answer('Хорошо, теперь введи сколько хочешь поставить')
		data['Choise'] = '2nd'
		await FSMcasino.next()

async def cb_choice_3rd(callback : types.CallbackQuery,state : FSMContext):
	async with state.proxy() as data:
		await callback.message.answer('Хорошо, теперь введи сколько хочешь поставить')
		data['Choise'] = '3rd'
		await FSMcasino.next()

async def cb_choice_number(callback : types.CallbackQuery,state : FSMContext):
	async with state.proxy() as data:
		data['Choise'] = 'Number'
		await callback.message.answer('Хорошо, теперь введи сколько хочешь поставить')
		await FSMcasino.next()

async def update_casino(arg1,arg2):
	global db_object,db_connection
	db_object.execute(f'UPDATE casino_player SET money_casino={arg1} WHERE user_id={arg2}')
	db_connection.commit()

async def bet_func(message : types.Message,state : FSMContext):
	global db_object
	ID = message.from_user.id
	db_object.execute(f'SELECT money_casino FROM casino_player WHERE user_id={ID}')
	money_tuple = db_object.fetchone()
	money = money_tuple[0]
	if not money:
		await message.reply('Сначало введи /start')
		await state.finish()
	else:			
		try:
			print(money)
			if int(message.text) <= money:
				bet = int(message.text)	
			else:
				await message.reply('У вас недостаточно средств, введите /wallet чтобы узнать скольку у вас на счёту\nЕсли не знаете как получить деньги введите /info')
				await state.finish()	
		except ValueError:
			await message.reply('Введите число без символов!')
			await state.finish()
	async with state.proxy() as data:
		global choise_number,update_casino,win,lose
		choise_casino = data['Choise']
		await message.reply('Начинаю крутить рулетку!')
		number_casino = random.randint(0,36)
		red = 0
		zero = 0
		black = 0
		if number_casino == 0:
			zero = 1
			red = 0
			black = 0
			await message.answer(f'Выпало число - {number_casino}')
		elif number_casino % 2 == 0:
			red = 1
			black = 0
			zero = 0
			await message.answer(f'Выпало число - {number_casino}')
		else:
			black =	1
			red = 0
			zero = 0
			await message.answer(f'Выпало число - {number_casino}')
		if choise_casino == 'Red':
			if red == 1:
				number_win = random.randint(1,5)
				if number_win == 1:
					await message.answer('Ты победил!\nУра!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgQAAxkBAAEFsOVjCfd0Pwg8f8MbgTpHINTjzvP2gAACcgADzjkIDZ4tlzE34tf6KQQ')
				elif number_win == 2:
					await message.answer('Молодец!\nУдача на твоей стороне!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKVjC7UpKBJLQZh4QVtiHVMN_1gJJAAC-hMAAqZ-IEiumtCfjdyCEikE')
				elif number_win == 3:
					await message.answer('Воу, ты победил...')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKtjC7Xa1FNu_-Vn4_PyK_KlDZym4QACoxgAArvwwEuKzMnbs96XFykE')
				elif number_win == 4:
					await message.answer('У тебя получилось, поздравляю!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLFjC7jzR1BkKiHsU_Y1LAptoRwhqAAClhUAAqi6IUiHHjYqaGkFBSkE')
				else:
					await message.answer('А ты везучий..')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLNjC7lnvRrNDQbTnf5Dy2zs6ERplAACCRsAAks34UrBNeObsGxRUikE')
				money += bet
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()
			else:
				await lose(message)
				money -= bet
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()	
		elif choise_casino == 'Black':
			if black == 1:
				number_win = random.randint(1,5)
				if number_win == 1:
					await message.answer('Ты победил!\nУра!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgQAAxkBAAEFsOVjCfd0Pwg8f8MbgTpHINTjzvP2gAACcgADzjkIDZ4tlzE34tf6KQQ')
				elif number_win == 2:
					await message.answer('Молодец!\nУдача на твоей стороне!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKVjC7UpKBJLQZh4QVtiHVMN_1gJJAAC-hMAAqZ-IEiumtCfjdyCEikE')
				elif number_win == 3:
					await message.answer('Воу, ты победил...')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKtjC7Xa1FNu_-Vn4_PyK_KlDZym4QACoxgAArvwwEuKzMnbs96XFykE')
				elif number_win == 4:
					await message.answer('У тебя получилось, поздравляю!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLFjC7jzR1BkKiHsU_Y1LAptoRwhqAAClhUAAqi6IUiHHjYqaGkFBSkE')
				else:
					await message.answer('А ты везучий..')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLNjC7lnvRrNDQbTnf5Dy2zs6ERplAACCRsAAks34UrBNeObsGxRUikE')
				money += bet
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()
			else:
				await lose(message)
				money -= bet 
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()	
		elif choise_casino == '1st':
			if number_casino <= 12:
				number_win = random.randint(1,5)
				if number_win == 1:
					await message.answer('Ты победил!\nУра!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgQAAxkBAAEFsOVjCfd0Pwg8f8MbgTpHINTjzvP2gAACcgADzjkIDZ4tlzE34tf6KQQ')
				elif number_win == 2:
					await message.answer('Молодец!\nУдача на твоей стороне!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKVjC7UpKBJLQZh4QVtiHVMN_1gJJAAC-hMAAqZ-IEiumtCfjdyCEikE')
				elif number_win == 3:
					await message.answer('Воу, ты победил...')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKtjC7Xa1FNu_-Vn4_PyK_KlDZym4QACoxgAArvwwEuKzMnbs96XFykE')
				elif number_win == 4:
					await message.answer('У тебя получилось, поздравляю!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLFjC7jzR1BkKiHsU_Y1LAptoRwhqAAClhUAAqi6IUiHHjYqaGkFBSkE')
				else:
					await message.answer('А ты везучий..')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLNjC7lnvRrNDQbTnf5Dy2zs6ERplAACCRsAAks34UrBNeObsGxRUikE')
				money += bet * 2
				await update_casino(money,ID)
				await state.finish()
			else:
				await lose(message)
				money -= bet
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()
		elif choise_casino == '2nd':
			if 12 <= number_casino <= 24:
				number_win = random.randint(1,5)
				if number_win == 1:
					await message.answer('Ты победил!\nУра!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgQAAxkBAAEFsOVjCfd0Pwg8f8MbgTpHINTjzvP2gAACcgADzjkIDZ4tlzE34tf6KQQ')
				elif number_win == 2:
					await message.answer('Молодец!\nУдача на твоей стороне!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKVjC7UpKBJLQZh4QVtiHVMN_1gJJAAC-hMAAqZ-IEiumtCfjdyCEikE')
				elif number_win == 3:
					await message.answer('Воу, ты победил...')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKtjC7Xa1FNu_-Vn4_PyK_KlDZym4QACoxgAArvwwEuKzMnbs96XFykE')
				elif number_win == 4:
					await message.answer('У тебя получилось, поздравляю!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLFjC7jzR1BkKiHsU_Y1LAptoRwhqAAClhUAAqi6IUiHHjYqaGkFBSkE')
				else:
					await message.answer('А ты везучий..')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLNjC7lnvRrNDQbTnf5Dy2zs6ERplAACCRsAAks34UrBNeObsGxRUikE')
				money += bet*2
				await message.answer(f'У вас на счёту - ${money}')	
				await update_casino(money,ID)
				await state.finish()
			else:
				await lose(message)
				money -= bet 
				await message.answer(f'У вас на счёту - ${money}')			 		
				await update_casino(money,ID)
				await state.finish()
		elif choise_casino == '3rd':
			if 24 <= number_casino <= 36:
				number_win = random.randint(1,5)
				if number_win == 1:
					await message.answer('Ты победил!\nУра!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgQAAxkBAAEFsOVjCfd0Pwg8f8MbgTpHINTjzvP2gAACcgADzjkIDZ4tlzE34tf6KQQ')
				elif number_win == 2:
					await message.answer('Молодец!\nУдача на твоей стороне!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKVjC7UpKBJLQZh4QVtiHVMN_1gJJAAC-hMAAqZ-IEiumtCfjdyCEikE')
				elif number_win == 3:
					await message.answer('Воу, ты победил...')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKtjC7Xa1FNu_-Vn4_PyK_KlDZym4QACoxgAArvwwEuKzMnbs96XFykE')
				elif number_win == 4:
					await message.answer('У тебя получилось, поздравляю!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLFjC7jzR1BkKiHsU_Y1LAptoRwhqAAClhUAAqi6IUiHHjYqaGkFBSkE')
				else:
					await message.answer('А ты везучий..')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLNjC7lnvRrNDQbTnf5Dy2zs6ERplAACCRsAAks34UrBNeObsGxRUikE')
				money += bet*2
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()
			else:
				await lose(message)
				money -= bet 
				await message.answer(f'У вас на счёту - ${money}')			 		
				await update_casino(money,ID)
				await state.finish()
		elif choise_casino == 'Number':
			if zero == 1:
				number_win = random.randint(1,5)
				if number_win == 1:
					await message.answer('Ты победил!\nУра!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgQAAxkBAAEFsOVjCfd0Pwg8f8MbgTpHINTjzvP2gAACcgADzjkIDZ4tlzE34tf6KQQ')
				elif number_win == 2:
					await message.answer('Молодец!\nУдача на твоей стороне!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKVjC7UpKBJLQZh4QVtiHVMN_1gJJAAC-hMAAqZ-IEiumtCfjdyCEikE')
				elif number_win == 3:
					await message.answer('Воу, ты победил...')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtKtjC7Xa1FNu_-Vn4_PyK_KlDZym4QACoxgAArvwwEuKzMnbs96XFykE')
				elif number_win == 4:
					await message.answer('У тебя получилось, поздравляю!')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLFjC7jzR1BkKiHsU_Y1LAptoRwhqAAClhUAAqi6IUiHHjYqaGkFBSkE')
				else:
					await message.answer('А ты везучий..')
					await bot.send_sticker(message.from_user.id,sticker='CAACAgIAAxkBAAEFtLNjC7lnvRrNDQbTnf5Dy2zs6ERplAACCRsAAks34UrBNeObsGxRUikE')
				money += bet*35
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()
			else:
				await lose(message)
				money -= bet 
				await message.answer(f'У вас на счёту - ${money}')
				await update_casino(money,ID)
				await state.finish()
		else:
			await message.answer('Такой ставки не существует...')
			await state.finish()			
		await state.finish()		


def register_handler_casino(dp : Dispatcher):
	dp.register_message_handler(start_command,commands=['start','help'])
	dp.register_message_handler(casino,commands=['casino'],state = None)
	dp.register_message_handler(casino,Text(equals='Продолжить✅',ignore_case=True),state=None)
	dp.register_message_handler(cancel_handler,Text(equals='Отмена',ignore_case=True),state='*')
	dp.register_message_handler(info,commands=['info'])
	dp.register_callback_query_handler(info_bet,text='info_for_bet')
	dp.register_callback_query_handler(info_money,text='how_get_money')
	dp.register_callback_query_handler(cb_choice_red,text='Red',state=FSMcasino.Choise)
	dp.register_callback_query_handler(cb_choice_black,text='Black',state=FSMcasino.Choise)
	dp.register_callback_query_handler(cb_choice_1st,text='1st',state=FSMcasino.Choise)
	dp.register_callback_query_handler(cb_choice_2nd,text='2nd',state=FSMcasino.Choise)
	dp.register_callback_query_handler(cb_choice_3rd,text='3rd',state=FSMcasino.Choise)
	dp.register_callback_query_handler(cb_choice_number,text='Zero',state=FSMcasino.Choise)
	dp.register_message_handler(bet_func,state=FSMcasino.bet)
	dp.register_message_handler(wallet_func,commands=['wallet'])
	dp.register_message_handler(admin,commands=['developer'])