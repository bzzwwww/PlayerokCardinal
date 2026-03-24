from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cardinal import Cardinal

from telebot.types import CallbackQuery, Message, InputFile

from tg_bot import CBT, keyboards as kb
from tg_bot import feature_tools
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from locales.localizer import Localizer
from Utils import updater

import logging
import os


logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_feature_center_cp(crd: Cardinal, *args):
    tg = crd.telegram
    bot = tg.bot
    time_re = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

    def is_allowed(call: CallbackQuery) -> bool:
        if call.from_user.id not in tg.authorized_users:
            tg.ignore_unauthorized_users(call)
            return False
        return True

    def edit_feature_section(call: CallbackQuery, section: str):
        sections = {
            "map": (feature_tools.render_lot_map_text(), kb.lot_map_settings()),
            "stats": (feature_tools.render_sales_stats_text(), kb.sales_stats_settings()),
            "safe": (feature_tools.render_safe_mode_text(crd), kb.safe_mode_settings(crd)),
            "sched": (feature_tools.render_scheduler_text(), kb.scheduler_settings()),
            "bkp": (feature_tools.render_backups_text(), kb.backups_settings()),
            "nc": (feature_tools.render_notification_center_text(crd, call.message.chat.id),
                   kb.notification_center_settings(call.message.chat.id)),
        }
        text, markup = sections[section]
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
        except Exception as e:
            if "message is not modified" not in str(e):
                raise

    def repeat_delivery(call: CallbackQuery):
        if not is_allowed(call):
            return
        deal_id = call.data.split(":")[1]
        saved = feature_tools.get_saved_delivery(deal_id)
        if not saved:
            bot.answer_callback_query(call.id, _("feature_repeat_delivery_missing"), show_alert=True)
            return

        success = crd.send_message(saved["chat_id"], saved["text"], saved["username"])
        if success:
            bot.answer_callback_query(call.id, _("feature_repeat_delivery_ok"))
            bot.send_message(call.message.chat.id, _("feature_repeat_delivery_ok_msg", deal_id, saved["item_name"]))
        else:
            bot.answer_callback_query(call.id, _("feature_repeat_delivery_err"), show_alert=True)

    def send_test_notification(call: CallbackQuery):
        if not is_allowed(call):
            return
        current_time = time.strftime("%H:%M:%S")
        bot.send_message(call.message.chat.id, _("feature_test_notification_body", current_time))
        bot.answer_callback_query(call.id, _("feature_test_notification_sent"))

    def open_announcements(call: CallbackQuery):
        if not is_allowed(call):
            return
        bot.edit_message_text(_("desc_an"), call.message.chat.id, call.message.id,
                              reply_markup=kb.announcements_settings(crd, call.message.chat.id))
        bot.answer_callback_query(call.id)

    def toggle_safe_mode(call: CallbackQuery):
        if not is_allowed(call):
            return
        feature_tools.set_safe_mode(crd, not feature_tools.safe_mode_enabled(crd))
        edit_feature_section(call, "safe")
        text = _("feature_safe_mode_on") if feature_tools.safe_mode_enabled(crd) else _("feature_safe_mode_off")
        bot.answer_callback_query(call.id, text)

    def act_set_backup_schedule(call: CallbackQuery):
        if not is_allowed(call):
            return
        result = bot.send_message(call.message.chat.id, _("feature_scheduler_enter_time"),
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(call.message.chat.id, result.id, call.from_user.id, CBT.SCHEDULER_SET_TIME)
        bot.answer_callback_query(call.id)

    def set_backup_schedule(msg: Message):
        tg.clear_state(msg.chat.id, msg.from_user.id, True)
        value = msg.text.strip()
        if not time_re.fullmatch(value):
            bot.reply_to(msg, _("feature_scheduler_invalid_time"))
            return
        feature_tools.set_backup_schedule(value)
        bot.reply_to(msg, _("feature_scheduler_saved", value))

    def disable_backup_schedule(call: CallbackQuery):
        if not is_allowed(call):
            return
        feature_tools.disable_backup_schedule()
        edit_feature_section(call, "sched")
        bot.answer_callback_query(call.id, _("feature_scheduler_disabled"))

    def send_backup_file(chat_id: int) -> bool:
        if not os.path.exists("backup.zip"):
            bot.send_message(chat_id, _("update_backup_not_found"))
            return False
        with open("backup.zip", "rb") as file:
            formatted_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(os.path.getmtime("backup.zip")))
            bot.send_document(chat_id=chat_id, document=InputFile(file), visible_file_name="backup.zip",
                              caption=f'{_("update_backup")}\n\n{formatted_time}')
        return True

    def create_backup(call: CallbackQuery):
        if not is_allowed(call):
            return
        if updater.create_backup():
            bot.answer_callback_query(call.id, _("update_backup_error"), show_alert=True)
            return
        send_backup_file(call.message.chat.id)
        edit_feature_section(call, "bkp")
        bot.answer_callback_query(call.id)

    def get_backup(call: CallbackQuery):
        if not is_allowed(call):
            return
        send_backup_file(call.message.chat.id)
        bot.answer_callback_query(call.id)

    def upload_backup(call: CallbackQuery):
        if not is_allowed(call):
            return
        result = bot.send_message(call.message.chat.id, _("send_backup"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(call.message.chat.id, result.id, call.from_user.id, CBT.UPLOAD_BACKUP)
        bot.answer_callback_query(call.id)

    def reset_feature_stats(call: CallbackQuery):
        if not is_allowed(call):
            return
        feature_tools.reset_stats()
        edit_feature_section(call, "stats")
        bot.answer_callback_query(call.id, _("feature_stats_reset"))

    def clear_lot_map(call: CallbackQuery):
        if not is_allowed(call):
            return
        feature_tools.clear_lot_map()
        edit_feature_section(call, "map")
        bot.answer_callback_query(call.id, _("feature_lot_map_cleared"))

    tg.cbq_handler(repeat_delivery, lambda c: c.data.startswith(f"{CBT.REPEAT_DELIVERY}:"))
    tg.cbq_handler(send_test_notification, lambda c: c.data == CBT.FEATURE_TEST_NOTIFICATION)
    tg.cbq_handler(open_announcements, lambda c: c.data == CBT.OPEN_ANNOUNCEMENTS)
    tg.cbq_handler(toggle_safe_mode, lambda c: c.data == CBT.TOGGLE_SAFE_MODE)
    tg.cbq_handler(act_set_backup_schedule, lambda c: c.data == CBT.SET_BACKUP_SCHEDULE)
    tg.msg_handler(set_backup_schedule,
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.SCHEDULER_SET_TIME))
    tg.cbq_handler(disable_backup_schedule, lambda c: c.data == CBT.DISABLE_BACKUP_SCHEDULE)
    tg.cbq_handler(create_backup, lambda c: c.data == CBT.FEATURE_CREATE_BACKUP)
    tg.cbq_handler(get_backup, lambda c: c.data == CBT.FEATURE_GET_BACKUP)
    tg.cbq_handler(upload_backup, lambda c: c.data == CBT.FEATURE_UPLOAD_BACKUP)
    tg.cbq_handler(reset_feature_stats, lambda c: c.data == CBT.RESET_FEATURE_STATS)
    tg.cbq_handler(clear_lot_map, lambda c: c.data == CBT.CLEAR_LOT_MAP)


BIND_TO_PRE_INIT = [init_feature_center_cp]
