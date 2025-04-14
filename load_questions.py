# load_questions.py
import asyncio
from database.db import async_session
from database.models import Question

# test auto-deploy 14:30


questions = [
    Question(
        text="Кто выиграл чемпионат мира 2018 года?",
        option_1="Бразилия",
        option_2="Франция",
        option_3="Хорватия",
        option_4="Германия",
        correct_option=2,
        game_number=1
    ),
    Question(
        text="Сколько игроков в футбольной команде на поле?",
        option_1="9",
        option_2="10",
        option_3="11",
        option_4="12",
        correct_option=3,
        game_number=1
    ),
    Question(
        text="В каком году прошли Олимпийские игры в Токио?",
        option_1="2016",
        option_2="2020",
        option_3="2021",
        option_4="2022",
        correct_option=3,
        game_number=1
    ),
    Question(
        text="Сколько таймов в футбольном матче?",
        option_1="1",
        option_2="2",
        option_3="3",
        option_4="4",
        correct_option=2,
        game_number=1
    ),
    Question(
        text="Как называется трофей чемпионата мира по футболу?",
        option_1="Кубок Европы",
        option_2="Кубок планеты",
        option_3="Золотой мяч",
        option_4="Кубок мира FIFA",
        correct_option=4,
        game_number=1
    ),
]

async def load():
    async with async_session() as session:
        session.add_all(questions)
        await session.commit()

asyncio.run(load())
