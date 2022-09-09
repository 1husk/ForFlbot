from aiogram import types,Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.types import InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton
from create_bot import dp,bot
from aiogram.dispatcher.filters import Text
from handlers import casino
import random
from datetime import date
import psycopg2
from psycopg2.extensions import AsIs


yesorno_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
bank_inline_kb = InlineKeyboardMarkup()
name_change = InlineKeyboardButton('Изменить имя',callback_data='change_name')
money_add_to_bank = InlineKeyboardButton('Положить деньги на карту',callback_data='addmoney')
credit_inlinetbtn = InlineKeyboardButton('Взять кредит',callback_data='credit')
repay_credit_inbtn = InlineKeyboardButton('Погасить кредит',callback_data='repay_credit')
money_take_to_bank = InlineKeyboardButton('Взять деньги с карты',callback_data='takemoney')
money_give_player = InlineKeyboardButton('Перевод денег на другую карту',callback_data='give_money_player')
back_btn = KeyboardButton('❌Отмена❌')
back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
yes_btn = KeyboardButton('Да')
no_btn = KeyboardButton('Нет')
yesorno_kb.row(yes_btn,no_btn)
bank_inline_kb.add(name_change).row(credit_inlinetbtn,repay_credit_inbtn).row(money_add_to_bank,money_take_to_bank,money_give_player)



DB_URL = 'postgres://zivescggovndkf:3c1f9b3b3646a5df732fbf4358fdc2c7a6985418891be785fed9780d5d89d656@ec2-99-81-16-126.eu-west-1.compute.amazonaws.com:5432/d2ja87rob9ne3l'

db_connection_bank = psycopg2.connect(DB_URL, sslmode='require')
db_object = db_connection_bank.cursor()

class FSMchange_name(StatesGroup):
	step_one = State()

class FSMadd_money(StatesGroup):
	money_step = State()

#@dp.callback_query_handler(text='change_name',state=None)
async def changename_stepOne(callback : types.CallbackQuery):
	await callback.message.answer('Введите новое имя')
	await callback.answer()
	await FSMchange_name.step_one.set()

async def addmoney(callback : types.CallbackQuery):
	await callback.message.answer('Введите сумму которую хотите положить на карту',reply_markup=back_markup)
	await callback.answer()
	await FSMadd_money.money_step.set()

async def add_money_stepTwo(message : types.Message, state : FSMContext):
	global db_object,db_connection_bank
	try:
		user = message.from_user.username
		ID = message.from_user.id
		money_want_get = int(message.text)
		db_object.execute(f'SELECT money_casino FROM casino_player WHERE user_id={ID}')
		money_have_tuple = db_object.fetchone()
		if not money_have_tuple:
			await message.reply('Сначало введите /start')
		else:	
			money_have = money_have_tuple[0]
			if money_have >= money_want_get:
				await message.answer('Деньги успешно положены на счёт!')
				money_have -= money_want_get
				db_object.execute('UPDATE casino_player SET money_casino=%s WHERE user_id=%s',(money_have,ID))
				db_object.execute('UPDATE bank SET moneybank=%s WHERE %s = %s',(money_want_get,AsIs('username'),user))
				db_connection_bank.commit()
				await state.finish()
			else:
				await message.reply('У вас нету такой суммы!\nЧтобы проверить сколько у вас денег введите /wallet')
				await state.finish()
	except ValueError:
		await message.answer('Введите сумму без символов и букв')
		await state.finish()	

async def changename_stepTwo(message : types.Message, state : FSMContext):
	global db_object,db_connection_bank
	new_name = str(message.text)
	user = message.from_user.username
	db_object.execute('UPDATE bank SET name=%s WHERE %s=%s',(new_name,AsIs('username'),user))
	db_connection_bank.commit()	
	await state.finish()
	await message.answer('Имя изменено!')
	await message.answer('Чтобы проверить изменения введити /bank')


class FSMbank(StatesGroup):
	create_bank = State()
	name = State()
	age = State()
	birthday = State()

async def start_bank(message : types.Message,State=None):
	global db_object,db_connection_bank
	user = message.from_user.username
	db_object.execute('SELECT createcard FROM bank WHERE %s=%s',(AsIs('username'),user))
	CreateBankCard = db_object.fetchone()
	if not CreateBankCard:
		await FSMbank.create_bank.set()
		await message.reply('Желаете создать банковский счёт?',reply_markup=yesorno_kb)
	else:
		db_object.execute('SELECT name FROM bank WHERE %s = %s',(AsIs('username'),user))
		name_info = db_object.fetchone()
		db_object.execute('SELECT age FROM bank WHERE %s = %s',(AsIs('username'),user))
		age_info = db_object.fetchone()
		db_object.execute('SELECT bankcard FROM bank WHERE %s=%s',(AsIs('username'),user))
		card_bank_info = db_object.fetchone()
		db_object.execute('SELECT moneybank FROM bank WHERE %s=%s',(AsIs('username'),user))
		money_info = db_object.fetchone()
		db_object.execute('SELECT datecreatebank FROM bank WHERE %s=%s',(AsIs('username'),user))
		data_create_bank_info = db_object.fetchone()
		db_object.execute('SELECT credit FROM bank WHERE %s = %s',(AsIs('username'),user))
		credit_bank1 = db_object.fetchone()
		db_object.execute('SELECT datelastcredit FROM bank WHERE %s = %s',(AsIs('username'),user))
		date_credit = db_object.fetchone()
		if date_credit == 0:
			date_credit[0] = 'Никогда'
		else:	
			await message.reply(f'Имя: {name_info[0]}\nЛет: {age_info[0]}\nНомер банковской карты: {card_bank_info[0]}\nДеньги в банке: ${money_info[0]}\nДата регистрации: {data_create_bank_info[0]}\nЗадолженость: ${credit_bank1[0]}\nПоследний раз брал(а) кредит - {date_credit[0]}',reply_markup=bank_inline_kb)	

class FSMtakemoney(StatesGroup):
	take_money_one = State()

async def money_take(callback : types.CallbackQuery,state = None):
	await callback.message.answer('Сколько хотите взять?')
	await FSMtakemoney.take_money_one.set()

async def update_moneytake(arg1,arg2,arg3,arg4):
	global db_object,db_connection_bank
	db_object.execute('UPDATE bank SET moneybank=%s WHERE %s=%s',(arg1,AsIs('username'),arg4))
	db_object.execute('UPDATE casino_player SET money_casino=%s WHERE user_id=%s',(arg3,arg2))
	db_connection_bank.commit()

async def money_take_two(message : types.Message,state : FSMContext):
	global db_object,update_moneytake
	user = message.from_user.username
	Id = message.from_user.id
	try:
		money_take = int(message.text)
		db_object.execute('SELECT moneybank FROM bank WHERE %s = %s',(AsIs('username'),user))
		bank_money1 = db_object.fetchone()
		db_object.execute(f'SELECT money_casino FROM casino_player WHERE user_id = {Id}',)
		money_wallet1 = db_object.fetchone()
		money_wallet = money_wallet1[0]
		bank_money = bank_money1[0]
		if money_take <= bank_money:
			money_wallet += money_take
			bank_money -= money_take
			await update_moneytake(bank_money,Id,money_wallet,user)
			await message.answer('Вы взяли деньги с карты\nЧтобы проверить свой банковский счёт введите /bank')
			await state.finish(А)
		else:
			await message.reply('У вас нет такой суммы на карте..')	
	except ValueError:
		await message.answer('Введите число без символов и букв!')
				
class FSMgive_money(StatesGroup):
	what_card = State()
	how_much_money = State()

async def give_money(callback : types.CallbackQuery, state = None):
	await callback.message.answer('На какую карту хотите сделать перевод?')
	await FSMgive_money.what_card.set()

async def what_card_bank(message : types.Message,state : FSMContext):
	global db_object
	try:
		user = message.from_user.username
		card = int(message.text)
		db_object.execute('SELECT bankcard FROM bank WHERE %s = %s',(AsIs('username'),user))
		card_tuple = db_object.fetchone()
		if card_tuple is None:
			await message.answer('Такой карты не существует')
			await state.finish()
		else:	
			await message.answer('Хорошо, сколько хочешь перевести?')
			await FSMgive_money.next()
			async with state.proxy() as data:
				data['what_card'] = card 
	except:
		await message.reply('Введите номер карты без символов и букв!')
		await state.finish()	

async def update_translate(arg1,arg2,arg3,arg4):
	global db_object,db_connection_bank
	db_object.execute('UPDATE bank SET moneybank=%s WHERE bankcard=%s',(arg1,arg2))
	db_object.execute('UPDATE bank SET moneybank=%s WHERE %s = %s',(arg3,AsIs('username'),arg4))
	db_connection_bank.commit()

async def how_many_money(message : types.Message,state : FSMContext):
	global db_object,update_translate
	async with state.proxy() as data: 
		card_bank = data['what_card']
		print('try...')
		try:
			ID = message.from_user.username
			user = message.from_user.username
			money_give = int(message.text)
			db_object.execute('SELECT moneybank FROM bank WHERE %s=%s',(AsIs('username'),user))
			money_in_bank1 = db_object.fetchone()
			db_object.execute(f'SELECT moneybank FROM bank WHERE bankcard={card_bank}',)
			money_player1 = db_object.fetchone()
			db_object.execute(f'SELECT uid FROM bank WHERE bankcard={card_bank}')
			money_player_id1 = db_object.fetchone()
			money_in_bank = money_in_bank1[0]
			money_player = money_player1[0]
			money_player_id = money_player_id1[0]
			print('None?')
			if not money_in_bank1:
				await message.answer('Сначало создай банковский счёт!')
				print('Yes')
			else:
				print('No')	
				if money_in_bank >= money_give:
					print('transction...')
					money_on_bank = money_in_bank - money_give
					money_translate = money_player + money_give
					await update_translate(money_translate,card_bank,money_on_bank,ID)
					await message.answer('Перевод прошел успешно!')
					print(money_player_id)
					await bot.send_message(int(money_player_id),f'Вам на счёт перевели - ${money_give}')
					await state.finish()
				else:
					await message.answer('У вас нет столько денег на карте!')
					await state.finish()	
		except ValueError:
			await message.answer('Введите число без символов и букв!')
			await state.finish()

class FSMrepay_credit(StatesGroup):
	repay_one = State()


async def repay_loan(callback : types.CallbackQuery, state = None):
	await callback.message.answer('Введите сумму которую хотите погасить')
	await FSMrepay_credit.repay_one.set()

async def update_repay(arg1,arg2,arg3):
	global db_object,db_connection_bank
	db_object.execute('UPDATE bank SET moneybank=%s WHERE %s=%s',(arg1,AsIs('username'),arg2))
	db_object.execute('UPDATE bank SET credit=%s WHERE %s=%s',(arg3,AsIs('username'),arg2))
	db_connection_bank.commit()	

async def repay_loan_two(message : types.Message, state : FSMContext):
	global db_object,update_repay
	user = message.from_user.username
	try:
		repay = int(message.text)
		db_object.execute('SELECT credit FROM bank WHERE %s=%s',(AsIs('username'),user))
		credit = db_object.fetchone()	
		db_object.execute('SELECT moneybank FROM bank WHERE %s=%s',(AsIs('username'),user))
		money_in_bank = db_object.fetchone()
		if money_in_bank[0] >= repay:
			if repay <= credit[0]:
				credit_on = credit[0] - repay
				money_on = money_in_bank[0] - repay
				await update_repay(money_on,user,credit_on)
				await message.answer('Готово!')
				await state.finish()				
			else:
				await message.answer('Вы ввели сумму больше вашего кредита\nЧтобы узнать сколько у вас задолжености введите /bank')
				await state.finish()	
		else:
			await message.reply('У вас недостаточно денег в банке')
			await state.finish()	
	except ValueError:
		await message.answer('Введите число без символов и букв')		

class FSMcredit(StatesGroup):
	credit_one = State()

async def update_date_credit(arg1,arg2):
	global db_object,db_connection_bank
	db_object.execute('UPDATE bank SET creditcanget=%s WHERE %s=%s',(1000,AsIs('username'),arg2))
	db_object.execute('UPDATE bank SET datelastcredit=%s WHERE %s=%s',(arg1,AsIs('username'),arg2))
	db_connection_bank.commit()

async def get_credit(callback : types.CallbackQuery, state = None):
	global db_object,update_date_credit,db_connection_bank
	user = callback.from_user.username
	db_object.execute('SELECT credit FROM bank WHERE %s=%s',(AsIs('username'),user))
	credit_tuple = db_object.fetchone()
	if credit_tuple is None:
		await callback.message.answer('Сначало введите /start')
	else:
		credit_in_bank = credit_tuple[0]
		db_object.execute('SELECT datelastcredit FROM bank WHERE %s=%s',(AsIs('username'),user))
		last_credit_tuple = db_object.fetchone()
		credit_date = last_credit_tuple[0]
		last_credit = date.today()
		db_object.execute('SELECT creditcanget FROM bank WHERE %s=%s',(AsIs('username'),user))
		credit_check = db_object.fetchone()
		if str(credit_date)	!= str(last_credit):
			if credit_check[0] == 0:
				update_date_credit(last_credit,user)
				await callback.message.answer('Вы можете взять кредит на сумму = $1000')
				db_object.execute('UPDATE bank SET creditcanget=%s WHERE %s=%s',(1000,AsIs('username'),user))
				db_connection_bank
				await FSMcredit.credit_one.set()
			elif credit_check[0] != 0:
				await callback.message.answer(f'Вы можете взять кредит на сумму - ${credit_check[0]}')
				await FSMcredit.credit_one.set()	 
		elif str(credit_date) == str(last_credit):
			if credit_check == 0:
				await callback.message.answer('Вы сегодня брали кредит, приходите завтра...')	
				await state.finish()
			else:
				await callback.message.answer(f'Вы можете взять кредит на сумму - ${credit_check[0]}')
				await FSMcredit.credit_one.set()		

async def update_credit(arg1,arg2,arg3,arg4,arg5):
	global db_object,db_connection_bank
	db_object.execute('UPDATE bank SET moneybank=%s WHERE %s=%s',(arg3,AsIs('username'),arg2))
	db_object.execute('UPDATE bank SET credit=%s WHERE %s=%s',(arg1,AsIs('username'),arg2))
	db_object.execute('UPDATE bank SET datelastcredit=%s WHERE %s=%s',(arg4,AsIs('username'),arg2))
	db_object.execute('UPDATE bank SET creditcanget=%s WHERE %s=%s',(arg5,AsIs('username'),arg2))
	db_connection_bank.commit()

async def get_credit_step_two(message : types.Message, state : FSMContext):
	global db_object,update_credit,db_connection_bank
	user = message.from_user.username
	db_object.execute('SELECT datelastcredit FROM bank WHERE %s=%s',(AsIs('username'),user))
	last_credit_tuple = db_object.fetchone()
	credit_date = last_credit_tuple[0]
	db_object.execute('SELECT credit FROM bank WHERE %s=%s',(AsIs('username'),user))
	credit_tuple = db_object.fetchone()
	credit_in_bank = credit_tuple[0]
	last_credit = date.today()
	try:
		if str(last_credit) != str(credit_date): 				
			credit1 = int(message.text)
			db_object.execute('SELECT creditcanget FROM bank WHERE %s=%s',(AsIs('username'),user))
			credit_check = db_object.fetchone()
			if credit_check[0] >= credit1:
				db_object.execute('SELECT moneybank FROM bank WHERE %s=%s',(AsIs('username'),user))
				money_tuple = db_object.fetchone()
				money_wallet = credit1 + money_tuple[0]
				credit_on_bank = int(credit_in_bank) + credit1
				credit_get = credit_check[0] - credit1
				await update_credit(credit_on_bank,user,money_wallet,last_credit,credit_get)
				await message.answer('Вы взяли кредит\nЧтобы посмотреть свой счёт введите /bank')			
				await state.finish()
				db_connection_bank.commit()
			else:
				await message.answer(f'Вы не можете взять столько денег, допустимая сумма - ${credit_check[0]}')
				await state.finish()
		else:
			if credit_check[0] != 0:
				db_object.execute('SELECT moneybank FROM bank WHERE %s=%s',(AsIs('username'),user))
				money_tuple = db_object.fetchone()
				money_wallet = credit1 + money_tuple[0]
				credit_on_bank = int(credit_in_bank) + credit1
				credit_get = credit_check[0] - credit1
				await update_credit(credit_on_bank,user,money_wallet,last_credit,credit_get)
				await message.answer('Вы взяли кредит\nЧтобы посмотреть свой счёт введите /bank')			
				await state.finish()
				db_connection_bank.commit()
			else:		
				await message.answer(f'Вы сегодня уже брали кредит, приходите завтра')
				await state.finish()		
	except ValueError:
		await message.answer('Введите число без символов и букв!')	

async def yesorno_bank(message : types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['create_bank'] = message.text.lower()
		if data['create_bank'] == 'да':
			await message.answer('Как вас зовут?')
			await FSMbank.next()
		elif data['create_bank'] == 'нет':
			await message.answer('Как пожелаете..')
			await state.finish()
		else:
			await message.reply('Введите Да или Нет!')		

async def name_bank(message : types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text
	await message.answer('Хорошо, сколько вам лет?')
	await message.answer('Внимание!\n Даные о возрасте невозможно будет изменить!')
	await FSMbank.next()

async def age_bank(message : types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['age'] = message.text
	await FSMbank.next()

async def birthday_bank(message : types.Message, state: FSMContext):
	global db_object,db_connection_bank
	print('generate card....')
	async with state.proxy() as data:
		data['birthday'] = message.text
	await message.answer('Генeрируеться номер карты')	
	user = message.from_user.username
	generate_card = random.randint(1111111111111111,9999999999999999)
	number_card = generate_card
	async with state.proxy() as data:
		await message.answer(f'Ваша банковская карта: {number_card}')
		print('succesfully')
		today = date.today()
		data['count3'] = 1
		name1 = data['name']
		age1 = data['age']
		data_create = today
		ID = message.from_user.id
		db_object.execute('INSERT INTO bank(id,username,name,age,moneybank,credit,createcard,datelastcredit,creditcanget,datecreatebank,bankcard) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(ID,user,name1,age1,0,0,True,0,1000,data_create,number_card))
		db_connection_bank.commit()
		await message.answer('Готово! Чтобы проверить банковский счёт введите /bank')
		await state.finish()



def register_handler_bank(dp : Dispatcher):
	dp.register_message_handler(start_bank,commands='bank')
	dp.register_message_handler(start_bank,Text(equals='Банк',ignore_case=True))
	dp.register_message_handler(yesorno_bank,state=FSMbank.create_bank)
	dp.register_message_handler(name_bank,state=FSMbank.name)
	dp.register_message_handler(age_bank,state=FSMbank.age)
	dp.register_message_handler(birthday_bank,state=FSMbank.birthday)
	dp.register_callback_query_handler(changename_stepOne,text='change_name',state=None)
	dp.register_message_handler(changename_stepTwo,state=FSMchange_name.step_one)	
	dp.register_callback_query_handler(addmoney,text='addmoney',state=None)
	dp.register_message_handler(add_money_stepTwo,state=FSMadd_money.money_step )
	dp.register_callback_query_handler(get_credit,text='credit',state=None)
	dp.register_message_handler(get_credit_step_two,state=FSMcredit.credit_one)
	dp.register_callback_query_handler(repay_loan,text='repay_credit',state = None)
	dp.register_message_handler(repay_loan_two,state = FSMrepay_credit.repay_one)
	dp.register_callback_query_handler(money_take,text='takemoney',state=None)
	dp.register_message_handler(money_take_two,state=FSMtakemoney.take_money_one)
	dp.register_callback_query_handler(give_money,text='give_money_player',state=None)
	dp.register_message_handler(what_card_bank,state=FSMgive_money.what_card)
	dp.register_message_handler(how_many_money,state=FSMgive_money.how_much_money)