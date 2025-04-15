import asyncio
import random
import logging
from aiogram import types, F, Router
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,  FSInputFile
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import uvicorn

bot = None  # Ceci sera défini dans main.py
user_last_signal_time = {}
router = Router()
# bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
# dp = Dispatcher()
CHANNEL_ID = "@mine1wgroup"
image_path = "photo.jpg"
welcome_message = """<b><i>⚙️ les nouvelles technologies ont permis d'obtenir des cotes futures directement à partir du jeu mine</i></b>

⚙️ administrator - @Minepro1w 🎰

<i>Voici comment jouer ✨</i>

<blockquote>1. S'inscrire sur 1win avec le code promo <b>CASHF</b></blockquote>

<blockquote>2. Faire un dépôt minimum de 2000f pour activer le compte</blockquote>

<blockquote>3. Trouver le jeu Mine sur 1win</blockquote>

<blockquote>4. Cliquer sur <b>GET SIGNAL</b> pour avoir une prédiction 100% à jouer</blockquote>

                    <a href="https://1wrjmw.com/v3/2158/1win-mines?p=qn1x">🔁VIDEO🔁</a>

           <a href="https://1wrjmw.com/v3/2158/1win-mines?p=qn1x">LIEN D'INSCRIPTION</a>

<b>NB : Chaque étape est importante pour faire fonctionner les prédictions.</b>
"""



# Clavier avec le bouton "Get Signal"
kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎯 Get Signal")]], resize_keyboard=True)

# Vérifie si l'utilisateur est abonné au canal
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False
    
# Fonction pour générer une grille aléatoire
def generate_grid():
    grid = [["⬛" for _ in range(5)] for _ in range(5)]
    stars_positions = random.sample(range(25), 4)  # 5 étoiles aléatoires
    for pos in stars_positions:
        row, col = divmod(pos, 5)
        grid[row][col] = "⭐"
    return "\n".join("".join(row) for row in grid)

@router.message(lambda message: message.text == "🎯 Get Signal")
async def send_signal(message: types.Message):

    user_id = message.from_user.id
    now = datetime.now()

    last_time = user_last_signal_time.get(user_id)
    if last_time and now - last_time < timedelta(seconds=60):
        remaining = 60 - int((now - last_time).total_seconds())
        await message.answer(f"⏳ Patiente encore {remaining} seconde(s) avant de demander un nouveau signal.")
        return

    # Met à jour le dernier temps
    user_last_signal_time[user_id] = now

    grid = generate_grid()
    signal_text = (f"✅ {hbold('NOUVEAU SIGNAL')}\n"
                   f"Valide pendant 3 min...\n"
                   f"Piège : 3 💣\n\n"
                   f"{grid}\n\n"
                   f"👉 <a href='https://1wrjmw.com/v3/2158/1win-mines?p=qn1x'>Joue ici !</a>\n\n"
                   "❓/how_to_play")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
             [InlineKeyboardButton(text="JOUER 💡", url="https://1wrjmw.com/v3/2158/1win-mines?p=qn1x")]            # (text="COMMENT JOUER ?", callback_data="how_to_play")
        ]
    )
    await message.answer(signal_text, parse_mode="HTML", reply_markup=keyboard)
# await message.answer(signal_text, reply_markup=kb)

@router.callback_query(lambda c: c.data == "how_to_play")
async def how_to_play(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 LIEN D'INSCRIPTION", url="https://1wrjmw.com/v3/2158/1win-mines?p=qn1x")]
                                  ]
    )
    photo = FSInputFile(image_path)
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=photo,
        caption=welcome_message,
        parse_mode="HTML",
        reply_markup=keyboard
)

@router.message()
async def start_command(message: types.Message):

    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        join_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="S’abonner au canal", url="https://t.me/mine1wgroup")],
            [InlineKeyboardButton(text="✅ Vérifier", callback_data="check_sub")]
        ])
        await message.answer("🔒 Pour accéder au bot, tu dois t’abonner à notre canal.", reply_markup=join_button)
        return
    
    
    user_id = str(message.from_user.id)
    args = message.text.split()
    photo = FSInputFile(image_path)
   
    await callback.message.answer_photo(
    photo=photo,
    caption=welcome_message,
    parse_mode="HTML",
    reply_markup=keyboard
    )
    await message.answer("Appuie sur '🎯 Get Signal' pour recevoir un signal.", reply_markup=kb)

    # await callback.message.edit_caption("Appuie sur '🎯 Get Signal' pour recevoir un signal.", reply_markup=kb)
# vérifier l’abonnement
@router.callback_query(F.data == "check_sub")
async def check_subscription_callback(callback: types.CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)
    if is_subscribed:
        await callback.message.delete()
        await start_command(callback.message)
    else:
        await callback.answer("Tu n'es pas encore abonné.", show_alert=True)

# Démarrer le bot

# async def main():
#     logging.basicConfig(level=logging.INFO)
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())
