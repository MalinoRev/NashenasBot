from typing import Tuple, Dict


_cache: Dict[int, Tuple[float, float]] = {}


def set_temp_location(user_db_id: int, lat: float, lon: float) -> None:
	_cache[user_db_id] = (lat, lon)


def get_temp_location(user_db_id: int) -> Tuple[float, float] | None:
	return _cache.get(user_db_id)


