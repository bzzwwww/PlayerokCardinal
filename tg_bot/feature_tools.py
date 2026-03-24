from __future__ import annotations

import configparser
import json
import os
import time
from datetime import datetime
from threading import Thread

from Utils import updater
from locales.localizer import Localizer


localizer = Localizer()
_ = localizer.translate


CACHE_DIR = "storage/cache"
LOT_MAP_FILE = os.path.join(CACHE_DIR, "lot_map.json")
STATS_FILE = os.path.join(CACHE_DIR, "feature_stats.json")
DELIVERY_FILE = os.path.join(CACHE_DIR, "delivery_memory.json")
SCHEDULER_FILE = os.path.join(CACHE_DIR, "scheduler.json")


def ensure_cache_dir() -> None:
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def _read_json(path: str, default):
    ensure_cache_dir()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except Exception:
        return default


def _write_json(path: str, data) -> None:
    ensure_cache_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_lot_map() -> dict:
    return _read_json(LOT_MAP_FILE, {"aliases": {}, "history": []})


def save_lot_map(data: dict) -> None:
    _write_json(LOT_MAP_FILE, data)


def remember_lot_mapping(old_id, new_id, item_name: str, mode: str = "free") -> None:
    old_id = str(old_id)
    new_id = str(new_id)
    data = load_lot_map()

    if old_id != new_id:
        data.setdefault("aliases", {})[old_id] = new_id

    history = data.setdefault("history", [])
    history.insert(0, {
        "old_id": old_id,
        "new_id": new_id,
        "item_name": item_name,
        "mode": mode,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    data["history"] = history[:50]
    save_lot_map(data)


def resolve_lot_id(lot_id) -> str:
    current = str(lot_id)
    aliases = load_lot_map().get("aliases", {})
    visited = set()
    while current in aliases and current not in visited:
        visited.add(current)
        current = str(aliases[current])
    return current


def lot_id_matches(config_lot_id, incoming_lot_id) -> bool:
    config_lot_id = str(config_lot_id)
    incoming_lot_id = str(incoming_lot_id)
    return (
        config_lot_id == incoming_lot_id
        or resolve_lot_id(config_lot_id) == incoming_lot_id
        or resolve_lot_id(incoming_lot_id) == config_lot_id
    )


def clear_lot_map() -> None:
    save_lot_map({"aliases": {}, "history": []})


def _default_stats() -> dict:
    return {
        "totals": {
            "new_deal": 0,
            "delivery_success": 0,
            "delivery_error": 0,
            "restore_success": 0,
            "restore_error": 0,
            "new_review": 0,
            "deal_problem": 0,
            "deal_problem_resolved": 0,
            "autoresponse_sent": 0,
            "safe_mode_skip": 0
        },
        "today": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "new_deal": 0,
            "delivery_success": 0,
            "delivery_error": 0,
            "restore_success": 0,
            "restore_error": 0,
            "new_review": 0,
            "deal_problem": 0,
            "deal_problem_resolved": 0,
            "autoresponse_sent": 0,
            "safe_mode_skip": 0
        },
        "recent": []
    }


def load_stats() -> dict:
    data = _read_json(STATS_FILE, _default_stats())
    today = datetime.now().strftime("%Y-%m-%d")
    if data.get("today", {}).get("date") != today:
        data["today"] = _default_stats()["today"]
        data["today"]["date"] = today
        save_stats(data)
    return data


def save_stats(data: dict) -> None:
    _write_json(STATS_FILE, data)


def reset_stats() -> None:
    save_stats(_default_stats())


def record_stat_event(event_type: str, **payload) -> None:
    data = load_stats()
    if event_type not in data["totals"]:
        data["totals"][event_type] = 0
    if event_type not in data["today"]:
        data["today"][event_type] = 0

    data["totals"][event_type] += 1
    data["today"][event_type] += 1
    data["recent"].insert(0, {
        "event": event_type,
        "payload": payload,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    data["recent"] = data["recent"][:25]
    save_stats(data)


def load_delivery_memory() -> dict:
    return _read_json(DELIVERY_FILE, {})


def save_delivery_memory(data: dict) -> None:
    _write_json(DELIVERY_FILE, data)


def remember_delivery(deal_id, chat_id, username: str, text: str, item_name: str) -> None:
    data = load_delivery_memory()
    data[str(deal_id)] = {
        "chat_id": str(chat_id),
        "username": username,
        "text": text,
        "item_name": item_name,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_delivery_memory(data)


def get_saved_delivery(deal_id) -> dict | None:
    return load_delivery_memory().get(str(deal_id))


def _safe_mode_flag(cardinal) -> str:
    section = cardinal.MAIN_CFG.get("Other", {})
    if isinstance(section, dict):
        return section.get("safeMode", "0")
    return section.get("safeMode", "0")


def safe_mode_enabled(cardinal) -> bool:
    return _safe_mode_flag(cardinal) == "1"


def set_safe_mode(cardinal, enabled: bool) -> None:
    if "Other" not in cardinal.MAIN_CFG:
        cardinal.MAIN_CFG["Other"] = {}
    cardinal.MAIN_CFG["Other"]["safeMode"] = "1" if enabled else "0"
    cardinal.save_config(cardinal.MAIN_CFG, "configs/_main.cfg")


def load_scheduler() -> dict:
    return _read_json(SCHEDULER_FILE, {
        "backup": {
            "enabled": False,
            "time": "",
            "last_run": ""
        }
    })


def save_scheduler(data: dict) -> None:
    _write_json(SCHEDULER_FILE, data)


def set_backup_schedule(time_str: str) -> None:
    data = load_scheduler()
    data.setdefault("backup", {})
    data["backup"]["enabled"] = True
    data["backup"]["time"] = time_str
    save_scheduler(data)


def disable_backup_schedule() -> None:
    data = load_scheduler()
    data.setdefault("backup", {})
    data["backup"]["enabled"] = False
    data["backup"]["time"] = ""
    save_scheduler(data)


def _load_auto_delivery_sections() -> list[dict]:
    cfg = configparser.ConfigParser(delimiters=(":",), interpolation=None)
    cfg.optionxform = str
    if os.path.exists("configs/auto_delivery.cfg"):
        cfg.read("configs/auto_delivery.cfg", encoding="utf-8")

    result = []
    for section_name in cfg.sections():
        if section_name.startswith("!"):
            continue
        section = cfg[section_name]
        result.append({
            "name": section_name,
            "goods_file": section.get("productsFileName") or section.get("goods_file"),
            "lot_id": section.get("lot_id", ""),
        })
    return result


def _count_all_products() -> int:
    total = 0
    products_dir = "storage/products"
    if not os.path.exists(products_dir):
        return 0
    for filename in os.listdir(products_dir):
        if not filename.endswith(".txt"):
            continue
        try:
            with open(os.path.join(products_dir, filename), "r", encoding="utf-8") as f:
                total += len([line for line in f.read().splitlines() if line.strip()])
        except Exception:
            continue
    return total


def render_lot_map_text() -> str:
    data = load_lot_map()
    aliases = data.get("aliases", {})
    history = data.get("history", [])
    last_entry = _("fc_empty")
    if history:
        latest = history[0]
        last_entry = _("fc_last_map_entry", latest["item_name"], latest["old_id"], latest["new_id"], latest["updated_at"])
    return _("fc_lot_map_text", len(aliases), len(history), last_entry)


def render_notification_center_text(cardinal, chat_id: int) -> str:
    from tg_bot.utils import NotificationTypes

    notification_types = [
        NotificationTypes.new_message,
        NotificationTypes.command,
        NotificationTypes.new_order,
        NotificationTypes.order_confirmed,
        NotificationTypes.lots_restore,
        NotificationTypes.delivery,
        NotificationTypes.review,
        NotificationTypes.deal_problem,
        NotificationTypes.bot_start,
        NotificationTypes.other,
    ]
    enabled = sum(1 for nt in notification_types if cardinal.telegram.is_notification_enabled(chat_id, nt))
    announcements = cardinal.telegram.is_notification_enabled(chat_id, NotificationTypes.announcement)
    ads = cardinal.telegram.is_notification_enabled(chat_id, NotificationTypes.ad)
    ann_text = _("fc_enabled") if announcements else _("fc_disabled")
    ads_text = _("fc_enabled") if ads else _("fc_disabled")
    return _("fc_notification_center_text", chat_id, enabled, len(notification_types), ann_text, ads_text)


def _render_recent_events_lines(recent: list[dict]) -> str:
    if not recent:
        return _("fc_no_recent_events")
    lines = []
    for entry in recent[:5]:
        event = entry.get("event", "other")
        created_at = entry.get("created_at", "")
        payload = entry.get("payload", {})
        short = payload.get("deal_id") or payload.get("item_id") or payload.get("chat_id") or payload.get("username") or "-"
        lines.append(f"• <code>{created_at}</code> - <b>{event}</b> - <code>{short}</code>")
    return "\n".join(lines)


def render_sales_stats_text() -> str:
    stats = load_stats()
    totals = stats["totals"]
    today = stats["today"]
    recent = _render_recent_events_lines(stats.get("recent", []))
    return _("fc_sales_stats_text",
             totals.get("new_deal", 0),
             today.get("new_deal", 0),
             totals.get("delivery_success", 0),
             totals.get("delivery_error", 0),
             totals.get("restore_success", 0),
             totals.get("new_review", 0),
             totals.get("deal_problem", 0),
             recent)


def render_quick_actions_text() -> str:
    delivery_count = len(load_delivery_memory())
    return _("fc_quick_actions_text", delivery_count)


def render_smart_replies_text(cardinal) -> str:
    commands_count = len(cardinal.RAW_AR_CFG.sections()) if hasattr(cardinal.RAW_AR_CFG, "sections") else 0
    templates_count = len(cardinal.telegram.answer_templates) if cardinal.telegram else 0
    safe_mode = _("fc_enabled") if safe_mode_enabled(cardinal) else _("fc_disabled")
    return _("fc_smart_replies_text", commands_count, templates_count, safe_mode)


def render_mass_lots_text() -> str:
    lots = _load_auto_delivery_sections()
    goods_files = len([name for name in os.listdir("storage/products") if name.endswith(".txt")]) if os.path.exists("storage/products") else 0
    mapped = len([lot for lot in lots if lot.get("goods_file")])
    return _("fc_mass_lots_text", len(lots), goods_files, _count_all_products(), mapped)


def render_safe_mode_text(cardinal) -> str:
    status = _("fc_enabled") if safe_mode_enabled(cardinal) else _("fc_disabled")
    return _("fc_safe_mode_text", status)


def render_scheduler_text() -> str:
    data = load_scheduler()
    backup = data.get("backup", {})
    if backup.get("enabled") and backup.get("time"):
        schedule_text = backup.get("time")
    else:
        schedule_text = _("fc_disabled")
    last_run = backup.get("last_run") or _("fc_empty")
    return _("fc_scheduler_text", schedule_text, last_run)


def render_backups_text() -> str:
    if os.path.exists("backup.zip"):
        modified_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(os.path.getmtime("backup.zip")))
        exists = _("fc_exists")
    else:
        modified_time = _("fc_empty")
        exists = _("fc_missing")
    return _("fc_backups_text", exists, modified_time)


def run_scheduled_backup_if_needed(cardinal) -> None:
    data = load_scheduler()
    backup = data.get("backup", {})
    if not backup.get("enabled") or not backup.get("time"):
        return

    now = datetime.now()
    current_hm = now.strftime("%H:%M")
    if current_hm != backup.get("time"):
        return

    last_run = backup.get("last_run", "")
    today_key = now.strftime("%Y-%m-%d")
    if last_run.startswith(today_key):
        return

    result = updater.create_backup()
    backup["last_run"] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_scheduler(data)

    if cardinal.telegram:
        from tg_bot.utils import NotificationTypes

        if result == 0:
            text = _("fc_scheduler_backup_ok", backup.get("time"))
        else:
            text = _("fc_scheduler_backup_error", backup.get("time"))
        Thread(
            target=cardinal.telegram.send_notification,
            args=(text, None, NotificationTypes.other),
            daemon=True
        ).start()


def scheduler_loop(cardinal) -> None:
    while True:
        try:
            if getattr(cardinal, "running", False):
                run_scheduled_backup_if_needed(cardinal)
        except Exception:
            pass
        time.sleep(20)
