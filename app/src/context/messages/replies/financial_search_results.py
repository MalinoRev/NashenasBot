def get_no_results_message() -> str:
	return "❌ هیچ پرداختی با این مشخصات یافت نشد."


def get_results_header(query: str, count: int) -> str:
	return f"🔍 **نتایج جستجو برای: {query}**\n\n**تعداد یافت شده: {count} مورد**\n\n"


def get_single_result_header(query: str) -> str:
	return f"🔍 **نتیجه جستجو برای: {query}**\n\n"
