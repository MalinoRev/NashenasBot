def get_message(profile_reward_amount: int) -> str:
    """
    Message sent after first-time profile completion to inform user about rewards.
    Only shown once after initial profile completion.
    """
    return (
        f"✅ عضویت شما تایید شد! شما هم اکنون می توانید از امکانات ویژه ربات استفاده کنید!\n\n"
        f"💥 با تکمیل کردن اطلاعات پروفایلت {profile_reward_amount} تا سکه رایگان بگیر 😍"
    )
