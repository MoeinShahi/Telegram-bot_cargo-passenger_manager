import logging
import sqlite3
import pytz
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the current UTC time
    # Specify the Hungary time zone (Central European Time)
    # Convert UTC time to Hungary time
current_utc_time = datetime.utcnow()
hungary_timezone = pytz.timezone("Europe/Budapest")
hungary_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(hungary_timezone)

# Establish a connection to the SQLite database (or create one if it doesn't exist)
connection = sqlite3.connect('bot.db')

        # Create a cursor object to execute SQL commands
cursor = connection.cursor()


create_chat_table_query = """
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT
);
"""
cursor.execute(create_chat_table_query)

create_table_query = """
CREATE TABLE IF NOT EXISTS cargo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weight REAL,
    depart TEXT,
    dest TEXT,
    price REAL,
    username TEXT,
    issued TEXT
);
"""

cursor.execute(create_table_query)

cargo_dict = {}
# Callback data
BUTTONS = range(1)
START,MENU , ADDCARGO, VIEWCARGO, ADDPASSENGER, VIEWPASSENGER, KG0_5, KG1, KG3, KG5, BUDAPEST, TEHRAN, MASHHAD, SHIRAZ, BUDA, TEH, MASH, SHIR, EURO30, EURO40 = range(20)


Start_keybord = [
    [
        InlineKeyboardButton("با قوانین موافق ام", callback_data=str(START)),
    ],
    
]

start_reply_markup = InlineKeyboardMarkup(Start_keybord)
Menu_keyboard = [
    [
        InlineKeyboardButton("اضافه کردن بسته", callback_data=str(ADDCARGO)),
        InlineKeyboardButton("می خواهم بسته ای را ببرم", callback_data=str(VIEWCARGO)),
    ],
    [
        InlineKeyboardButton("می روم سفر", callback_data=str(ADDPASSENGER)),
        InlineKeyboardButton("مشاهده مسافران", callback_data=str(VIEWPASSENGER)),
    ],
]

menu_reply_markup = InlineKeyboardMarkup(Menu_keyboard)

Weight_selection = [
    [
        InlineKeyboardButton("> 0.5 KG", callback_data=str(KG0_5)),
        InlineKeyboardButton("> 1 KG", callback_data=str(KG1)),
        InlineKeyboardButton("> 3 KG", callback_data=str(KG3)),
        InlineKeyboardButton("> 5 KG", callback_data=str(KG5)),
    ],
]

weight_reply_markup = InlineKeyboardMarkup(Weight_selection)

depart_selection = [
    [
        InlineKeyboardButton("بوداپست", callback_data=str(BUDAPEST)),
        InlineKeyboardButton("تهران", callback_data=str(TEHRAN)),
        InlineKeyboardButton("مشهد", callback_data=str(MASHHAD)),
        InlineKeyboardButton("شیراز", callback_data=str(SHIRAZ)),
    ],
]

depart_reply_markup = InlineKeyboardMarkup(depart_selection)


dest_selection = [
    [
        InlineKeyboardButton("بوداپست", callback_data=str(BUDA)),
        InlineKeyboardButton("تهران", callback_data=str(TEH)),
        InlineKeyboardButton("مشهد", callback_data=str(MASH)),
        InlineKeyboardButton("شیراز", callback_data=str(SHIR)),
    ],
]

dest_reply_markup = InlineKeyboardMarkup(dest_selection)


cargo_price_selection = [
    [
        InlineKeyboardButton("40 €", callback_data=str(EURO40)),
        InlineKeyboardButton("30 €", callback_data=str(EURO30)),
    ],
]

cargo_price_reply_markup = InlineKeyboardMarkup(cargo_price_selection)

confirm_selection = [
    [
        InlineKeyboardButton("تایید", callback_data='YES'),
        InlineKeyboardButton("عدم موافقیت",callback_data='NO'),
    ],
]

confrim_reply_markup = InlineKeyboardMarkup(confirm_selection)

async def menu(update:Update, context:ContextTypes.DEFAULT_TYPE) -> int :
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("لطفا انتخاب کنید", reply_markup=menu_reply_markup)
    return BUTTONS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("""**🎉 به معبن اکسپرس خوش اومدی! 🎉** 

  

**اینجا چکار میشه کرد؟ ❓** 

  

- اگر بسته‌ای داری، می‌خوای به اطلاع بقیه برسونی که برات جابجا کن ✅ 

- اگر داری میری سفر و می‌خوای از سفرت پول در بیاری ✅ 

- و کلی خدمات دیگه ما این امکان رو فراهم کردیم که شما عزیزان با استفاده از این ربات تونید همدیگر رو ✅ 

    سریع‌تر و راحت‌تر پیدا کنید   

  

**قوانین استفاده از پلتفرم 🔴** 

  

- این پلتفرم تنها به عنوان یک فضا برای اشتراک گذاری اطلاعات حمل و نقل و تبادل اطلاعات مسافر و مالک بار عمل می‌کند. ما هیچ نقشی در توافقات شما با دیگر کاربران نداریم و هیچ مسئولیتی در قبال تبادل و انتقال مالی یا هر گونه اتفاقات ناخوشایندی به عهده ما نیست.  

- انتخاب مسافر یا مالک بار به عهده خود کاربران است. شما باید خودتان تصمیم بگیرید و تحقیقات لازم را انجام دهید تا از هویت و اعتبار فرد مقابل اطمینان حاصل کنید.  

- در هنگام تبادل هر نوع اطلاعات حساس، اطلاعات مالی یا مشخصات شخصی، لطفاً از راه‌های ارتباطی امنی استفاده کنید و از اشتراک این اطلاعات در پیام‌های عمومی خودداری کنید.  

- در صورت وقوع هر گونه تخلف یا مشکلی با دیگر کاربران، لطفاً به ما گزارش دهید. ما تا حد امکان سعی خواهیم کرد تا اختلافات را حل کرده و هر گونه تخلفی را بررسی کنیم.  

- شما می‌پذیرید که اطلاعاتی که در این پلتفرم به اشتراک می‌گذارید، به مشتریان و کاربران دیگر قابل دسترسی است. لذا با دقت اطلاعات خود را به اشتراک بگذارید.  

- ما حق داریم هر زمان و بدون اطلاع قبلی قوانین و شرایط را تغییر دهیم. لطفاً به صورت دوره‌ای این صفحه را مرور کنید تا با تغییرات آشنا شوید.  

**این قوانین و شرایط به منظور ایجاد اطمینان و شفافیت در پلتفرم ما ایجاد شده‌اند. با استفاده از پلتفرم ما، شما به این قوانین پایبند می‌شوید.** """)

    if update.message.from_user.username == None:
        await update.message.reply_text("/start در تلگرام ثبت کنید @username شما نام کاربری در تلگرام ندارید لطفا برای استفاده ازین پلتفرم یک نام کاربری")
    else:
        insert_query = """
        INSERT INTO chat (username,date)
        VALUES (?, ?);
        """
        time = hungary_time
        values = (update.message.from_user.username,time)
        cursor.execute(insert_query, values)
        connection.commit()
        await update.message.reply_text("موافقی ؟",reply_markup=start_reply_markup)
        return BUTTONS
        

async def addcargo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("اضافه کردن بسته")
    await query.message.reply_text(":وزن بسته خود را مشخص کنید", reply_markup=weight_reply_markup)
    return BUTTONS


async def weight(update: Update, context) -> int:
    query = update.callback_query
    await query.answer()
    weight = None

    if query.data == str(KG0_5):
        weight = 0.5
        await query.message.edit_text("وزن بسته 0.5")
    elif query.data == str(KG1):
        weight = 1
        await query.message.edit_text("وزن بسته 1")
    elif query.data == str(KG3):
        weight = 3
        await query.message.edit_text("وزن بسته 3")
    elif query.data == str(KG5):
        weight = 5
        await query.message.edit_text("وزن بسته 5")

    cargo_dict["weight"] = weight
    await query.message.reply_text(":شهر مبدا را انتخاب کنید", reply_markup=depart_reply_markup)
    return BUTTONS


async def depart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    depart = None
    if query.data == str(BUDAPEST):
        depart = "Budapest"
        await query.message.edit_text("بوداپست")
    elif query.data == str(TEHRAN):
        depart = "Tehran"
        await query.message.edit_text("تهران")
    elif query.data == str(MASHHAD):
        depart = "Mashhad"
        await query.message.edit_text("مشهد")
    elif query.data == str(SHIRAZ):
        depart = "Shiraz"
        await query.message.edit_text("شیراز")

    cargo_dict["depart"] = depart

    await query.message.reply_text(":مقصد خود را وارد کنید", reply_markup=dest_reply_markup)
    return BUTTONS

async def dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dest = None

    if query.data == str(BUDA):
        dest = "Budapest"
        await query.message.edit_text("بوداپست")
    elif query.data == str(TEH):
        dest = "Tehran"
        await query.message.edit_text("تهران")
    elif query.data == str(MASH):
        dest = "Mashhad"
        await query.message.edit_text("مشهد")
    elif query.data == str(SHIR):
        dest = "Shiraz"
        await query.message.edit_text("شیراز")

    cargo_dict["dest"] = dest
    await query.message.reply_text(":هزینه قابل پرداخت جهت ارسال", reply_markup=cargo_price_reply_markup)
    return BUTTONS

async def cargoPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == str(EURO40):
        price = 40
    elif query.data == str(EURO30):
        price = 30

    cargo_dict["price"] = price
    cargo_dict["username"] = query.from_user.username
    cargo_dict["issued"] = hungary_time
    await query.message.edit_text(f'{price}')

    await query.message.reply_text(f""" ایا با اطلاعات زیر موافق هستید ؟
Username : {cargo_dict['username']}
Depart :{cargo_dict['depart']}
Destination:{cargo_dict['dest']}
Price: €{cargo_dict['price']}
Weight:{cargo_dict['weight']}
Issue:{cargo_dict['issued']}""",reply_markup=confrim_reply_markup)
    return BUTTONS

async def confrimCargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'YES':
        insert_query = """
        INSERT INTO cargo (weight, depart, dest, price, username, issued)
        VALUES (?, ?, ?, ?, ?, ?);
        """

        values = (
        cargo_dict["weight"],
        cargo_dict["depart"],
        cargo_dict["dest"],
        cargo_dict["price"],
        cargo_dict["username"],
        cargo_dict["issued"]
        )

        try:
            cursor.execute(insert_query, values)
            connection.commit()
            await query.message.edit_text("تایید")
            
        except sqlite3.Error as e:
            await query.message.edit_text(f"Error inserting data: {e}")


    elif query.data == 'NO':
        await update.message.edit_text("لطفا انتخاب کنید", reply_markup=menu_reply_markup)
        return BUTTONS




def main() -> None:
    application = Application.builder().token("Your bot token").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BUTTONS: [
                CallbackQueryHandler(addcargo, pattern="^" + str(ADDCARGO) + "$"),
                CallbackQueryHandler(menu, pattern="^" + str(START) + "$"),
                CallbackQueryHandler(weight, pattern="^" + str(KG0_5) + "$"),
                CallbackQueryHandler(weight, pattern="^" + str(KG1) + "$"),
                CallbackQueryHandler(weight, pattern="^" + str(KG3) + "$"),
                CallbackQueryHandler(weight, pattern="^" + str(KG5) + "$"),
                CallbackQueryHandler(depart, pattern="^" + str(BUDAPEST) + "$"),
                CallbackQueryHandler(depart, pattern="^" + str(TEHRAN) + "$"),
                CallbackQueryHandler(depart, pattern="^" + str(MASHHAD) + "$"),
                CallbackQueryHandler(depart, pattern="^" + str(SHIRAZ) + "$"),
                CallbackQueryHandler(dest, pattern="^" + str(BUDA) + "$"),
                CallbackQueryHandler(dest, pattern="^" + str(TEH) + "$"),
                CallbackQueryHandler(dest, pattern="^" + str(MASH) + "$"),
                CallbackQueryHandler(dest, pattern="^" + str(SHIR) + "$"),
                CallbackQueryHandler(cargoPrice, pattern="^" + str(EURO40) + "$"),
                CallbackQueryHandler(cargoPrice, pattern="^" + str(EURO30) + "$"),
                CallbackQueryHandler(confrimCargo, pattern="^" + 'YES' + "$"),
                CallbackQueryHandler(menu, pattern="^" + 'NO' + "$"),
            ],  
        },
        fallbacks=[CommandHandler("menu", menu)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()