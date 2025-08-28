def get_message() -> str:
    """
    Message sent to user when they have a new chat request
    """
    print("LOG: get_message (notification) called")
    result = "🔔 شما یک درخواست چت جدید دریافت کرده‌اید!"
    print(f"LOG: get_message result: '{result}'")
    return result
