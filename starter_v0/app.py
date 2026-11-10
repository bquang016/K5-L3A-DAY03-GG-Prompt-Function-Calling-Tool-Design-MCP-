from __future__ import annotations

import html
import json
import threading
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

load_lab_env(ROOT)

LOGO_PATH = ROOT / "assets" / "bot_logo.svg"

st.set_page_config(
    page_title="Research Agent Studio",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else ":material/smart_toy:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- VECTOR SVG ICONS (No cheap emojis) ----------------
BOT_HEADER_SVG = """
<svg width="30" height="30" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgG" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0F172A"/>
      <stop offset="55%" stop-color="#1E3A8A"/>
      <stop offset="100%" stop-color="#2563EB"/>
    </linearGradient>
    <linearGradient id="visG" x1="16" y1="26" x2="48" y2="38" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#818CF8"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="56" height="56" rx="10" fill="url(#bgG)" stroke="#3B82F6" stroke-width="2"/>
  <path d="M32 11V17" stroke="#60A5FA" stroke-width="3" stroke-linecap="square"/>
  <rect x="29" y="8" width="6" height="4" rx="1" fill="#38BDF8"/>
  <rect x="14" y="17" width="36" height="30" rx="5" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>
  <rect x="9" y="26" width="4" height="12" rx="1" fill="#38BDF8"/>
  <rect x="51" y="26" width="4" height="12" rx="1" fill="#38BDF8"/>
  <rect x="19" y="23" width="26" height="12" rx="3" fill="#0F172A"/>
  <rect x="23" y="26.5" width="6" height="5" rx="1" fill="url(#visG)"/>
  <rect x="35" y="26.5" width="6" height="5" rx="1" fill="url(#visG)"/>
  <rect x="24" y="40" width="4" height="2.5" rx="0.5" fill="#2563EB"/>
  <rect x="30" y="39" width="4" height="4.5" rx="0.5" fill="#2563EB"/>
  <rect x="36" y="40" width="4" height="2.5" rx="0.5" fill="#2563EB"/>
</svg>
"""

SVG_SEARCH = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="square"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
SVG_GLOBE = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="square"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'
SVG_USER = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2" stroke-linecap="square"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
SVG_HASH = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="square"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>'
SVG_HELP = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="square"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
SVG_SHIELD = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="square"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
SVG_DOC = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0F172A" stroke-width="2" stroke-linecap="square"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
SVG_SEND = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#E11D48" stroke-width="2" stroke-linecap="square"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>'

TOOL_META: dict[str, dict[str, str]] = {
    "lookup": {"label": "Tra cứu Web", "svg": SVG_SEARCH, "desc": "Tìm kiếm tin tức & thông tin qua Tavily API"},
    "fetch": {"label": "Đọc trang Web", "svg": SVG_GLOBE, "desc": "Trích xuất nội dung Markdown từ URL qua Firecrawl"},
    "timeline": {"label": "Dòng thời gian X", "svg": SVG_USER, "desc": "Lấy bài đăng gần đây của một tài khoản X/Twitter"},
    "social_search": {"label": "Tìm kiếm Mạng xã hội", "svg": SVG_HASH, "desc": "Tìm kiếm bài thảo luận trên X theo từ khóa (Latest/Top)"},
    "clarify": {"label": "Hỏi lại người dùng", "svg": SVG_HELP, "desc": "Tạm dừng và yêu cầu người dùng bổ sung thông tin thiếu"},
    "format": {"label": "Định dạng Bản tin", "svg": SVG_DOC, "desc": "Trình bày danh sách dữ liệu thành Markdown Digest"},
    "policy": {"label": "Quy định Nội bộ", "svg": SVG_SHIELD, "desc": "Tra cứu tài liệu chính sách nội bộ công ty"},
    "papers": {"label": "Tìm bài báo arXiv", "svg": SVG_DOC, "desc": "Tìm kiếm bài báo khoa học trên hệ thống arXiv"},
    "paper_text": {"label": "Đọc PDF arXiv", "svg": SVG_DOC, "desc": "Tải file PDF arXiv và trích xuất toàn văn"},
    "send": {"label": "Gửi Telegram", "svg": SVG_SEND, "desc": "Đăng bản tin lên kênh Telegram (bắt buộc xác nhận)"},
}

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .block-container {
        padding-top: 0.85rem !important;
        padding-bottom: 0.75rem !important;
        max-width: 98.5% !important;
    }
    header[data-testid="stHeader"] {
        height: 1.5rem !important;
        background: transparent !important;
    }

    /* Crisp 4px radius containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0 !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    /* Buttons: sharp 4px corners, clean hover */
    .stButton > button,
    .stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 4px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 500 !important;
        font-size: 0.83rem !important;
        padding: 0.35rem 0.7rem !important;
        transition: all 0.12s ease;
        box-shadow: none !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #2563EB !important;
        background-color: #F8FAFC !important;
        color: #1D4ED8 !important;
    }
    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #1D4ED8 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }

    /* Inputs & Chat input */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-testid="stChatInput"] > div {
        border-radius: 4px !important;
        border-color: #CBD5E1 !important;
        background-color: #FFFFFF !important;
    }

    [data-testid="stExpander"] {
        border-radius: 4px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #F8FAFC !important;
    }

    /* Top App Bar */
    .studio-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px 20px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #2563EB;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .studio-brand {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .studio-brand > svg {
        flex-shrink: 0;
    }
    .studio-title {
        font-weight: 700;
        font-size: 1.02rem;
        color: #0F172A;
        letter-spacing: -0.01em;
    }
    .studio-sub {
        font-size: 0.76rem;
        color: #64748B;
    }
    .studio-badges {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
    }
    .chip {
        overflow-wrap: anywhere;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 3px 8px;
        border-radius: 3px;
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        color: #334155;
    }
    .chip-blue {
        background: #EFF6FF;
        border-color: #BFDBFE;
        color: #1D4ED8;
        font-weight: 500;
    }
    .chip-green {
        background: #ECFDF5;
        border-color: #A7F3D0;
        color: #047857;
    }

    /* Light Workspace Browser Bar */
    .ws-address-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 6px 12px;
        margin-bottom: 12px;
    }
    .ws-window-controls {
        display: flex;
        gap: 5px;
    }
    .ws-dot {
        width: 8px;
        height: 8px;
        border-radius: 1px;
        background: #CBD5E1;
    }
    .ws-url-box {
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 3px;
        padding: 3px 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        color: #475569;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Result Cards in Workspace */
    .ws-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #2563EB;
        border-radius: 4px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: border-color 0.12s ease;
    }
    .ws-card:hover {
        border-color: #93C5FD;
        border-left-color: #1D4ED8;
    }
    .ws-card-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 4px;
    }
    .ws-card-title {
        font-weight: 600;
        font-size: 0.94rem;
        color: #0F172A;
        line-height: 1.35;
    }
    .ws-card-title a {
        color: #0F172A;
        text-decoration: none;
    }
    .ws-card-title a:hover {
        color: #2563EB;
        text-decoration: underline;
    }
    .ws-card-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.73rem;
        color: #64748B;
        margin-bottom: 8px;
    }
    .ws-card-body {
        font-size: 0.86rem;
        color: #334155;
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* Research chat */
    .sider-heading {
        margin: 0;
        color: #0F172A;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .sider-conversation-title {
        color: #334155;
        font-weight: 600;
        overflow-wrap: anywhere;
    }
    .sider-welcome {
        border: 1px solid #DBEAFE;
        border-radius: 14px;
        background: linear-gradient(135deg, #EFF6FF, #FFFFFF);
        padding: 20px 16px;
    }
    .sider-welcome h2 {
        margin: 0 0 6px;
        padding: 0;
        color: #0F172A;
        font-size: 1.1rem;
        line-height: 1.4;
    }
    .sider-welcome p {
        margin: 0;
        color: #475569;
        font-size: 0.9rem;
    }
    .st-key-sider_navigation [role="radiogroup"] {
        flex-wrap: wrap;
        gap: 0.25rem 0.6rem;
    }
    .st-key-sider_new_chat button {
        min-height: 2.5rem;
        border-radius: 10px !important;
    }
    [data-testid="stChatInput"] > div {
        border-radius: 12px !important;
    }
    .sider-user-msg {
        background: #EFF6FF;
        border: 1px solid #DBEAFE;
        border-radius: 14px 14px 4px 14px;
        padding: 10px 14px;
        font-size: 0.9rem;
        color: #172554;
        line-height: 1.5;
        margin-left: auto;
        width: fit-content;
        max-width: 90%;
    }
    .sider-thought-step {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 3px 0;
        font-size: 0.78rem;
        color: #475569;
        font-family: 'JetBrains Mono', monospace;
    }
    .sider-user-msg,
    .sider-clarify-msg {
        white-space: pre-wrap;
    }
    .sider-user-msg,
    .sider-clarify-msg,
    .sider-thought-step {
        overflow-wrap: anywhere;
    }
    .sider-thought-step > svg {
        flex-shrink: 0;
    }
    .sider-clarify-msg {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 3px solid #D97706;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 0.87rem;
        color: #92400E;
        margin-bottom: 8px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------
def init_session_state() -> None:
    defaults: dict[str, Any] = {
        "history": [],
        "ui_turns": [],
        "turn_index": 0,
        "transcript_path": None,
        "transcript": None,
        "pending_input": None,
        "workspace_events": [],
        "active_turn_num": None,
        "sider_tab": ":material/chat: Trò chuyện",
        "sider_save_error": None,
        "cfg_provider": "openrouter",
        "cfg_model": "",
        "cfg_version": "v3",
        "cfg_history": 5,
        "cfg_rounds": 4,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_conversation() -> None:
    st.session_state.history = []
    st.session_state.ui_turns = []
    st.session_state.turn_index = 0
    st.session_state.transcript_path = None
    st.session_state.transcript = None
    st.session_state.pending_input = None
    st.session_state.workspace_events = []
    st.session_state.active_turn_num = None
    st.session_state.sider_save_error = None
    st.session_state.sider_tab = ":material/chat: Trò chuyện"


@st.cache_resource
def transcript_lock() -> threading.RLock:
    return threading.RLock()


def conversation_title(turns: list[dict[str, Any]]) -> str:
    title = " ".join(turns[0]["user"].split())
    return (title[:67].rstrip() + "…") if len(title) > 68 else title or "Hội thoại"


def saved_conversations() -> dict[Path, tuple[datetime, list[dict[str, Any]]]]:
    entries = {}
    for path in (ROOT / "transcripts").glob("*.transcript.json"):
        try:
            if path.is_symlink():
                continue
            modified = datetime.fromtimestamp(path.stat().st_mtime)
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        turns = data.get("turns") if isinstance(data, dict) else None
        if isinstance(turns, list) and turns and all(
            isinstance(turn, dict)
            and isinstance(turn.get("user"), str)
            and isinstance(turn.get("turn_index"), int)
            and (turn.get("assistant_text") is None or isinstance(turn["assistant_text"], str))
            for turn in turns
        ):
            entries[path] = (modified, turns)
    return dict(sorted(entries.items(), key=lambda entry: (entry[1][0], entry[0].name), reverse=True))


def open_conversation(path: Path) -> None:
    with transcript_lock():
        if path.is_symlink():
            raise ValueError("Không thể mở hội thoại này.")
        transcript = json.loads(path.read_text(encoding="utf-8"))
    turns = transcript["turns"]
    reset_conversation()
    st.session_state.transcript_path = path
    st.session_state.transcript = transcript
    st.session_state.ui_turns = list(turns)
    st.session_state.turn_index = max(turn["turn_index"] for turn in turns)
    st.session_state.history = [
        message
        for turn in turns if turn.get("status") != "provider_error"
        for message in (
            {"role": "user", "content": turn["user"]},
            {"role": "assistant", "content": turn.get("assistant_text") or ""},
        )
    ]


def ensure_transcript(
    *,
    version: str,
    provider_name: str,
    selected_model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[Path, dict[str, Any]]:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    if st.session_state.transcript is None or st.session_state.transcript_path is None:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
        transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
        transcript: dict[str, Any] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": selected_model,
            "system_prompt": str(system_prompt_path),
            "tools": str(tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": list(st.session_state.ui_turns),
        }
        st.session_state.transcript_path = transcript_path
        st.session_state.transcript = transcript
    else:
        st.session_state.transcript.update(artifact_version_dict(artifact_version))
        st.session_state.transcript["provider"] = provider_name
        st.session_state.transcript["model"] = selected_model
        st.session_state.transcript["history_window"] = history_window
        st.session_state.transcript["max_tool_rounds"] = max_tool_rounds
    return st.session_state.transcript_path, st.session_state.transcript


def extract_clarify_options(tool_events: list[dict[str, Any]]) -> list[str]:
    if not tool_events:
        return []
    last_result = tool_events[-1].get("result", {})
    if not isinstance(last_result, dict) or not last_result.get("awaiting_user"):
        return []
    resp_type = last_result.get("response_type", "text")
    options = [str(opt) for opt in (last_result.get("options") or []) if str(opt).strip()]
    if resp_type == "yes_no" and not options:
        return ["Đồng ý, hãy thực hiện", "Hủy bỏ"]
    return options


def needs_telegram_confirmation(tool_events: list[dict[str, Any]]) -> str | None:
    for ev in reversed(tool_events):
        res = ev.get("result", {})
        if isinstance(res, dict) and res.get("status") == "needs_confirmation":
            return str((ev.get("args") or {}).get("text") or "")
    return None


def format_thought_step_html(ev: dict[str, Any]) -> str:
    t_name = ev.get("tool", "")
    args = ev.get("args", {}) or {}
    meta = TOOL_META.get(t_name, {"label": t_name, "svg": SVG_DOC})
    svg_icon = meta["svg"]

    if t_name == "lookup":
        detail = f'Tìm kiếm: "{args.get("query", "")}" [{args.get("topic", "general")} • {args.get("timeframe", "week")}]'
    elif t_name == "fetch":
        detail = f'Đọc trang: {args.get("url", "")}'
    elif t_name == "timeline":
        detail = f'Dòng thời gian X: @{ str(args.get("screenname", "")).lstrip("@") } (limit={args.get("limit", 5)})'
    elif t_name == "social_search":
        detail = f'Tìm trên X: "{args.get("query", "")}" ({args.get("search_type", "Latest")})'
    elif t_name == "clarify":
        detail = f'Hỏi lại: "{args.get("question", "")}"'
    elif t_name == "policy":
        detail = f'Tra cứu Policy: "{args.get("query", "")}" ({args.get("policy_area", "all")})'
    elif t_name == "papers":
        detail = f'Tìm arXiv: "{args.get("query", "")}"'
    elif t_name == "paper_text":
        detail = f'Đọc PDF arXiv: {args.get("arxiv_url", "")}'
    elif t_name == "format":
        detail = f'Định dạng Digest: template={args.get("template", "sections")}'
    elif t_name == "send":
        detail = f'Telegram: confirmed={args.get("confirmed", False)}'
    else:
        detail = f"{t_name}: {json.dumps(args, ensure_ascii=False)}"

    return f'<div class="sider-thought-step">{svg_icon}<span>{html.escape(detail)}</span></div>'


def execute_agent_turn(
    *,
    user_text: str,
    provider_name: str,
    model_override: str | None,
    version_label: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    st.session_state.turn_index += 1
    current_turn_index = st.session_state.turn_index

    turn_record: dict[str, Any] = {
        "turn_index": current_turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(tool_declarations)
        provider = make_provider(provider_name)
        selected_model = model_override or getattr(provider, "default_model", None)

        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, history_window),
            {"role": "user", "content": user_text},
        ]

        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model_override,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]

        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})

        if result.get("tool_events"):
            st.session_state.workspace_events = result["tool_events"]
            st.session_state.active_turn_num = current_turn_index

    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {str(exc)}",
        })
        selected_model = model_override

    turn_record["ended_at"] = now_iso()
    with transcript_lock():
        current_path = st.session_state.transcript_path
        if current_path is not None:
            try:
                if current_path.is_symlink():
                    raise OSError("Đường dẫn hội thoại không hợp lệ.")
                current = json.loads(current_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                current = None
            if current != st.session_state.transcript:
                st.session_state.sider_save_error = (
                    "Hội thoại đã được thay đổi hoặc xóa ở nơi khác. "
                    "Lượt vừa gửi chưa được lưu. Hãy sao chép nội dung cần giữ và mở lại hội thoại."
                )
                st.session_state.ui_turns.append(turn_record)
                return
        t_path, transcript_obj = ensure_transcript(
            version=version_label,
            provider_name=provider_name,
            selected_model=selected_model,
            system_prompt_path=system_prompt_path,
            tools_path=tools_path,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        transcript_obj["turns"].append(turn_record)
        write_transcript(t_path, transcript_obj)
        st.session_state.ui_turns.append(turn_record)


init_session_state()

system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
artifact_ver = build_artifact_version(st.session_state.cfg_version, system_prompt_path, tools_path)
is_sidepanel_only = st.query_params.get("mode") == "sider"

if is_sidepanel_only:
    st.markdown(
        """
        <style>
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
                background: #FFFFFF !important;
            }
            .block-container {
                max-width: 100% !important;
                padding: 0.9rem 4.75rem 1rem 1rem !important;
            }
            .st-key-sider_navigation {
                position: fixed;
                z-index: 100;
                top: 0;
                right: 0;
                bottom: 0;
                width: 4rem;
                padding: 1rem 0.3rem;
                background: #F7F7FA;
                border-left: 1px solid #F0F0F4;
            }
            .st-key-sider_navigation [data-testid="stVerticalBlock"] {
                gap: 0.65rem;
                align-items: center;
            }
            .st-key-sider_navigation .stButton button {
                width: 2.8rem !important;
                height: 2.8rem !important;
                min-height: 0;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 12px !important;
                background: transparent !important;
                color: #767994 !important;
                box-shadow: none !important;
            }
            .st-key-sider_navigation .stButton button[kind="primary"] {
                color: #6D3AFF !important;
                background: #FFFFFF !important;
            }
            .st-key-sider_navigation .stButton button:hover {
                color: #6D3AFF !important;
                background: #FFFFFF !important;
            }
            .st-key-sider_navigation .stButton button:focus-visible {
                outline: 2px solid #805CFF;
                outline-offset: 2px;
            }
            .st-key-sider_navigation .stButton button span[role="img"] {
                font-size: 1.45rem !important;
            }
            .st-key-sider_new_chat button[kind="primary"] {
                width: auto !important;
                min-height: 2.3rem;
                padding: 0.4rem 0.85rem !important;
                border-radius: 999px !important;
                border-color: #E8E8EF !important;
                color: #5531D9 !important;
                background: #F7F6FC !important;
            }
            .sider-welcome {
                min-height: min(47vh, 340px);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                border: 0;
                background: #FFFFFF;
                padding: 24px 10px;
            }
            .sider-welcome::before {
                content: "";
                display: block;
                width: 60px;
                height: 60px;
                margin-bottom: 24px;
                border-radius: 42% 58% 52% 48%;
                background: radial-gradient(circle at 28% 20%, #FFE78F 0 12%, transparent 34%),
                    radial-gradient(circle at 78% 27%, #FF589B 0 12%, transparent 42%),
                    linear-gradient(145deg, #44D2F7 10%, #8041FF 72%, #5820EE);
                box-shadow: 0 6px 18px #7546ff33;
            }
            .sider-welcome h2 {
                color: #101018;
                font-size: 1.25rem;
                font-weight: 700;
            }
            .sider-welcome p {
                color: #7C7D94;
                max-width: 32rem;
                line-height: 1.6;
            }
            [data-testid="stBottom"] {
                padding-right: 4rem;
                background: #FFFFFF;
            }
            [data-testid="stBottom"] {
                padding-bottom: 0.8rem;
            }
            div[data-testid="stChatInput"] > div {
                position: relative;
                min-height: 112px;
                border: 1px solid #DCDDE7 !important;
                border-radius: 20px !important;
                background: #FFFFFF !important;
                box-shadow: 0 0 0 4px #F6F6F9, 0 3px 12px #2520430D !important;
            }
            div[data-testid="stChatInput"] > div:focus-within {
                border-color: #A78BFA !important;
                box-shadow: 0 0 0 4px #F1ECFF !important;
            }
            [data-testid="stChatInputTextArea"] {
                min-height: 76px !important;
                padding: 6px 38px 12px 4px !important;
                color: #232236;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            [data-testid="stChatInputTextArea"]::placeholder {
                color: #A7A8B9;
            }
            [data-testid="stChatInputSubmitButton"] {
                position: absolute;
                right: 12px;
                bottom: 12px;
                width: 36px;
                height: 36px;
                border: 0 !important;
                border-radius: 50%;
                background: transparent !important;
                color: #7040FF !important;
            }
            [data-testid="stChatInputSubmitButton"] svg {
                display: none;
            }
            [data-testid="stChatInputSubmitButton"]::after {
                content: "";
                display: block;
                width: 22px;
                height: 22px;
                background: currentColor;
                mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M5 5.5 19 12 5 18.5 8 12z' fill='none' stroke='%23000' stroke-width='4' stroke-linejoin='round' stroke-linecap='round'/%3E%3C/svg%3E") center / contain no-repeat;
            }
            [data-testid="stChatInputSubmitButton"]:disabled {
                color: #BDB4D8 !important;
            }
            [data-testid="stChatInputSubmitButton"]:focus-visible {
                outline: 2px solid #805CFF;
                outline-offset: 2px;
            }
            .stButton > button, .stDownloadButton > button {
                border-radius: 14px !important;
                border-color: #D6E9FA !important;
                background: #F1F8FF !important;
                color: #245987 !important;
            }
            .stButton > button:hover, .stDownloadButton > button:hover {
                background: #E2F2FF !important;
                border-color: #B9DDF9 !important;
            }
            .st-key-sider_history_list [data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                align-items: center;
                gap: 0.4rem !important;
            }
            .st-key-sider_history_list [data-testid="stColumn"]:first-child {
                flex: 1 1 0 !important;
                width: auto !important;
                min-width: 0 !important;
            }
            .st-key-sider_history_list [data-testid="stColumn"]:last-child {
                flex: 0 0 2.8rem !important;
                width: 2.8rem !important;
                min-width: 0 !important;
            }
            .st-key-sider_history_list [data-testid="stPopoverButton"] {
                width: 2.8rem;
                min-height: 2.8rem;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 12px !important;
                background: #F1F8FF !important;
                color: #527493 !important;
            }
            .st-key-sider_history_list [data-testid="stPopoverButton"] [aria-hidden="true"] {
                display: none;
            }
            .st-key-sider_history_list .stButton button {
                justify-content: flex-start;
                text-align: left;
                min-height: 2.8rem;
                padding: 0.6rem 0.8rem !important;
                border: 1px solid #E3F0FB !important;
                border-radius: 12px !important;
                background: #F5FAFF !important;
                color: #294A68 !important;
            }
            .st-key-sider_history_list .stButton button:hover {
                background: #F4F2FA !important;
                color: #5F36DD !important;
            }
            .st-key-sider_history_list .stButton button p {
                text-align: left;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .stApp {
                font-family: Inter, "Segoe UI", sans-serif;
            }
            .sider-user-msg {
                background: #F3F0FF;
                border-color: #E7E0FF;
                color: #312060;
            }
            @media (max-width: 300px) {
                .st-key-sider_navigation { width: 3.5rem; }
                .block-container { padding-right: 4rem !important; }
                [data-testid="stBottom"] { padding-right: 3.5rem; }
            }
            [data-testid="stMarkdownContainer"] {
                overflow-wrap: anywhere;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        """
        <style>
            .stApp {
                background: #F5F8FC;
                color: #1D2939;
                font-family: Inter, "Segoe UI", sans-serif;
            }
            .block-container {
                max-width: 1500px !important;
                padding: 1.25rem 1.5rem 2rem !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border: 1px solid #E2EBF4 !important;
                border-radius: 18px !important;
                background: #FFFFFF;
                box-shadow: 0 4px 18px rgba(38, 70, 106, 0.04);
            }
            .studio-topbar {
                border: 1px solid #E2EBF4;
                border-left: 3px solid #8ABFEA;
                border-radius: 16px;
                padding: 15px 20px;
            }
            .studio-badges { row-gap: 8px; }
            .chip { border-radius: 8px; }
            .ws-address-bar {
                background: #F7FAFE;
                border-radius: 10px;
            }
            .ws-url-box { border-radius: 8px; }
            .ws-card { border-radius: 12px; }
            [data-testid="stExpander"] {
                border-radius: 12px !important;
                background: #FAFCFF !important;
            }
            [data-baseweb="select"] > div,
            [data-baseweb="input"] > div,
            [data-baseweb="textarea"] > div {
                border-radius: 12px !important;
                border-color: #D7E6F3 !important;
            }
            .stButton button, .stButton > button[kind="primary"],
            .stDownloadButton button, [data-testid="stFormSubmitButton"] button,
            div[data-testid="stFormSubmitButton"] > button[kind="primary"],
            [data-testid="stPopoverButton"] {
                min-height: 2.7rem;
                border: 1px solid #D6E9FA !important;
                border-radius: 14px !important;
                background: #F1F8FF !important;
                color: #245987 !important;
                box-shadow: none !important;
                transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
            }
            .stButton button:hover, .stButton > button[kind="primary"]:hover,
            .stDownloadButton button:hover, [data-testid="stFormSubmitButton"] button:hover,
            [data-testid="stPopoverButton"]:hover {
                background: #E2F2FF !important;
                border-color: #B9DDF9 !important;
                color: #164C78 !important;
            }
            .stButton button:focus-visible, .stDownloadButton button:focus-visible,
            [data-testid="stPopoverButton"]:focus-visible {
                outline: 2px solid #80B6E5;
                outline-offset: 2px;
            }
            .st-key-sider_navigation button[kind="primary"] {
                background: #E8E2FF !important;
                border-color: #DAD0FF !important;
                color: #6539E8 !important;
            }
            .st-key-sider_navigation button span[role="img"] {
                font-size: 1.2rem !important;
            }
            .st-key-sider_new_chat button {
                border-radius: 999px !important;
            }
            .sider-welcome {
                border: 1px solid #E5F0FA;
                border-radius: 16px;
                background: #F8FBFF;
                padding: 24px 20px;
            }
            .sider-welcome h2 { line-height: 1.4; }
            .sider-welcome p { line-height: 1.6; }
            .sider-user-msg {
                background: #F1F8FF;
                border-color: #D8EAF8;
                color: #234967;
            }
            div[data-testid="stChatInput"] > div {
                position: relative;
                min-height: 104px;
                border: 1px solid #DCDDE7 !important;
                border-radius: 20px !important;
                background: #FFFFFF !important;
                box-shadow: 0 0 0 4px #F6F6F9 !important;
            }
            div[data-testid="stChatInput"] > div:focus-within {
                border-color: #A78BFA !important;
                box-shadow: 0 0 0 4px #F1ECFF !important;
            }
            [data-testid="stChatInputTextArea"] {
                min-height: 68px !important;
                padding: 6px 38px 12px 4px !important;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            [data-testid="stChatInputTextArea"]::placeholder { color: #A7A8B9; }
            [data-testid="stChatInputSubmitButton"] {
                position: absolute;
                right: 12px;
                bottom: 12px;
                width: 36px;
                height: 36px;
                border: 0 !important;
                border-radius: 50%;
                background: transparent !important;
                color: #7040FF !important;
            }
            [data-testid="stChatInputSubmitButton"] svg { display: none; }
            [data-testid="stChatInputSubmitButton"]::after {
                content: "";
                display: block;
                width: 22px;
                height: 22px;
                background: currentColor;
                mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M5 5.5 19 12 5 18.5 8 12z' fill='none' stroke='%23000' stroke-width='4' stroke-linejoin='round' stroke-linecap='round'/%3E%3C/svg%3E") center / contain no-repeat;
            }
            [data-testid="stChatInputSubmitButton"]:disabled { color: #BDB4D8 !important; }
            [data-testid="stChatInputSubmitButton"]:focus-visible {
                outline: 2px solid #805CFF;
                outline-offset: 2px;
            }
            .st-key-sider_history_list [data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                align-items: center;
                gap: 0.4rem !important;
            }
            .st-key-sider_history_list [data-testid="stColumn"]:first-child {
                flex: 1 1 0 !important;
                width: auto !important;
                min-width: 0 !important;
            }
            .st-key-sider_history_list [data-testid="stColumn"]:last-child {
                flex: 0 0 2.8rem !important;
                width: 2.8rem !important;
                min-width: 0 !important;
            }
            .st-key-sider_history_list [data-testid="stPopoverButton"] {
                width: 2.8rem;
                min-height: 2.8rem;
                padding: 0 !important;
            }
            .st-key-sider_history_list [data-testid="stPopoverButton"] [aria-hidden="true"] {
                display: none;
            }
            .st-key-sider_history_list .stButton button {
                justify-content: flex-start;
                text-align: left;
                min-height: 2.8rem;
                padding: 0.6rem 0.8rem !important;
            }
            .st-key-sider_history_list .stButton button p {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------- TOP STATUS BAR (Desktop Mode) ----------------
if not is_sidepanel_only:
    tx_status = st.session_state.transcript_path.name if st.session_state.transcript_path else "Chưa ghi (0 lượt)"
    st.html(
        f"""
        <div class="studio-topbar">
            <div class="studio-brand">
                {BOT_HEADER_SVG}
                <div>
                    <div class="studio-title">Research Agent Studio</div>
                    <div class="studio-sub">Không gian Nghiên cứu Đa công cụ & Đánh giá Thực nghiệm (Day 03 Lab v2)</div>
                </div>
            </div>
            <div class="studio-badges">
                <span class="chip chip-blue">VERSION: {html.escape(artifact_ver.version)}</span>
                <span class="chip">HASH: {html.escape(artifact_ver.artifact_version)}</span>
                <span class="chip">PROVIDER: {html.escape(st.session_state.cfg_provider.upper())}</span>
                <span class="chip chip-green">NGỮ CẢNH: {len(st.session_state.history)//2} LƯỢT</span>
                <span class="chip">LOG: {html.escape(tx_status)}</span>
            </div>
        </div>
        """,
    )

# ---------------- MAIN 2-PANE LAYOUT ----------------
if is_sidepanel_only:
    col_workspace = None
    col_sider = nullcontext()
else:
    col_workspace, col_sider = st.columns([6.0, 4.0], gap="small")


# =====================================================================
# PANE TRÁI: KHÔNG GIAN NỘI DUNG & KIỂM THỬ (WORKSPACE)
# =====================================================================
if col_workspace is not None:
    with col_workspace:
        with st.container(border=True, height=760):
            # Light clean address bar
            active_url_display = "research://studio/bang-dieu-khien"
            if st.session_state.workspace_events:
                last_ev = st.session_state.workspace_events[-1]
                active_url_display = (
                    f"tool://{last_ev.get('tool')} "
                    f"— {json.dumps(last_ev.get('args', {}), ensure_ascii=False)}"
                )

            st.markdown(
                f"""
                <div class="ws-address-bar">
                    <div class="ws-window-controls">
                        <span class="ws-dot"></span>
                        <span class="ws-dot"></span>
                        <span class="ws-dot"></span>
                    </div>
                    {SVG_GLOBE}
                    <div class="ws-url-box">{html.escape(active_url_display)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            ws_tab_data, ws_tab_playground, ws_tab_logs, ws_tab_specs = st.tabs([
                ":material/article: Nội dung & Kết quả",
                ":material/science: Chạy thử 10 Công cụ",
                ":material/receipt_long: Nhật ký Transcript & Eval",
                ":material/code: Prompt, Tools & Báo cáo A",
            ])

            # --- TAB 1: HIỂN THỊ DỮ LIỆU TRÍCH XUẤT ---
            with ws_tab_data:
                if not st.session_state.workspace_events:
                    st.markdown("##### Bảng Điều Khiển Kịch Bản Demo (Nhấn để gửi sang Trợ lý AI bên phải)")
                    st.caption(
                        "Thiết kế theo đúng nhiệm vụ bàn giao: Kịch bản 1 gọi công cụ ngay, "
                        "Kịch bản 2 kiểm tra khả năng hỏi lại (`clarify`) và nối ngữ cảnh ở lượt kế tiếp."
                    )
                    g1, g2 = st.columns(2)
                    with g1:
                        with st.container(border=True):
                            st.markdown("**Kịch bản 1 — Tra cứu trực tiếp (1 lượt)**")
                            st.caption("Câu hỏi đủ thông tin -> Agent tự động gọi `lookup(topic='news', timeframe='week')`.")
                            if st.button(
                                ":material/play_arrow: Chạy: Tin tức AI nổi bật tuần này",
                                key="ws_sc1",
                                use_container_width=True,
                                type="primary",
                            ):
                                st.session_state.pending_input = "Tin tức AI nổi bật trong tuần này là gì?"
                                st.session_state.sider_tab = ":material/chat: Trò chuyện"
                                st.rerun()

                        with st.container(border=True):
                            st.markdown("**Kịch bản 3 — Tra cứu Quy định nội bộ (`policy`)**")
                            st.caption("Kiểm tra khả năng định tuyến vào kho tài liệu `company_policy/`.")
                            if st.button(
                                ":material/policy: Chạy: Quy định trích dẫn nguồn",
                                key="ws_sc3",
                                use_container_width=True,
                            ):
                                st.session_state.pending_input = "Quy định nội bộ của công ty về trích dẫn nguồn (source citation) là gì?"
                                st.session_state.sider_tab = ":material/chat: Trò chuyện"
                                st.rerun()

                    with g2:
                        with st.container(border=True):
                            st.markdown("**Kịch bản 2 (Lượt 1) — Thiếu tài khoản X**")
                            st.caption("Không nêu tên tài khoản -> Agent bắt buộc gọi `clarify` để hỏi lại.")
                            if st.button(
                                ":material/help: Lượt 1: Xem tweet của tài khoản đó",
                                key="ws_sc2a",
                                use_container_width=True,
                                type="primary",
                            ):
                                st.session_state.pending_input = "Cho tôi xem các bài tweet gần đây của tài khoản đó"
                                st.session_state.sider_tab = ":material/chat: Trò chuyện"
                                st.rerun()

                        with st.container(border=True):
                            st.markdown("**Kịch bản 2 (Lượt 2) — Bổ sung Handle `@sama`**")
                            st.caption("Kiểm tra lưu lịch sử hội thoại -> Nối ngữ cảnh và gọi `timeline(screenname='sama')`.")
                            if st.button(
                                ":material/reply: Lượt 2: Tài khoản Sam Altman (@sama)",
                                key="ws_sc2b",
                                use_container_width=True,
                            ):
                                st.session_state.pending_input = "Tài khoản của Sam Altman (@sama)"
                                st.session_state.sider_tab = ":material/chat: Trò chuyện"
                                st.rerun()
                else:
                    # Hiển thị thanh công cụ nhỏ trên đầu kết quả
                    top_c1, top_c2, top_c3 = st.columns([3, 2, 1.5])
                    with top_c1:
                        turn_badge = f"Lượt #{st.session_state.active_turn_num}" if st.session_state.active_turn_num else "Chạy thủ công"
                        st.markdown(f"**Kết quả thực thi công cụ ({turn_badge})**")
                    with top_c2:
                        view_mode = st.segmented_control(
                            "Chế độ xem",
                            options=["Thẻ chi tiết", "Bản tin Digest", "JSON"],
                            default="Thẻ chi tiết",
                            label_visibility="collapsed",
                        )
                    with top_c3:
                        if st.button(":material/close: Đóng kết quả", use_container_width=True):
                            st.session_state.workspace_events = []
                            st.rerun()

                    for ev_i, ev in enumerate(st.session_state.workspace_events, start=1):
                        t_name = ev.get("tool", "")
                        meta = TOOL_META.get(t_name, {"label": t_name, "svg": SVG_DOC, "desc": ""})
                        res = ev.get("result", {}) or {}

                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:8px;margin:8px 0 4px 0;">'
                            f'{meta["svg"]}<strong>{ev_i}. {html.escape(meta["label"])} (<code>{html.escape(t_name)}</code>)</strong>'
                            f'<span class="chip">{html.escape(json.dumps(ev.get("args", {}), ensure_ascii=False))}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        if view_mode == "JSON":
                            st.json(res, expanded=True)
                            continue

                        if isinstance(res, dict) and res.get("error"):
                            st.error(f"Lỗi công cụ `{t_name}`: {res.get('error')} — {res.get('message', '')}")
                            continue

                        items = res.get("items") if isinstance(res, dict) else None
                        if isinstance(items, list) and items:
                            if view_mode == "Bản tin Digest":
                                digest_out = TOOL_FUNCTIONS["format"](
                                    items=items,
                                    template="sections",
                                    headline=f"Tổng hợp dữ liệu từ {meta['label']}",
                                )
                                st.markdown(digest_out.get("markdown", ""))
                                continue

                            for item in items:
                                title_raw = str(item.get("title") or "Không có tiêu đề")
                                title = html.escape(title_raw)
                                url = str(item.get("url") or "")
                                source = html.escape(str(item.get("source") or "web"))
                                date_str = html.escape(str(item.get("date") or item.get("published") or ""))
                                summary = html.escape(str(item.get("summary") or ""))

                                title_html = f'<a href="{html.escape(url)}" target="_blank">{title} ↗</a>' if url else title
                                meta_chips = [f"<span>Nguồn: {source}</span>"]
                                if date_str:
                                    meta_chips.append(f"<span>Thời gian: {date_str}</span>")
                                metrics = item.get("metrics")
                                if isinstance(metrics, dict):
                                    m_str = " • ".join(f"{k}: {v}" for k, v in metrics.items() if v is not None)
                                    if m_str:
                                        meta_chips.append(f"<span>{html.escape(m_str)}</span>")
                                if item.get("pdf_url"):
                                    meta_chips.append(f'<a href="{html.escape(str(item["pdf_url"]))}" target="_blank">PDF ↗</a>')

                                st.markdown(
                                    f"""
                                    <div class="ws-card">
                                        <div class="ws-card-header">
                                            <div class="ws-card-title">{title_html}</div>
                                        </div>
                                        <div class="ws-card-meta">{" • ".join(meta_chips)}</div>
                                        <div class="ws-card-body">{summary[:1500]}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                        elif isinstance(res, dict) and "results" in res:
                            hits = res.get("results") or []
                            if not hits:
                                st.warning("Không tìm thấy mục quy định nào khớp truy vấn.")
                            for hit in hits:
                                st.markdown(
                                    f"""
                                    <div class="ws-card">
                                        <div class="ws-card-title">{html.escape(str(hit.get('title')))} — {html.escape(str(hit.get('section')))}</div>
                                        <div class="ws-card-meta">
                                            <span>Khu vực: {html.escape(str(hit.get('policy_area')))}</span> •
                                            <span>Hiệu lực: {html.escape(str(hit.get('effective_date')))}</span> •
                                            <span>Điểm khớp: {html.escape(str(hit.get('score')))}</span>
                                        </div>
                                        <div class="ws-card-body">{html.escape(str(hit.get('facts')))}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                        elif isinstance(res, dict) and (res.get("markdown") or res.get("text")):
                            st.markdown(res.get("markdown") or res.get("text") or "")
                        else:
                            st.json(res, expanded=True)

            # --- TAB 2: CHẠY THỬ TRỰC TIẾP 10 CÔNG CỤ (0 TỐN TOKEN LLM) ---
            with ws_tab_playground:
                st.caption("Gọi trực tiếp hàm Python trong `TOOL_FUNCTIONS` để kiểm tra API Key và dữ liệu đầu ra (không tốn token LLM).")
                selected_tool = st.selectbox(
                    "Chọn công cụ cần kiểm tra:",
                    options=list(TOOL_FUNCTIONS.keys()),
                    format_func=lambda k: f"{k} — {TOOL_META.get(k, {}).get('label', k)} ({TOOL_META.get(k, {}).get('desc', '')})",
                )
                with st.form("playground_form"):
                    if selected_tool == "lookup":
                        q = st.text_input("Từ khóa (query)", value="AI agent breakthroughs")
                        c1, c2, c3 = st.columns(3)
                        topic = c1.selectbox("Phân loại (topic)", ["general", "news"], index=1)
                        timeframe = c2.selectbox("Thời gian (timeframe)", ["day", "week", "month", "year"], index=1)
                        max_res = c3.number_input("Số kết quả (max_results)", 1, 10, 5)
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi lookup", type="primary")
                        if run_btn:
                            args = {"query": q, "topic": topic, "timeframe": timeframe, "max_results": int(max_res)}
                            out = TOOL_FUNCTIONS["lookup"](**args)
                            st.session_state.workspace_events = [{"tool": "lookup", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "fetch":
                        url_in = st.text_input("Địa chỉ URL (url)", value="https://openai.com/research/")
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi fetch", type="primary")
                        if run_btn:
                            args = {"url": url_in}
                            out = TOOL_FUNCTIONS["fetch"](**args)
                            st.session_state.workspace_events = [{"tool": "fetch", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "timeline":
                        c1, c2 = st.columns([3, 1])
                        handle = c1.text_input("Handle X không có @ (screenname)", value="sama")
                        lim = c2.number_input("Số bài (limit)", 1, 10, 5)
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi timeline", type="primary")
                        if run_btn:
                            args = {"screenname": handle.lstrip("@"), "limit": int(lim)}
                            out = TOOL_FUNCTIONS["timeline"](**args)
                            st.session_state.workspace_events = [{"tool": "timeline", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "social_search":
                        c1, c2, c3 = st.columns([3, 1.5, 1])
                        sq = c1.text_input("Từ khóa (query)", value="OpenAI")
                        stype = c2.selectbox("Sắp xếp (search_type)", ["Latest", "Top"])
                        lim = c3.number_input("Số bài (limit)", 1, 10, 5)
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi social_search", type="primary")
                        if run_btn:
                            args = {"query": sq, "search_type": stype, "limit": int(lim)}
                            out = TOOL_FUNCTIONS["social_search"](**args)
                            st.session_state.workspace_events = [{"tool": "social_search", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "policy":
                        c1, c2, c3 = st.columns([3, 2, 1])
                        pq = c1.text_input("Truy vấn (query)", value="source citation")
                        parea = c2.selectbox("Khu vực (policy_area)", ["all", "ai_research", "source_citation", "data_privacy", "external_publishing", "tool_usage"])
                        topk = c3.number_input("Top K", 1, 5, 3)
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi policy", type="primary")
                        if run_btn:
                            args = {"query": pq, "policy_area": parea, "top_k": int(topk)}
                            out = TOOL_FUNCTIONS["policy"](**args)
                            st.session_state.workspace_events = [{"tool": "policy", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "papers":
                        c1, c2, c3 = st.columns([3, 1.5, 1])
                        aq = c1.text_input("Từ khóa arXiv (query)", value="tool calling evaluation")
                        asort = c2.selectbox("Sắp xếp (sort_by)", ["relevance", "lastUpdatedDate", "submittedDate"])
                        amax = c3.number_input("Số bài (max_results)", 1, 10, 3)
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi papers", type="primary")
                        if run_btn:
                            args = {"query": aq, "max_results": int(amax), "sort_by": asort}
                            out = TOOL_FUNCTIONS["papers"](**args)
                            st.session_state.workspace_events = [{"tool": "papers", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "paper_text":
                        c1, c2 = st.columns([3, 1])
                        aid = c1.text_input("ID hoặc URL arXiv (arxiv_url)", value="1706.03762")
                        apages = c2.number_input("Số trang (max_pages)", 1, 10, 2)
                        run_btn = st.form_submit_button(":material/play_arrow: Thực thi paper_text", type="primary")
                        if run_btn:
                            args = {"arxiv_url": aid, "max_pages": int(apages), "max_chars": 6000}
                            out = TOOL_FUNCTIONS["paper_text"](**args)
                            st.session_state.workspace_events = [{"tool": "paper_text", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    elif selected_tool == "send":
                        msg_txt = st.text_input("Nội dung tin nhắn Telegram (text)", value="Bản tin thử nghiệm từ Research Agent Studio")
                        conf_flag = st.checkbox("Đã xác nhận gửi (confirmed=True)", value=False)
                        run_btn = st.form_submit_button(":material/send: Thực thi send", type="primary")
                        if run_btn:
                            args = {"text": msg_txt, "confirmed": bool(conf_flag)}
                            out = TOOL_FUNCTIONS["send"](**args)
                            st.session_state.workspace_events = [{"tool": "send", "args": args, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

                    else:
                        raw_json_args = st.text_area("Tham số JSON:", value="{}")
                        run_btn = st.form_submit_button(f":material/play_arrow: Thực thi {selected_tool}", type="primary")
                        if run_btn:
                            parsed = json.loads(raw_json_args or "{}")
                            out = TOOL_FUNCTIONS[selected_tool](**parsed)
                            st.session_state.workspace_events = [{"tool": selected_tool, "args": parsed, "result": out}]
                            st.session_state.active_turn_num = None
                            st.rerun()

            # --- TAB 3: NHẬT KÝ TRANSCRIPT JSON (GỬI ĐỨC) & EVAL RUNS ---
            with ws_tab_logs:
                st.markdown("##### 1. Nhật ký Phiên Hội Thoại Hiện Tại (`transcripts/*.transcript.json`)")
                if st.session_state.transcript_path and st.session_state.transcript:
                    c_dl1, c_dl2 = st.columns([3, 1.5])
                    c_dl1.success(f"File đang ghi: `{st.session_state.transcript_path.name}` ({len(st.session_state.ui_turns)} lượt)")
                    json_bytes = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
                    c_dl2.download_button(
                        ":material/download: Tải .transcript.json (Gửi Đức)",
                        data=json_bytes,
                        file_name=st.session_state.transcript_path.name,
                        mime="application/json",
                        use_container_width=True,
                        type="primary",
                    )
                    # Bảng tóm tắt chuẩn mục B4 của REPORT.md
                    b4_rows = []
                    for t in st.session_state.ui_turns:
                        calls_str = ", ".join(
                            f"{e['tool']}({json.dumps(e.get('args', {}), ensure_ascii=False)})"
                            for e in t.get("tool_events", [])
                        ) or "(no_tool)"
                        b4_rows.append({
                            "Turn": t.get("turn_index"),
                            "User Request": t.get("user"),
                            "Tool Calls": calls_str,
                            "Version Evidence": artifact_ver.artifact_version,
                            "Status": t.get("status"),
                        })
                    st.dataframe(b4_rows, use_container_width=True, hide_index=True)
                    with st.expander("Xem toàn bộ nội dung JSON của Transcript"):
                        st.json(st.session_state.transcript, expanded=False)
                else:
                    st.info("Chưa có lượt hội thoại nào trong phiên này. Hãy chạy ít nhất 3 lượt ở khung bên phải để xuất file gửi Đức.")

                st.divider()
                st.markdown("##### 2. Tra cứu các File Transcript & Eval Runs đã lưu trên máy")
                tx_dir = ROOT / "transcripts"
                tx_files = sorted(tx_dir.glob("*.transcript.json"), key=lambda p: p.stat().st_mtime, reverse=True) if tx_dir.exists() else []
                if tx_files:
                    chosen_tx = st.selectbox("Xem file transcript trong thư mục `transcripts/`:", tx_files, format_func=lambda p: p.name)
                    if chosen_tx:
                        with st.expander(f"Nội dung `{chosen_tx.name}`"):
                            st.json(json.loads(chosen_tx.read_text(encoding="utf-8")), expanded=False)

            # --- TAB 4: THÔNG SỐ ARTIFACT, SYSTEM PROMPT & TOOLS.YAML ---
            with ws_tab_specs:
                st.markdown("##### 1. Mã định danh Phiên bản (Artifact Hashes)")
                st.code(
                    json.dumps(
                        {
                            "version": artifact_ver.version,
                            "artifact_version": artifact_ver.artifact_version,
                            "prompt_hash": artifact_ver.prompt_hash,
                            "tools_hash": artifact_ver.tools_hash,
                        },
                        indent=2,
                    ),
                    language="json",
                )
                st.markdown("##### 2. Bảng Công cụ khai báo trong `artifacts/tools.yaml` (Dùng cho Phần A2 Báo cáo)")
                try:
                    decls = load_tool_declarations(tools_path)
                    rows = []
                    for d in decls:
                        name = d["name"]
                        props = list((d.get("parameters", {}) or {}).get("properties", {}).keys())
                        rows.append({
                            "Tên Tool": name,
                            "Nhóm": TOOL_META.get(name, {}).get("label", "Tool mở rộng"),
                            "Tham số": ", ".join(props),
                            "Mô tả trong tools.yaml": d.get("description", ""),
                        })
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                except Exception as exc:
                    st.error(f"Lỗi đọc tools.yaml: {exc}")

                with st.expander("Xem nội dung `artifacts/system_prompt.md` hiện tại"):
                    st.code(system_prompt_path.read_text(encoding="utf-8"), language="markdown")


# =====================================================================
# PANE PHẢI: THANH TRỢ LÝ AI (SIDER PANEL)
# =====================================================================
def render_turn_messages(turn: dict[str, Any]) -> None:
    user_text = html.escape(turn["user"])
    st.html(f'<div class="sider-user-msg">{user_text}</div>')
    assistant_text = turn.get("assistant_text") or ""
    if turn.get("status") == "provider_error":
        st.error(turn.get("error") or "Lỗi gọi nhà cung cấp AI")
    elif turn.get("status") == "waiting_for_user":
        st.html(
            '<div class="sider-clarify-msg"><strong>Cần bổ sung thông tin</strong><br>'
            f'{html.escape(assistant_text)}</div>'
        )
    else:
        st.markdown(assistant_text or "_Trợ lý chưa trả về nội dung._")


def render_conversation_history(*, compact: bool) -> None:
    st.markdown("#### Lịch sử hội thoại")
    entries = saved_conversations()
    if not entries:
        st.info("Chưa có hội thoại đã lưu. Lượt chat đầu tiên sẽ xuất hiện ở đây.")
        return

    with st.container(key="sider_history_list"):
        for path, (modified, turns) in entries.items():
            chat_col, delete_col = st.columns([8, 1], gap="small")
            if chat_col.button(
                conversation_title(turns),
                key=f"sider_history_{path.name}",
                help=f"Cập nhật {modified:%d/%m/%Y %H:%M} · {len(turns)} lượt",
                use_container_width=True,
            ):
                try:
                    open_conversation(path)
                except (OSError, ValueError, KeyError, TypeError):
                    st.error("Không thể mở hội thoại. Hãy tải lại danh sách.")
                else:
                    st.rerun()
            with delete_col.popover("×", help="Xóa hội thoại"):
                st.write(f"Xóa hội thoại “{conversation_title(turns)}”?")
                st.caption("Hội thoại sẽ bị xóa khỏi danh sách và tệp đã lưu.")
                if st.button("Xác nhận xóa", key=f"sider_delete_{path.name}"):
                    try:
                        with transcript_lock():
                            if path.is_symlink():
                                raise OSError("Đường dẫn hội thoại không hợp lệ.")
                            path.unlink()
                        if st.session_state.transcript_path == path:
                            reset_conversation()
                            st.session_state.sider_tab = ":material/history: Lịch sử"
                        st.rerun()
                    except OSError:
                        st.error("Không thể xóa hội thoại. Hãy tải lại danh sách.")


def select_sider_tab(tab: str) -> None:
    st.session_state.sider_tab = tab


with col_sider:
    with (nullcontext() if is_sidepanel_only else st.container(border=True, height=760)):
        if not is_sidepanel_only:
            st.html('<h2 class="sider-heading">Trợ lý nghiên cứu</h2>')
        st.button(
            ":material/add: Hội thoại mới",
            key="sider_new_chat",
            on_click=reset_conversation,
            type="primary",
            use_container_width=True,
        )
        sider_tabs = (
            (":material/chat: Trò chuyện", ":material/chat_bubble:", "Trò chuyện"),
            (":material/history: Lịch sử", ":material/history:", "Lịch sử"),
            (":material/tune: Cài đặt", ":material/settings:", "Cài đặt"),
        )
        if st.session_state.sider_tab not in [item[0] for item in sider_tabs]:
            st.session_state.sider_tab = sider_tabs[0][0]
        with st.container(key="sider_navigation"):
            targets = [st] * len(sider_tabs) if is_sidepanel_only else st.columns(len(sider_tabs))
            for target, (tab, icon, label) in zip(targets, sider_tabs):
                target.button(
                    icon,
                    key=f"sider_nav_{label}",
                    help=label,
                    type="primary" if st.session_state.sider_tab == tab else "secondary",
                    on_click=select_sider_tab,
                    args=(tab,),
                    use_container_width=not is_sidepanel_only,
                )

        # ---------------- MODE 1: SIDER CHAT STREAM ----------------
        if st.session_state.sider_tab == ":material/chat: Trò chuyện":
            if st.session_state.sider_save_error:
                st.warning(st.session_state.sider_save_error)
            with (nullcontext() if is_sidepanel_only else st.container(height=555, border=False)):
                if st.session_state.ui_turns:
                    title = html.escape(conversation_title(st.session_state.ui_turns))
                    st.html(f'<div class="sider-conversation-title">{title}</div>')
                else:
                    st.html(
                        '<div class="sider-welcome"><h2>Hỏi bất cứ điều gì hoặc giao một tác vụ</h2>'
                        '<p>Trò chuyện, tra cứu và nghiên cứu cùng trợ lý AI của bạn.</p></div>'
                    )

                for idx, turn in enumerate(st.session_state.ui_turns):
                    render_turn_messages(turn)
                    t_events = turn.get("tool_events") or []
                    if t_events:
                        with st.expander(f"Công cụ đã gọi · {len(t_events)}"):
                            st.html("".join(format_thought_step_html(event) for event in t_events))

                    # 4. Sider-style Artifact Card button to view data on Left Workspace
                    if t_events and not is_sidepanel_only:
                        b_c1, b_c2 = st.columns([3, 2])
                        with b_c1:
                            if st.button(
                                f":material/open_in_new: Xem dữ liệu Lượt #{turn['turn_index']} ở màn hình trái",
                                key=f"view_ws_{idx}",
                                use_container_width=True,
                            ):
                                st.session_state.workspace_events = t_events
                                st.session_state.active_turn_num = turn["turn_index"]
                                st.rerun()
                        with b_c2:
                            with st.popover(":material/data_object: Xem JSON"):
                                st.json(t_events, expanded=True)

                    # 5. Quick reply buttons if this is the latest turn
                    if idx == len(st.session_state.ui_turns) - 1:
                        clarify_opts = extract_clarify_options(t_events)
                        if clarify_opts:
                            opt_cols = [st] if is_sidepanel_only else st.columns(min(len(clarify_opts), 2))
                            for o_i, opt_val in enumerate(clarify_opts):
                                if opt_cols[o_i % len(opt_cols)].button(
                                    opt_val,
                                    key=f"clarify_btn_{idx}_{o_i}",
                                    use_container_width=True,
                                    type="primary" if o_i == 0 else "secondary",
                                ):
                                    st.session_state.pending_input = opt_val
                                    st.rerun()

                        pending_tg_text = needs_telegram_confirmation(t_events)
                        if pending_tg_text:
                            if st.button(
                                ":material/send: Xác nhận gửi bản tin lên Telegram (confirmed=True)",
                                key=f"confirm_tg_{idx}",
                                use_container_width=True,
                                type="primary",
                            ):
                                st.session_state.pending_input = f"Tôi xác nhận đồng ý gửi nội dung này lên Telegram: {pending_tg_text}"
                                st.rerun()

            # Native Chat Input at bottom of Sider panel (Enter to send)
            typed_prompt = st.chat_input(
                "Hỏi bất cứ điều gì hoặc mô tả một tác vụ...",
                disabled=bool(st.session_state.sider_save_error),
            )
            active_prompt = st.session_state.pending_input or typed_prompt
            st.session_state.pending_input = None

            if active_prompt and active_prompt.strip():
                with st.spinner("Đang phân tích và thực thi công cụ..."):
                    execute_agent_turn(
                        user_text=active_prompt.strip(),
                        provider_name=st.session_state.cfg_provider,
                        model_override=st.session_state.cfg_model.strip() or None,
                        version_label=st.session_state.cfg_version.strip() or "v3",
                        system_prompt_path=system_prompt_path,
                        tools_path=tools_path,
                        history_window=int(st.session_state.cfg_history),
                        max_tool_rounds=int(st.session_state.cfg_rounds),
                    )
                st.rerun()

        elif st.session_state.sider_tab == ":material/history: Lịch sử":
            render_conversation_history(compact=is_sidepanel_only)

        # ---------------- MODE 3: CONFIGURATION ----------------
        elif st.session_state.sider_tab == ":material/tune: Cài đặt":
            st.markdown("##### Cấu hình Model & Phiên bản")
            providers_list = ["openrouter", "openai", "gemini", "anthropic", "ollama"]
            st.session_state.cfg_provider = st.selectbox(
                "Provider",
                options=providers_list,
                index=providers_list.index(st.session_state.cfg_provider),
            )
            st.session_state.cfg_model = st.text_input(
                "Model override (để trống = mặc định của provider)",
                value=st.session_state.cfg_model,
                placeholder="VD: openai/gpt-4o-mini hoặc qwen2.5:7b",
            )
            c_v1, c_v2 = (st, st) if is_sidepanel_only else st.columns(2)
            version_options = ["v3", "v2", "v1", "v0", "v4-local", "v5-local"]
            if st.session_state.cfg_version not in version_options:
                version_options.insert(0, st.session_state.cfg_version)
            st.session_state.cfg_version = c_v1.selectbox(
                "Nhãn Version",
                options=version_options,
                index=version_options.index(st.session_state.cfg_version),
                accept_new_options=True,
                help="Chọn v0..v3 hoặc tự gõ nhãn mới rồi nhấn Enter",
            )
            st.session_state.cfg_rounds = c_v2.number_input("Max Tool Rounds", 1, 8, int(st.session_state.cfg_rounds))
            st.session_state.cfg_history = st.slider(
                "Cửa sổ nhớ ngữ cảnh (History Window)",
                min_value=1,
                max_value=10,
                value=int(st.session_state.cfg_history),
            )
            st.divider()
            st.caption(f"**Artifact Version:** `{artifact_ver.artifact_version}`")
            if st.session_state.transcript_path:
                json_dl = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
                st.download_button(
                    ":material/download: Tải file Transcript JSON",
                    data=json_dl,
                    file_name=st.session_state.transcript_path.name,
                    mime="application/json",
                    use_container_width=True,
                )
