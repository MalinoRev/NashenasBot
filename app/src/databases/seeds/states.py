from sqlalchemy import insert

from src.core.database import engine
from src.databases.states import State


async def seed_states() -> None:
	data = [
		{"id": 1, "state_name": "آذربایجان شرقی"},
		{"id": 2, "state_name": "آذربایجان غربی"},
		{"id": 3, "state_name": "اردبیل"},
		{"id": 4, "state_name": "اصفهان"},
		{"id": 5, "state_name": "البرز"},
		{"id": 6, "state_name": "ایلام"},
		{"id": 7, "state_name": "بوشهر"},
		{"id": 8, "state_name": "تهران"},
		{"id": 9, "state_name": "چهارمحال و بختیاری"},
		{"id": 10, "state_name": "خراسان جنوبی"},
		{"id": 11, "state_name": "خراسان رضوی"},
		{"id": 12, "state_name": "خراسان شمالی"},
		{"id": 13, "state_name": "خوزستان"},
		{"id": 14, "state_name": "زنجان"},
		{"id": 15, "state_name": "سمنان"},
		{"id": 16, "state_name": "سیستان و بلوچستان"},
		{"id": 17, "state_name": "فارس"},
		{"id": 18, "state_name": "قزوین"},
		{"id": 19, "state_name": "قم"},
		{"id": 20, "state_name": "کردستان"},
		{"id": 21, "state_name": "کرمان"},
		{"id": 22, "state_name": "کرمانشاه"},
		{"id": 23, "state_name": "کهگیلویه و بویراحمد"},
		{"id": 24, "state_name": "گلستان"},
		{"id": 25, "state_name": "گیلان"},
		{"id": 26, "state_name": "لرستان"},
		{"id": 27, "state_name": "مازندران"},
		{"id": 28, "state_name": "مرکزی"},
		{"id": 29, "state_name": "هرمزگان"},
		{"id": 30, "state_name": "همدان"},
		{"id": 31, "state_name": "یزد"},
	]
	async with engine.begin() as conn:
		await conn.execute(insert(State).prefix_with("IGNORE"), data)


