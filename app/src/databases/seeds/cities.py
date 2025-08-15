from typing import List

from sqlalchemy import insert, select

from src.core.database import engine
from src.databases.cities import City
from src.databases.states import State


CITY_NAMES_STATE_1: List[str] = [
	"آذرشهر",
	"تیمورلو",
	"گوگان",
	"ممقان",
	"اسکو",
	"ایلخچی",
	"سهند",
	"اهر",
	"هوراند",
	"بستان آباد",
	"تیکمه داش",
	"بناب",
	"باسمنج",
	"تبریز",
	"خسروشاه",
	"سردرود",
	"جلفا",
	"سیه رود",
	"هادیشهر",
	"قره آغاج",
	"خمارلو",
	"دوزدوزان",
	"سراب",
	"شربیان",
	"مهربان",
	"تسوج",
	"خامنه",
	"سیس",
	"شبستر",
	"شرفخانه",
	"شندآباد",
	"صوفیان",
	"کوزه کنان",
	"وایقان",
	"جوان قلعه",
	"عجب شیر",
	"آبش احمد",
	"کلیبر",
	"خداجو(خراجو)",
	"مراغه",
	"بناب مرند",
	"زنوز",
	"کشکسرای",
	"مرند",
	"یامچی",
	"لیلان",
	"مبارک شهر",
	"ملکان",
	"آقکند",
	"اچاچی",
	"ترک",
	"ترکمانچای",
	"میانه",
	"خاروانا",
	"ورزقان",
	"بخشایش",
	"خواجه",
	"زرنق",
	"کلوانق",
	"هریس",
	"نظرکهریزی",
	"هشترود",
]


async def seed_cities_state_1() -> None:
	# Ensure state id 1 exists; otherwise skip to avoid FK errors
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 1))
		if not exists:
			return
		values = [
			{"id": idx + 1, "state_id": 1, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_1)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_2: List[str] = [
	"ارومیه",
	"سرو",
	"سیلوانه",
	"قوشچی",
	"نوشین",
	"اشنویه",
	"نالوس",
	"بوکان",
	"سیمینه",
	"پلدشت",
	"نازک علیا",
	"پیرانشهر",
	"گردکشانه",
	"تکاب",
	"آواجیق",
	"سیه چشمه",
	"قره ضیاءالدین",
	"ایواوغلی",
	"خوی",
	"دیزج دیز",
	"زرآباد",
	"فیرورق",
	"قطور",
	"ربط",
	"سردشت",
	"میرآباد",
	"تازه شهر",
	"سلماس",
	"شاهین دژ",
	"کشاورز",
	"محمودآباد",
	"شوط",
	"مرگنلر",
	"بازرگان",
	"ماکو",
	"خلیفان",
	"مهاباد",
	"باروق",
	"چهاربرج",
	"میاندوآب",
	"محمدیار",
	"نقده",
]


async def seed_cities_state_2(start_id: int = 94) -> None:
	# Ensure state id 2 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 2))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 2, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_2)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_3: List[str] = [
	"اردبیل",
	"هیر",
	"بیله سوار",
	"جعفرآباد",
	"اسلام اباد",
	"اصلاندوز",
	"پارس آباد",
	"تازه کند",
	"خلخال",
	"کلور",
	"هشتجین",
	"سرعین",
	"گیوی",
	"تازه کندانگوت",
	"گرمی",
	"رضی",
	"فخراباد",
	"قصابه",
	"لاهرود",
	"مرادلو",
	"مشگین شهر",
	"آبی بیگلو",
	"عنبران",
	"نمین",
	"کوراییم",
	"نیر",
]


async def seed_cities_state_3(start_id: int = 136) -> None:
	# Ensure state id 3 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 3))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 3, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_3)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_4: List[str] = [
	"آران وبیدگل",
	"ابوزیدآباد",
	"سفیدشهر",
	"نوش آباد",
	"اردستان",
	"زواره",
	"مهاباد",
	"اژیه",
	"اصفهان",
	"بهارستان",
	"تودشک",
	"حسن اباد",
	"زیار",
	"سجزی",
	"قهجاورستان",
	"کوهپایه",
	"محمدآباد",
	"نصرآباد",
	"نیک آباد",
	"ورزنه",
	"هرند",
	"حبیب آباد",
	"خورزوق",
	"دستگرد",
	"دولت آباد",
	"سین",
	"شاپورآباد",
	"کمشچه",
	"افوس",
	"بویین ومیاندشت",
	"تیران",
	"رضوانشهر",
	"عسگران",
	"چادگان",
	"رزوه",
	"اصغرآباد",
	"خمینی شهر",
	"درچه",
	"کوشک",
	"خوانسار",
	"جندق",
	"خور",
	"فرخی",
	"دهاقان",
	"گلشن",
	"حنا",
	"سمیرم",
	"کمه",
	"ونک",
	"شاهین شهر",
	"گرگاب",
	"گزبرخوار",
	"لای بید",
	"میمه",
	"وزوان",
	"شهرضا",
	"منظریه",
	"داران",
	"دامنه",
	"برف انبار",
	"فریدونشهر",
	"ابریشم",
	"ایمانشهر",
	"بهاران شهر",
	"پیربکران",
	"زازران",
	"فلاورجان",
	"قهدریجان",
	"کلیشادوسودرجان",
	"برزک",
	"جوشقان قالی",
	"قمصر",
	"کاشان",
	"کامو و چوگان",
	"مشکات",
	"نیاسر",
	"گلپایگان",
	"گلشهر",
	"گوگد",
	"باغ بهادران",
	"باغشاد",
	"چرمهین",
	"چمگردان",
	"زاینده رود",
	"زرین شهر",
	"سده لنجان",
	"فولادشهر",
	"ورنامخواست",
	"دیزیچه",
	"زیباشهر",
	"طالخونچه",
	"کرکوند",
	"مبارکه",
	"مجلسی",
	"انارک",
	"بافران",
	"نایین",
	"جوزدان",
	"دهق",
	"علویجه",
	"کهریزسنگ",
	"گلدشت",
	"نجف آباد",
	"بادرود",
	"خالدآباد",
	"طرق رود",
	"نطنز",
]


async def seed_cities_state_4(start_id: int = 162) -> None:
	# Ensure state id 4 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 4))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 4, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_4)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_5: List[str] = [
	"اشتهارد",
	"چهارباغ",
	"شهرجدیدهشتگرد",
	"کوهسار",
	"گلسار",
	"هشتگرد",
	"طالقان",
	"فردیس",
	"مشکین دشت",
	"آسارا",
	"کرج",
	"کمال شهر",
	"گرمدره",
	"ماهدشت",
	"محمدشهر",
	"تنکمان",
	"نظرآباد",
]


async def seed_cities_state_5(start_id: int = 269) -> None:
	# Ensure state id 5 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 5))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 5, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_5)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_6: List[str] = [
	"آبدانان",
	"سراب باغ",
	"مورموری",
	"ایلام",
	"چوار",
	"ایوان",
	"زرنه",
	"بدره",
	"آسمان آباد",
	"بلاوه",
	"توحید",
	"سرابله",
	"شباب",
	"دره شهر",
	"ماژین",
	"پهله",
	"دهلران",
	"موسیان",
	"میمه",
	"لومار",
	"ارکواز",
	"دلگشا",
	"مهر",
	"صالح آباد",
	"مهران",
]


async def seed_cities_state_6(start_id: int = 286) -> None:
	# Ensure state id 6 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 6))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 6, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_6)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_7: List[str] = [
	"بوشهر",
	"چغادک",
	"خارک",
	"عالی شهر",
	"آباد",
	"اهرم",
	"دلوار",
	"انارستان",
	"جم",
	"ریز",
	"آب پخش",
	"برازجان",
	"بوشکان",
	"تنگ ارم",
	"دالکی",
	"سعد آباد",
	"شبانکاره",
	"کلمه",
	"وحدتیه",
	"بادوله",
	"خورموج",
	"شنبه",
	"کاکی",
	"آبدان",
	"بردخون",
	"بردستان",
	"بندردیر",
	"دوراهک",
	"امام حسن",
	"بندردیلم",
	"عسلویه",
	"نخل تقی",
	"بندرکنگان",
	"بنک",
	"سیراف",
	"بندرریگ",
	"بندرگناوه",
]


async def seed_cities_state_7(start_id: int = 311) -> None:
	# Ensure state id 7 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 7))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 7, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_7)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_8: List[str] = [
	"احمد آباد مستوفی",
	"اسلامشهر",
	"چهاردانگه",
	"صالحیه",
	"گلستان",
	"نسیم شهر",
	"پاکدشت",
	"شریف آباد",
	"فرون اباد",
	"بومهن",
	"پردیس",
	"پیشوا",
	"تهران",
	"آبسرد",
	"آبعلی",
	"دماوند",
	"رودهن",
	"کیلان",
	"پرند",
	"رباطکریم",
	"نصیرشهر",
	"باقرشهر",
	"حسن آباد",
	"ری",
	"کهریزک",
	"تجریش",
	"شمشک",
	"فشم",
	"لواسان",
	"اندیشه",
	"باغستان",
	"شاهدشهر",
	"شهریار",
	"صباشهر",
	"فردوسیه",
	"وحیدیه",
	"ارجمند",
	"فیروزکوه",
	"قدس",
	"قرچک",
	"صفادشت",
	"ملارد",
	"جوادآباد",
	"ورامین",
]


async def seed_cities_state_8(start_id: int = 348) -> None:
	# Ensure state id 8 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 8))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 8, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_8)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_9: List[str] = [
	"اردل",
	"دشتک",
	"سرخون",
	"کاج",
	"بروجن",
	"بلداجی",
	"سفیددشت",
	"فرادبنه",
	"گندمان",
	"نقنه",
	"بن",
	"وردنجان",
	"سامان",
	"سودجان",
	"سورشجان",
	"شهرکرد",
	"طاقانک",
	"فرخ شهر",
	"کیان",
	"نافچ",
	"هارونی",
	"هفشجان",
	"باباحیدر",
	"پردنجان",
	"جونقان",
	"چلیچه",
	"فارسان",
	"گوجان",
	"بازفت",
	"چلگرد",
	"صمصامی",
	"دستنا",
	"شلمزار",
	"گهرو",
	"ناغان",
	"آلونی",
	"سردشت",
	"لردگان",
	"مال خلیفه",
	"منج",
]


async def seed_cities_state_9(start_id: int = 392) -> None:
	# Ensure state id 9 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 9))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 9, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_9)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_10: List[str] = [
	"ارسک",
	"بشرویه",
	"بیرجند",
	"خوسف",
	"محمدشهر",
	"اسدیه",
	"طبس مسینا",
	"قهستان",
	"گزیک",
	"حاجی آباد",
	"زهان",
	"آیسک",
	"سرایان",
	"سه قلعه",
	"سربیشه",
	"مود",
	"دیهوک",
	"طبس",
	"عشق آباد",
	"اسلامیه",
	"فردوس",
	"آرین شهر",
	"اسفدن",
	"خضری دشت بیاض",
	"قاین",
	"نیمبلوک",
	"شوسف",
	"نهبندان",
]


async def seed_cities_state_10(start_id: int = 432) -> None:
	# Ensure state id 10 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 10))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 10, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_10)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_11: List[str] = [
	"باخرز",
	"بجستان",
	"یونسی",
	"انابد",
	"بردسکن",
	"شهراباد",
	"شاندیز",
	"طرقبه",
	"تایباد",
	"کاریز",
	"مشهدریزه",
	"احمدابادصولت",
	"تربت جام",
	"صالح آباد",
	"نصرآباد",
	"نیل شهر",
	"بایک",
	"تربت حیدریه",
	"رباط سنگ",
	"کدکن",
	"جغتای",
	"نقاب",
	"چناران",
	"گلبهار",
	"گلمکان",
	"خلیل آباد",
	"کندر",
	"خواف",
	"سلامی",
	"سنگان",
	"قاسم آباد",
	"نشتیفان",
	"سلطان آباد",
	"داورزن",
	"چاپشلو",
	"درگز",
	"لطف آباد",
	"نوخندان",
	"جنگل",
	"رشتخوار",
	"دولت آباد",
	"روداب",
	"سبزوار",
	"ششتمد",
	"سرخس",
	"مزدآوند",
	"سفیدسنگ",
	"فرهادگرد",
	"فریمان",
	"قلندرآباد",
	"فیروزه",
	"همت آباد",
	"باجگیران",
	"قوچان",
	"ریوش",
	"کاشمر",
	"شهرزو",
	"کلات",
	"بیدخت",
	"کاخک",
	"گناباد",
	"رضویه",
	"مشهد",
	"مشهد ثامن",
	"ملک آباد",
	"شادمهر",
	"فیض آباد",
	"بار",
	"چکنه",
	"خرو",
	"درود",
	"عشق آباد",
	"قدمگاه",
	"نیشابور",
]


async def seed_cities_state_11(start_id: int = 460) -> None:
	# Ensure state id 11 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 11))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 11, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_11)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_12: List[str] = [
	"اسفراین",
	"صفی آباد",
	"بجنورد",
	"چناران شهر",
	"حصارگرمخان",
	"جاجرم",
	"سنخواست",
	"شوقان",
	"راز",
	"زیارت",
	"شیروان",
	"قوشخانه",
	"لوجلی",
	"تیتکانلو",
	"فاروج",
	"ایور",
	"درق",
	"گرمه",
	"آشخانه",
	"آوا",
	"پیش قلعه",
	"قاضی",
]


async def seed_cities_state_12(start_id: int = 534) -> None:
	# Ensure state id 12 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 12))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 12, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_12)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_13: List[str] = [
	"آبادان",
	"اروندکنار",
	"چویبده",
	"آغاجاری",
	"امیدیه",
	"جایزان",
	"آبژدان",
	"قلعه خواجه",
	"آزادی",
	"اندیمشک",
	"بیدروبه",
	"چم گلک",
	"حسینیه",
	"الهایی",
	"اهواز",
	"ایذه",
	"دهدز",
	"باغ ملک",
	"صیدون",
	"قلعه تل",
	"میداود",
	"شیبان",
	"ملاثانی",
	"ویس",
	"بندرامام خمینی",
	"بندرماهشهر",
	"چمران",
	"بهبهان",
	"تشان",
	"سردشت",
	"منصوریه",
	"حمیدیه",
	"خرمشهر",
	"مقاومت",
	"مینوشهر",
	"چغامیش",
	"حمزه",
	"دزفول",
	"سالند",
	"سیاه منصور",
	"شمس آباد",
	"شهر امام",
	"صفی آباد",
	"میانرود",
	"ابوحمیظه",
	"بستان",
	"سوسنگرد",
	"کوت سیدنعیم",
	"رامشیر",
	"مشراگه",
	"رامهرمز",
	"خنافره",
	"دارخوین",
	"شادگان",
	"الوان",
	"حر",
	"شاوور",
	"شوش",
	"فتح المبین",
	"سرداران",
	"شرافت",
	"شوشتر",
	"گوریه",
	"کوت عبداله",
	"ترکالکی",
	"جنت مکان",
	"سماله",
	"صالح شهر",
	"گتوند",
	"لالی",
	"گلگیر",
	"مسجدسلیمان",
	"هفتگل",
	"زهره",
	"هندیجان",
	"رفیع",
	"هویزه",
]


async def seed_cities_state_13(start_id: int = 556) -> None:
	# Ensure state id 13 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 13))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 13, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_13)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_14: List[str] = [
	"ابهر",
	"صایین قلعه",
	"هیدج",
	"حلب",
	"زرین آباد",
	"زرین رود",
	"سجاس",
	"سهرورد",
	"قیدار",
	"کرسف",
	"گرماب",
	"نوربهار",
	"خرمدره",
	"ارمغانخانه",
	"زنجان",
	"نیک پی",
	"سلطانیه",
	"آب بر",
	"چورزق",
	"دندی",
	"ماه نشان",
]


async def seed_cities_state_14(start_id: int = 633) -> None:
	# Ensure state id 14 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 14))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 14, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_14)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_15: List[str] = [
	"آرادان",
	"کهن آباد",
	"امیریه",
	"دامغان",
	"دیباج",
	"کلاته",
	"سرخه",
	"سمنان",
	"بسطام",
	"بیارجمند",
	"رودیان",
	"شاهرود",
	"کلاته خیج",
	"مجن",
	"ایوانکی",
	"گرمسار",
	"درجزین",
	"شهمیرزاد",
	"مهدی شهر",
	"میامی",
]


async def seed_cities_state_15(start_id: int = 654) -> None:
	# Ensure state id 15 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 15))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 15, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_15)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_16: List[str] = [
	"ایرانشهر",
	"بزمان",
	"بمپور",
	"محمدان",
	"چابهار",
	"نگور",
	"خاش",
	"نوک آباد",
	"گلمورتی",
	"بنجار",
	"زابل",
	"زاهدان",
	"نصرت آباد",
	"زهک",
	"جالق",
	"سراوان",
	"سیرکان",
	"گشت",
	"محمدی",
	"پیشین",
	"راسک",
	"سرباز",
	"سوران",
	"هیدوچ",
	"فنوج",
	"قصرقند",
	"زرآباد",
	"کنارک",
	"مهرستان",
	"میرجاوه",
	"اسپکه",
	"بنت",
	"نیک شهر",
	"ادیمی",
	"شهرک علی اکبر",
	"محمدآباد",
	"دوست محمد",
]


async def seed_cities_state_16(start_id: int = 674) -> None:
	# Ensure state id 16 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 16))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 16, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_16)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_17: List[str] = [
	"آباده",
	"ایزدخواست",
	"بهمن",
	"سورمق",
	"صغاد",
	"ارسنجان",
	"استهبان",
	"ایج",
	"رونیز",
	"اقلید",
	"حسن اباد",
	"دژکرد",
	"سده",
	"بوانات",
	"حسامی",
	"کره ای",
	"مزایجان",
	"سعادت شهر",
	"مادرسلیمان",
	"باب انار",
	"جهرم",
	"خاوران",
	"دوزه",
	"قطب آباد",
	"خرامه",
	"سلطان شهر",
	"صفاشهر",
	"قادراباد",
	"خنج",
	"جنت شهر",
	"داراب",
	"دوبرجی",
	"فدامی",
	"کوپن",
	"مصیری",
	"حاجی آباد",
	"دبیران",
	"شهرپیر",
	"اردکان",
	"بیضا",
	"هماشهر",
	"سروستان",
	"کوهنجان",
	"خانه زنیان",
	"داریان",
	"زرقان",
	"شهرصدرا",
	"شیراز",
	"لپویی",
	"دهرم",
	"فراشبند",
	"نوجین",
	"زاهدشهر",
	"ششده",
	"فسا",
	"قره بلاغ",
	"میانشهر",
	"نوبندگان",
	"فیروزآباد",
	"میمند",
	"افزر",
	"امام شهر",
	"قیر",
	"کارزین (فتح آباد)",
	"مبارک آباددیز",
	"بالاده",
	"خشت",
	"قایمیه",
	"کازرون",
	"کنارتخته",
	"نودان",
	"کوار",
	"گراش",
	"اوز",
	"بنارویه",
	"بیرم",
	"جویم",
	"خور",
	"عمادده",
	"لار",
	"لطیفی",
	"اشکنان",
	"اهل",
	"علامرودشت",
	"لامرد",
	"خانیمن",
	"رامجرد",
	"سیدان",
	"کامفیروز",
	"مرودشت",
	"بابامنیر",
	"خومه زار",
	"نورآباد",
	"اسیر",
	"خوزی",
	"گله دار",
	"مهر",
	"وراوی",
	"آباده طشک",
	"قطرویه",
	"مشکان",
	"نی ریز",
]


async def seed_cities_state_17(start_id: int = 711) -> None:
	# Ensure state id 17 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 17))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 17, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_17)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_18: List[str] = [
	"آبیک",
	"خاکعلی",
	"آبگرم",
	"آوج",
	"الوند",
	"بیدستان",
	"شریفیه",
	"محمدیه",
	"ارداق",
	"بویین زهرا",
	"دانسفهان",
	"سگزآباد",
	"شال",
	"اسفرورین",
	"تاکستان",
	"خرمدشت",
	"ضیاڈآباد",
	"نرجه",
	"اقبالیه",
	"رازمیان",
	"سیردان",
	"قزوین",
	"کوهین",
	"محمودآبادنمونه",
	"معلم کلایه",
]


async def seed_cities_state_18(start_id: int = 813) -> None:
	# Ensure state id 18 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 18))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 18, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_18)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_19: List[str] = [
	"جعفریه",
	"دستجرد",
	"سلفچگان",
	"قم",
	"قنوات",
	"کهک",
]


async def seed_cities_state_19(start_id: int = 838) -> None:
	# Ensure state id 19 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 19))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 19, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_19)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_20: List[str] = [
	"آرمرده",
	"بانه",
	"بویین سفلی",
	"کانی سور",
	"بابارشانی",
	"بیجار",
	"پیرتاج",
	"توپ آغاج",
	"یاسوکند",
	"بلبان آباد",
	"دهگلان",
	"دیواندره",
	"زرینه",
	"اورامان تخت",
	"سروآباد",
	"سقز",
	"صاحب",
	"سنندج",
	"شویشه",
	"دزج",
	"دلبران",
	"سریش آباد",
	"قروه",
	"کامیاران",
	"موچش",
	"برده رشه",
	"چناره",
	"کانی دینار",
	"مریوان",
]


async def seed_cities_state_20(start_id: int = 844) -> None:
	# Ensure state id 20 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 20))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 20, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_20)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_21: List[str] = [
	"ارزوییه",
	"امین شهر",
	"انار",
	"بافت",
	"بزنجان",
	"بردسیر",
	"دشتکار",
	"گلزار",
	"لاله زار",
	"نگار",
	"بروات",
	"بم",
	"بلوک",
	"جبالبارز",
	"جیرفت",
	"درب بهشت",
	"رابر",
	"هنزا",
	"راور",
	"هجدک",
	"بهرمان",
	"رفسنجان",
	"صفاییه",
	"کشکوییه",
	"مس سرچشمه",
	"رودبار",
	"زهکلوت",
	"گنبکی",
	"محمدآباد",
	"خانوک",
	"ریحان",
	"زرند",
	"یزدان شهر",
	"بلورد",
	"پاریز",
	"خواجو شهر",
	"زیدآباد",
	"سیرجان",
	"نجف شهر",
	"هماشهر",
	"جوزم",
	"خاتون اباد",
	"خورسند",
	"دهج",
	"شهربابک",
	"دوساری",
	"عنبرآباد",
	"مردهک",
	"فاریاب",
	"فهرج",
	"قلعه گنج",
	"اختیارآباد",
	"اندوهجرد",
	"باغین",
	"جوپار",
	"چترود",
	"راین",
	"زنگی آباد",
	"شهداد",
	"کاظم آباد",
	"کرمان",
	"گلباف",
	"ماهان",
	"محی آباد",
	"کوهبنان",
	"کیانشهر",
	"کهنوج",
	"منوجان",
	"نودژ",
	"نرماشیر",
	"نظام شهر",
]


async def seed_cities_state_21(start_id: int = 873) -> None:
	# Ensure state id 21 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 21))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 21, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_21)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_22: List[str] = [
	"اسلام آبادغرب",
	"حمیل",
	"بانوره",
	"باینگان",
	"پاوه",
	"نودشه",
	"نوسود",
	"ازگله",
	"تازه آباد",
	"جوانرود",
	"ریجاب",
	"کرند",
	"گهواره",
	"روانسر",
	"شاهو",
	"سرپل ذهاب",
	"سطر",
	"سنقر",
	"صحنه",
	"میان راهان",
	"سومار",
	"قصرشیرین",
	"رباط",
	"کرمانشاه",
	"کوزران",
	"هلشی",
	"کنگاور",
	"گودین",
	"سرمست",
	"گیلانغرب",
	"بیستون",
	"هرسین",
]


async def seed_cities_state_22(start_id: int = 944) -> None:
	# Ensure state id 22 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 22))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 22, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_22)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_23: List[str] = [
	"باشت",
	"چیتاب",
	"گراب سفلی",
	"مادوان",
	"مارگون",
	"یاسوج",
	"لیکک",
	"چرام",
	"سرفاریاب",
	"پاتاوه",
	"سی سخت",
	"دهدشت",
	"دیشموک",
	"سوق",
	"قلعه رییسی",
	"دوگنبدان",
	"لنده",
]


async def seed_cities_state_23(start_id: int = 976) -> None:
	# Ensure state id 23 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 23))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 23, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_23)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_24: List[str] = [
	"آزادشهر",
	"نگین شهر",
	"نوده خاندوز",
	"آق قلا",
	"انبارآلوم",
	"بندرگز",
	"نوکنده",
	"بندرترکمن",
	"تاتارعلیا",
	"خان ببین",
	"دلند",
	"رامیان",
	"سنگدوین",
	"علی اباد",
	"فاضل آباد",
	"مزرعه",
	"کردکوی",
	"فراغی",
	"کلاله",
	"گالیکش",
	"جلین",
	"سرخنکلاته",
	"گرگان",
	"سیمین شهر",
	"گمیش تپه",
	"اینچه برون",
	"گنبدکاووس",
	"مراوه",
	"مینودشت",
]


async def seed_cities_state_24(start_id: int = 993) -> None:
	# Ensure state id 24 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 24))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 24, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_24)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_25: List[str] = [
	"آستارا",
	"لوندویل",
	"آستانه اشرفیه",
	"کیاشهر",
	"املش",
	"رانکوه",
	"بندرانزلی",
	"خشکبیجار",
	"خمام",
	"رشت",
	"سنگر",
	"کوچصفهان",
	"لشت نشاء",
	"لولمان",
	"پره سر",
	"رضوانشهر",
	"بره سر",
	"توتکابن",
	"جیرنده",
	"رستم آباد",
	"رودبار",
	"لوشان",
	"منجیل",
	"چابکسر",
	"رحیم آباد",
	"رودسر",
	"کلاچای",
	"واجارگاه",
	"دیلمان",
	"سیاهکل",
	"احمدسرگوراب",
	"شفت",
	"صومعه سرا",
	"گوراب زرمیخ",
	"مرجقل",
	"اسالم",
	"چوبر",
	"حویق",
	"لیسار",
	"هشتپر (تالش)",
	"فومن",
	"ماسوله",
	"ماکلوان",
	"رودبنه",
	"لاهیجان",
	"اطاقور",
	"چاف و چمخاله",
	"شلمان",
	"کومله",
	"لنگرود",
	"بازار جمعه",
	"ماسال",
]


async def seed_cities_state_25(start_id: int = 1022) -> None:
	# Ensure state id 25 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 25))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 25, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_25)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_26: List[str] = [
	"ازنا",
	"مومن آباد",
	"الیگودرز",
	"شول آباد",
	"اشترینان",
	"بروجرد",
	"پلدختر",
	"معمولان",
	"بیران شهر",
	"خرم آباد",
	"زاغه",
	"سپیددشت",
	"نورآباد",
	"هفت چشمه",
	"چالانچولان",
	"دورود",
	"سراب دوره",
	"ویسیان",
	"چقابل",
	"الشتر",
	"فیروزآباد",
	"درب گنبد",
	"کوهدشت",
	"کوهنانی",
	"گراب",
]


async def seed_cities_state_26(start_id: int = 1074) -> None:
	# Ensure state id 26 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 26))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 26, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_26)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_27: List[str] = [
	"آمل",
	"امامزاده عبدالله",
	"دابودشت",
	"رینه",
	"گزنک",
	"امیرکلا",
	"بابل",
	"خوش رودپی",
	"زرگرمحله",
	"گتاب",
	"گلوگاه",
	"مرزیکلا",
	"بابلسر",
	"بهنمیر",
	"هادی شهر",
	"بهشهر",
	"خلیل شهر",
	"رستمکلا",
	"تنکابن",
	"خرم آباد",
	"شیرود",
	"نشتارود",
	"جویبار",
	"کوهی خیل",
	"چالوس",
	"مرزن آباد",
	"هچیرود",
	"رامسر",
	"کتالم وسادات شهر",
	"پایین هولار",
	"ساری",
	"فریم",
	"کیاسر",
	"آلاشت",
	"پل سفید",
	"زیرآب",
	"شیرگاه",
	"کیاکلا",
	"سلمان شهر",
	"عباس اباد",
	"کلارآباد",
	"فریدونکنار",
	"ارطه",
	"قایم شهر",
	"کلاردشت",
	"گلوگاه",
	"سرخرود",
	"محمودآباد",
	"سورک",
	"نکا",
	"ایزدشهر",
	"بلده",
	"چمستان",
	"رویان",
	"نور",
	"پول",
	"کجور",
	"نوشهر",
]


async def seed_cities_state_27(start_id: int = 1099) -> None:
	# Ensure state id 27 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 27))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 27, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_27)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_28: List[str] = [
	"آشتیان",
	"اراک",
	"داودآباد",
	"ساروق",
	"کارچان",
	"تفرش",
	"خمین",
	"قورچی باشی",
	"جاورسیان",
	"خنداب",
	"دلیجان",
	"نراق",
	"پرندک",
	"خشکرود",
	"رازقان",
	"زاویه",
	"مامونیه",
	"آوه",
	"ساوه",
	"غرق آباد",
	"نوبران",
	"آستانه",
	"توره",
	"شازند",
	"شهباز",
	"مهاجران",
	"هندودر",
	"خنجین",
	"فرمهین",
	"کمیجان",
	"میلاجرد",
	"محلات",
	"نیمور",
]


async def seed_cities_state_28(start_id: int = 1157) -> None:
	# Ensure state id 28 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 28))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 28, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_28)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_29: List[str] = [
	"ابوموسی",
	"بستک",
	"جناح",
	"سردشت",
	"گوهران",
	"بندرعباس",
	"تازیان پایین",
	"تخت",
	"فین",
	"قلعه قاضی",
	"بندرلنگه",
	"چارک",
	"کنگ",
	"کیش",
	"لمزان",
	"پارسیان",
	"دشتی",
	"کوشکنار",
	"بندرجاسک",
	"حاجی اباد",
	"سرگز",
	"فارغان",
	"خمیر",
	"رویدر",
	"بیکاء",
	"دهبارز",
	"زیارتعلی",
	"سیریک",
	"کوهستک",
	"گروک",
	"درگهان",
	"سوزا",
	"قشم",
	"هرمز",
	"تیرور",
	"سندرک",
	"میناب",
	"هشتبندی",
]


async def seed_cities_state_29(start_id: int = 1190) -> None:
	# Ensure state id 29 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 29))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 29, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_29)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_30: List[str] = [
	"آجین",
	"اسدآباد",
	"بهار",
	"صالح آباد",
	"لالجین",
	"مهاجران",
	"تویسرکان",
	"سرکان",
	"فرسفج",
	"دمق",
	"رزن",
	"قروه درجزین",
	"فامنین",
	"شیرین سو",
	"کبودرآهنگ",
	"گل تپه",
	"ازندریان",
	"جوکار",
	"زنگنه",
	"سامن",
	"ملایر",
	"برزول",
	"فیروزان",
	"گیان",
	"نهاوند",
	"جورقان",
	"قهاوند",
	"مریانج",
	"همدان",
]


async def seed_cities_state_30(start_id: int = 1228) -> None:
	# Ensure state id 30 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 30))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 30, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_30)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


CITY_NAMES_STATE_31: List[str] = [
	"ابرکوه",
	"مهردشت",
	"احمدآباد",
	"اردکان",
	"عقدا",
	"اشکذر",
	"خضرآباد",
	"بافق",
	"بهاباد",
	"تفت",
	"نیر",
	"مروست",
	"هرات",
	"مهریز",
	"بفروییه",
	"میبد",
	"ندوشن",
	"حمیدیا",
	"زارچ",
	"شاهدیه",
	"یزد",
]


async def seed_cities_state_31(start_id: int = 1257) -> None:
	# Ensure state id 31 exists; otherwise skip
	async with engine.begin() as conn:
		exists = await conn.scalar(select(State.id).where(State.id == 31))
		if not exists:
			return
		values = [
			{"id": start_id + idx, "state_id": 31, "city_name": name}
			for idx, name in enumerate(CITY_NAMES_STATE_31)
		]
		await conn.execute(insert(City).prefix_with("IGNORE"), values)


