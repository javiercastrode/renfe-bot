"""Módulo principal del bot interactivo: FSM fluido, filtrado horario preciso y manejo de múltiples rutas."""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from telebot import async_telebot, asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states import State, StatesGroup
from telebot.states.asyncio.context import StateContext
from telebot.states.asyncio.middleware import StateMiddleware
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import get_bot_token
from errors import InvalidDWRToken, InvalidTrainRideFilter
from messages import user_messages as msg, get_tickets_message
from models import TrainRideFilter, StationRecord
from scraper import Scraper
from validators import validate_station, validate_date, validate_float


class SearchStates(StatesGroup):
    origin = State()
    destination = State()
    departure_date = State()
    needs_return = State()
    return_date = State()
    max_price = State()
    max_duration_minutes = State()
    max_departure_hour = State()


TOKEN = get_bot_token()
state_storage = StateMemoryStorage()
bot = async_telebot.AsyncTeleBot(TOKEN, state_storage=state_storage)

active_searches: Dict[str, Dict[str, Any]] = {}

def validate_time_format(text: str) -> Optional[str]:
    text = text.replace(" (Omitir)", "").strip()
    if text == "0":
        return text
    try:
        datetime.strptime(text, "%H:%M")
        return text
    except ValueError:
        return None

# --- TECLADOS INTERACTIVOS ---

def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔍 Nueva Búsqueda", callback_data="action_buscar"),
        InlineKeyboardButton("📋 Mis Búsquedas", callback_data="action_listar"),
        InlineKeyboardButton("ℹ️ Ayuda", callback_data="action_ayuda")
    )
    return markup

def get_active_searches_kb(chat_id: int, action_prefix: str):
    markup = InlineKeyboardMarkup(row_width=1)
    user_searches = {s_id: data for s_id, data in active_searches.items() if data["chat_id"] == chat_id}

    if not user_searches:
        return None

    for s_id, data in user_searches.items():
        ctx = data["ctx"]
        origin = ctx.get("origin").name if ctx.get("origin") else "?"
        destination = ctx.get("destination").name if ctx.get("destination") else "?"
        dep_date = ctx["departure_date"].strftime("%d/%m") if ctx.get("departure_date") else "?"

        btn_text = f"{origin} ➡️ {destination} ({dep_date})"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"{action_prefix}_{s_id}"))

    markup.add(InlineKeyboardButton("❌ Cerrar Menú", callback_data="action_close"))
    return markup

def get_yes_no_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Sí", "No")
    return markup

def get_skip_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("0 (Omitir)")
    return markup


# --- COMANDOS BÁSICOS ---

@bot.message_handler(commands=["start"])
async def send_welcome(message: Message, state: StateContext):
    assert message.from_user is not None
    await bot.send_message(
        message.chat.id,
        msg["welcome"].format(message.from_user.first_name) + "\n\nSelecciona una opción del menú:",
        reply_markup=get_main_menu()
    )

@bot.message_handler(commands=["ayuda"])
async def send_help(message: Message):
    help_text = (
        "🤖 *Bot de Trenes - Ayuda*\n\n"
        "• `/buscar` - Iniciar configuración de búsqueda.\n"
        "• `/mis_busquedas` - Listar activas.\n"
        "• `/ver` - Consultar disponibilidad actual.\n"
        "• `/cancelar` - Detener una búsqueda o asistente.\n"
    )
    await bot.send_message(message.chat.id, help_text, parse_mode="Markdown", reply_markup=get_main_menu())


# --- MENÚS DE SELECCIÓN (VER / CANCELAR) ---

@bot.message_handler(commands=["mis_busquedas"])
async def list_searches(message: Message):
    chat_id = message.chat.id
    user_searches = {s_id: data for s_id, data in active_searches.items() if data["chat_id"] == chat_id}

    if not user_searches:
        await bot.send_message(message.chat.id, "🔍 No tienes búsquedas activas.", reply_markup=get_main_menu())
        return

    response = "📋 *Tus búsquedas activas:*\n\n"
    for s_id, data in user_searches.items():
        ctx = data["ctx"]
        origin = ctx.get("origin").name
        destination = ctx.get("destination").name

        dep_date = ctx["departure_date"].strftime("%d/%m/%Y")
        min_h = ctx["departure_date"].strftime("%H:%M")
        max_h = ctx.get("max_departure_hour") or "23:59"

        response += (f"🆔 `{s_id}`\n"
                     f" 🚉 {origin} ➡️ {destination}\n"
                     f" 📅 Salida: {dep_date}\n"
                     f" ⏰ Franja: {min_h} - {max_h}\n\n")

    await bot.send_message(message.chat.id, response, parse_mode="Markdown")

@bot.message_handler(commands=["ver"])
async def view_search_cmd(message: Message):
    markup = get_active_searches_kb(message.chat.id, "ver")
    if markup:
        await bot.send_message(message.chat.id, "👇 *Selecciona la búsqueda que quieres consultar ahora mismo:*", parse_mode="Markdown", reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "No tienes búsquedas activas en este momento.")

@bot.message_handler(commands=["cancelar"])
async def cancel_search_cmd(message: Message, state: StateContext):
    current_state = await state.get()
    if current_state:
        await state.delete()
        await bot.send_message(message.chat.id, msg.get("cancel_params", "Configuración cancelada."), reply_markup=ReplyKeyboardRemove())
        return

    markup = get_active_searches_kb(message.chat.id, "cancel")
    if markup:
        await bot.send_message(message.chat.id, "👇 *Selecciona la búsqueda que deseas detener:*", parse_mode="Markdown", reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "No tienes búsquedas activas en este momento.")


# --- HANDLER DE BOTONES INLINE (CALLBACKS) ---

@bot.callback_query_handler(func=lambda call: True)
async def handle_callbacks(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    await bot.answer_callback_query(call.id)

    if data == "action_buscar":
        await bot.delete_message(chat_id, call.message.message_id)
        await bot.set_state(user_id, SearchStates.origin, chat_id)
        await bot.send_message(chat_id, msg["start"], reply_markup=ReplyKeyboardRemove())

    elif data == "action_listar":
        await bot.delete_message(chat_id, call.message.message_id)
        await list_searches(call.message)

    elif data == "action_ayuda":
        await bot.delete_message(chat_id, call.message.message_id)
        await send_help(call.message)

    elif data == "action_close":
        await bot.delete_message(chat_id, call.message.message_id)

    elif data.startswith("cancel_"):
        search_id = data.split("_")[1]
        if search_id in active_searches and active_searches[search_id]["chat_id"] == chat_id:
            active_searches[search_id]["task"].cancel()
            del active_searches[search_id]
            await bot.edit_message_text(f"✅ Búsqueda `{search_id}` detenida con éxito.", chat_id, call.message.message_id)
        else:
            await bot.edit_message_text("❌ La búsqueda ya no existe.", chat_id, call.message.message_id)

    elif data.startswith("ver_"):
        search_id = data.split("_")[1]
        await bot.edit_message_text(f"🔄 Consultando disponibilidad para `{search_id}`...", chat_id, call.message.message_id)
        await execute_immediate_search(chat_id, search_id)


# --- ASISTENTE DE CONFIGURACIÓN (FSM) ---

@bot.message_handler(commands=["buscar"])
async def start_search_cmd(message: Message, state: StateContext):
    await state.set(SearchStates.origin)
    await bot.send_message(message.chat.id, msg["start"], reply_markup=ReplyKeyboardRemove())

@bot.message_handler(state=SearchStates.origin)
async def origin_get(message: Message, state: StateContext):
    res = validate_station(message.text)
    if not res or not getattr(res, "station", None):
        await bot.send_message(message.chat.id, getattr(res, "error_message", "Origen inválido."))
    else:
        await state.set(SearchStates.destination)
        await state.add_data(origin=res.station)
        await bot.send_message(message.chat.id, msg["destination"])

@bot.message_handler(state=SearchStates.destination)
async def destination_get(message: Message, state: StateContext):
    res = validate_station(message.text)
    if not res or not getattr(res, "station", None):
        await bot.send_message(message.chat.id, getattr(res, "error_message", "Destino inválido."))
    else:
        await state.set(SearchStates.departure_date)
        await state.add_data(destination=res.station)
        await bot.send_message(message.chat.id, "📅 ¿Qué día y a partir de qué hora sales? (Ej: 15/10/2026 08:00)")

@bot.message_handler(state=SearchStates.departure_date)
async def departure_date_get(message: Message, state: StateContext):
    res = validate_date(message.text)
    if not res or not getattr(res, "date", None):
        await bot.send_message(message.chat.id, "❌ Fecha/hora inválida. Usa el formato DD/MM/YYYY HH:MM.")
    else:
        await bot.send_message(message.chat.id, msg["confirm_date"].format(res.date.strftime("%d/%m/%Y %H:%M")))
        await state.set(SearchStates.needs_return)
        await state.add_data(departure_date=res.date)
        await bot.send_message(message.chat.id, msg["needs_return"], reply_markup=get_yes_no_kb())

@bot.message_handler(state=SearchStates.needs_return)
async def return_get(message: Message, state: StateContext):
    if message.text and message.text.lower() in ["sí", "si", "s", "y", "yes"]:
        await state.set(SearchStates.return_date)
        await bot.send_message(message.chat.id, "📅 ¿Qué día y a partir de qué hora vuelves? (Ej: 20/10/2026 15:00)", reply_markup=ReplyKeyboardRemove())
    else:
        await state.set(SearchStates.max_price)
        await bot.send_message(message.chat.id, "💰 Indica el precio máximo (o pulsa Omitir):", reply_markup=get_skip_kb())

@bot.message_handler(state=SearchStates.return_date)
async def return_date_get(message: Message, state: StateContext):
    res = validate_date(message.text)
    if not res or not getattr(res, "date", None):
        await bot.send_message(message.chat.id, "❌ Fecha/hora inválida. Usa el formato DD/MM/YYYY HH:MM.")
    else:
        await bot.send_message(message.chat.id, msg["confirm_date"].format(res.date.strftime("%d/%m/%Y %H:%M")))
        await state.add_data(return_date=res.date)
        await state.set(SearchStates.max_price)
        await bot.send_message(message.chat.id, "💰 Indica el precio máximo (o pulsa Omitir):", reply_markup=get_skip_kb())

@bot.message_handler(state=SearchStates.max_price)
async def ask_for_max_price(message: Message, state: StateContext):
    clean_text = message.text.replace(" (Omitir)", "").strip() if message.text else "0"
    parsed = validate_float(clean_text)
    if not parsed:
        await bot.send_message(message.chat.id, getattr(parsed, "error_message", "Precio inválido."), reply_markup=get_skip_kb())
    else:
        await state.add_data(max_price=None if parsed.number == 0 else parsed.number)
        await state.set(SearchStates.max_duration_minutes)
        await bot.send_message(message.chat.id, "⏱ Indica la duración máxima en minutos (o pulsa Omitir):", reply_markup=get_skip_kb())

@bot.message_handler(state=SearchStates.max_duration_minutes)
async def get_max_duration(message: Message, state: StateContext):
    clean_text = message.text.replace(" (Omitir)", "").strip() if message.text else "0"
    parsed = validate_float(clean_text)
    if not parsed:
        await bot.send_message(message.chat.id, getattr(parsed, "error_message", "Duración inválida."), reply_markup=get_skip_kb())
    else:
        await state.add_data(max_duration_minutes=None if parsed.number == 0 else parsed.number)
        await state.set(SearchStates.max_departure_hour)
        await bot.send_message(message.chat.id, "🌃 Indica la **hora máxima** de salida (ej: `22:00`) o pulsa Omitir:", parse_mode="Markdown", reply_markup=get_skip_kb())

@bot.message_handler(state=SearchStates.max_departure_hour)
async def get_max_hour(message: Message, state: StateContext):
    valid_time = validate_time_format(message.text if message.text else "0")
    if valid_time is None:
        await bot.send_message(message.chat.id, "⚠️ Formato inválido. Usa `HH:MM` (ej: `22:00`) o pulsa Omitir.", reply_markup=get_skip_kb())
    else:
        await state.add_data(max_departure_hour=None if valid_time == "0" else valid_time)
        await finalize_and_launch(message.chat.id, state)


# --- LÓGICA DE TAREAS Y BACKGROUND ---

async def finalize_and_launch(chat_id: int, state: StateContext):
    async with state.data() as data:
        ctx = dict(data)
    await state.delete()

    search_id = uuid.uuid4().hex[:6]
    task = asyncio.create_task(continuous_search_worker(search_id, chat_id, ctx))

    active_searches[search_id] = {
        "task": task, "chat_id": chat_id, "ctx": ctx,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    min_h = ctx["departure_date"].strftime("%H:%M")
    max_h = ctx.get("max_departure_hour") or "23:59"

    msg_text = (f"🚀 *¡Búsqueda programada!*\n\n"
                f"🆔 ID: `{search_id}`\n"
                f"🛤 {ctx['origin'].name} ➡️ {ctx['destination'].name}\n"
                f"📅 {ctx['departure_date'].strftime('%d/%m/%Y')}\n"
                f"⏰ Franja Ida: {min_h} - {max_h}\n")

    if ctx.get("return_date"):
        min_ret_h = ctx["return_date"].strftime("%H:%M")
        msg_text += f"\n📅 Vuelta: {ctx['return_date'].strftime('%d/%m/%Y')}\n"
        msg_text += f"⏰ Franja Vuelta: {min_ret_h} - {max_h}\n"

    msg_text += "\nEl bot te avisará automáticamente de cambios."

    await bot.send_message(chat_id, msg_text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())


async def execute_immediate_search(chat_id: int, search_id: str):
    if search_id not in active_searches:
        await bot.send_message(chat_id, "❌ La búsqueda ya no está activa.")
        return

    ctx = active_searches[search_id]["ctx"]
    try:
        scraper = Scraper(ctx["origin"], ctx["destination"], ctx["departure_date"], ctx.get("return_date"))
        trains = scraper.get_trainrides()

        dep_filter = TrainRideFilter(
            origin=ctx["origin"].name, destination=ctx["destination"].name,
            departure_date=ctx["departure_date"], min_departure_hour=None,
            max_departure_hour=ctx.get("max_departure_hour"), max_duration_minutes=ctx.get("max_duration_minutes"),
            max_price=ctx.get("max_price")
        )

        try:
            dep_trains = dep_filter.filter_rides(trains)
        except InvalidTrainRideFilter:
            dep_trains = []

        if dep_trains:
            await bot.send_message(chat_id, f"✅ *Ida ({search_id}):*\n" + get_tickets_message(dep_trains, ctx["origin"], ctx["destination"]), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id, "⏳ Sin coincidencias exactas de ida actualmente.")

        if ctx.get("return_date"):
            ret_filter = TrainRideFilter(
                origin=ctx["destination"].name, destination=ctx["origin"].name,
                departure_date=ctx["return_date"], min_departure_hour=None,
                max_departure_hour=ctx.get("max_departure_hour"), max_duration_minutes=ctx.get("max_duration_minutes"),
                max_price=ctx.get("max_price")
            )

            try:
                ret_trains = ret_filter.filter_rides(trains)
            except InvalidTrainRideFilter:
                ret_trains = []

            if ret_trains:
                await bot.send_message(chat_id, f"✅ *Vuelta ({search_id}):*\n" + get_tickets_message(ret_trains, ctx["destination"], ctx["origin"]), parse_mode="Markdown")
            else:
                await bot.send_message(chat_id, "⏳ Sin coincidencias exactas de vuelta actualmente.")

    except Exception as e:
        await bot.send_message(chat_id, f"❌ Error consultando: {str(e)}")


async def continuous_search_worker(search_id: str, chat_id: int, ctx: Dict[str, Any]):
    last_notified_dep_ids = set()
    last_notified_ret_ids = set()

    # Cálculo de la fecha/hora de caducidad
    max_h_str = ctx.get("max_departure_hour") or "23:59"
    max_h_time = datetime.strptime(max_h_str, "%H:%M").time()

    dep_expiration = datetime.combine(ctx["departure_date"].date(), max_h_time)

    if ctx.get("return_date"):
        ret_expiration = datetime.combine(ctx["return_date"].date(), max_h_time)
        expiration_datetime = max(dep_expiration, ret_expiration)
    else:
        expiration_datetime = dep_expiration

    dep_filter = TrainRideFilter(
        origin=ctx["origin"].name, destination=ctx["destination"].name,
        departure_date=ctx["departure_date"], min_departure_hour=None,
        max_departure_hour=ctx.get("max_departure_hour"), max_duration_minutes=ctx.get("max_duration_minutes"),
        max_price=ctx.get("max_price")
    )

    ret_filter = None
    if ctx.get("return_date"):
        ret_filter = TrainRideFilter(
            origin=ctx["destination"].name, destination=ctx["origin"].name,
            departure_date=ctx["return_date"], min_departure_hour=None,
            max_departure_hour=ctx.get("max_departure_hour"), max_duration_minutes=ctx.get("max_duration_minutes"),
            max_price=ctx.get("max_price")
        )

    try:
        while search_id in active_searches:
            # 1. Comprobamos si la búsqueda ha caducado
            if datetime.now() > expiration_datetime:
                await bot.send_message(
                    chat_id,
                    f"🛑 La búsqueda `{search_id}` ({ctx['origin'].name} ➡️ {ctx['destination'].name}) ha caducado porque su fecha y hora máxima han pasado. Se ha detenido automáticamente."
                )
                break  # Sale del bucle y pasa al bloque finally donde se borra

            # 2. Consultamos la web protegida con Try/Except
            try:
                scraper = Scraper(ctx["origin"], ctx["destination"], ctx["departure_date"], ctx.get("return_date"))
                trains = scraper.get_trainrides()

                # Ida
                try:
                    dep_trains = dep_filter.filter_rides(trains)
                except InvalidTrainRideFilter:
                    dep_trains = []

                curr_dep_ids = {f"{t.departure_time}-{t.price}" for t in dep_trains}

                if dep_trains and curr_dep_ids != last_notified_dep_ids:
                    last_notified_dep_ids = curr_dep_ids
                    await bot.send_message(chat_id, f"🔔 *Novedades Ida `{search_id}`!*\n" + get_tickets_message(dep_trains, ctx["origin"], ctx["destination"]), parse_mode="Markdown")

                # Vuelta
                if ret_filter:
                    try:
                        ret_trains = ret_filter.filter_rides(trains)
                    except InvalidTrainRideFilter:
                        ret_trains = []

                    curr_ret_ids = {f"{t.departure_time}-{t.price}" for t in ret_trains}

                    if ret_trains and curr_ret_ids != last_notified_ret_ids:
                        last_notified_ret_ids = curr_ret_ids
                        await bot.send_message(chat_id, f"🔔 *Novedades Vuelta `{search_id}`!*\n" + get_tickets_message(ret_trains, ctx["destination"], ctx["origin"]), parse_mode="Markdown")

            except Exception as e:
                # Fallos de red o de la web de Renfe se silencian para que reintente en 30s
                print(f"[Worker {search_id}] Error temporal: {e}")

            await asyncio.sleep(30)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        await bot.send_message(chat_id, f"⚠️ Error crítico en `{search_id}`: {str(e)}")
    finally:
        if search_id in active_searches:
            del active_searches[search_id]


# --- TAREA HEARTBEAT PARA DOCKER ---
async def heartbeat_worker():
    """Escribe periódicamente un archivo para el healthcheck de Docker."""
    while True:
        try:
            with open("/tmp/bot_heartbeat", "w") as f:
                f.write(str(time.time()))
        except Exception:
            pass
        await asyncio.sleep(30)

async def main():
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    bot.setup_middleware(StateMiddleware(bot))

    asyncio.create_task(heartbeat_worker())
    await bot.infinity_polling()


if __name__ == "__main__":
    asyncio.run(main())
