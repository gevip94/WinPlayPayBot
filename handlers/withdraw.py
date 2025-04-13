from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import async_session
from database.models import User, WithdrawalRequest

router = Router()

class WithdrawForm(StatesGroup):
    amount = State()
    card = State()
    confirm = State()

@router.callback_query(F.data == "withdraw")
async def start_withdraw(callback: types.CallbackQuery, state: FSMContext):
    print("✅ Кнопка 'Вывести деньги' сработала")  # тест лог
    await callback.message.answer("💸 Введите сумму для вывода:")
    await state.set_state(WithdrawForm.amount)
    await callback.answer()

@router.message(WithdrawForm.amount)
async def get_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
    except:
        return await message.answer("❌ Введите корректную сумму в цифрах.")

    await state.update_data(amount=amount)
    await message.answer("💳 Введите номер вашей банковской карты:")
    await state.set_state(WithdrawForm.card)

@router.message(WithdrawForm.card)
async def get_card(message: types.Message, state: FSMContext):
    await state.update_data(card=message.text)
    data = await state.get_data()

    text = (
        f"📝 Подтвердите заявку на вывод:\n\n"
        f"💰 Сумма: <b>{data['amount']}₽</b>\n"
        f"💳 Карта: <b>{data['card']}</b>"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="confirm_withdraw")
    kb.button(text="❌ Отмена", callback_data="cancel_withdraw")

    await message.answer(text, reply_markup=kb.as_markup())
    await state.set_state(WithdrawForm.confirm)

@router.callback_query(F.data == "confirm_withdraw")
async def confirm_withdraw(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    async with async_session() as session:
        user = await session.get(User, user_id)

        if user.balance < data["amount"]:
            await callback.message.edit_text("❌ Недостаточно средств на балансе.")
            await state.clear()
            return

        user.balance -= data["amount"]
        request = WithdrawalRequest(
            user_id=user_id,
            amount=data["amount"],
            card_number=data["card"]
        )
        session.add(request)
        await session.commit()

    await callback.message.edit_text("✅ Заявка на вывод принята. Ожидайте вручную.")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_withdraw")
async def cancel_withdraw(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Вывод отменён.")
    await callback.answer()
