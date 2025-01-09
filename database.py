import aiosqlite

DB_NAME = 'quiz_bot.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS results (user_id INTEGER PRIMARY KEY, result TEXT)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?,?)', (user_id, index))
        await db.commit()

async def save_result(user_id, result):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT result FROM results WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                new_result = results[0] + '\n' + result
                await db.execute('UPDATE results SET result = (?) WHERE user_id = (?)', (new_result, user_id))
            else:
                await db.execute('INSERT INTO results (user_id, result) VALUES (?,?)', (user_id, result))
            await db.commit()

async def get_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT result FROM results WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                correct_answers = results[0].count('Верно!')
                wrong_answers = results[0].count('Неправильно.')
                return f'Количество правильных ответов: {correct_answers}\nКоличество неправильных ответов: {wrong_answers}'
            else:
                return 'Вы еще не проходили квиз.'