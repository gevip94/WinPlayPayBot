from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, func
from database.db import Base

# 👤 Пользователь
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    full_name = Column(String)
    balance = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    cups = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)

# 💸 Заявка на вывод
class WithdrawalRequest(Base):
    __tablename__ = "withdrawals"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    amount = Column(Integer)
    card_number = Column(String)
    status = Column(String, default="pending")  # 👈 Обязательно для фильтрации
    created_at = Column(DateTime, default=func.now())

# ❓ Вопрос
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    option_1 = Column(String, nullable=False)
    option_2 = Column(String, nullable=False)
    option_3 = Column(String, nullable=False)
    option_4 = Column(String, nullable=False)
    correct_option = Column(Integer, nullable=False)  # 1–4
    game_number = Column(Integer, nullable=False)

# 🏆 Результаты игр
class GameResult(Base):
    __tablename__ = "game_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    score = Column(Integer)
    game_number = Column(Integer)
    date = Column(DateTime, default=func.current_date())
