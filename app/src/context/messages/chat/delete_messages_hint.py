def format_message(chat_id: int) -> str:
	return (
		"جهت حذف تمامی پیام ها از چت شما و پیام های ارسال شده توسط شما از چت مخاطب /delete_messages_"
		f"{chat_id} را بزنید.\n\n"
		"/help_deleteMessage (راهنما)"
	)


