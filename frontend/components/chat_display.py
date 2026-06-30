from __future__ import annotations

from html import escape

import streamlit as st

from backend.localization.text_sanitizer import sanitize_text
from backend.localization.translator import translate


ICONS = {
    "assistant": "◎",
    "user": "◉",
    "chat": "◌",
    "documents": "▤",
    "audio": "◍",
    "structured": "▦",
}


def render_chat_message(role: str, content: str, language: str = "en") -> None:
    role_key = "user" if role == "user" else "assistant"
    label = (
        translate("you", language)
        if role_key == "user"
        else translate("assistant", language)
    )
    text = escape(sanitize_text(content)).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="ym-chat-row ym-chat-{role_key}">
          <div class="ym-chat-avatar">{escape(ICONS[role_key])}</div>
          <div class="ym-chat-bubble">
            <div class="ym-chat-label">{escape(label)}</div>
            <div class="ym-chat-text">{text}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_citations(citations: list[dict], language: str) -> None:
    if not citations:
        return
    st.markdown(
        f"<div class='ym-citation-title'>{escape(translate('sources', language))}</div>",
        unsafe_allow_html=True,
    )
    for index, citation in enumerate(citations[:3], start=1):
        title = sanitize_text(
            citation.get("document_name") or citation.get("scheme_name") or "Document"
        )
        page = citation.get("page_number", 1)
        section = sanitize_text(citation.get("section_title") or "")
        text = sanitize_text(citation.get("text") or "")
        with st.expander(
            f"{index}. {title} · {translate('page', language)} {page}", expanded=False
        ):
            st.markdown(
                f"""
                <div class="ym-source-card">
                  <div class="ym-source-meta">
                    <span>{escape(section or translate("document", language))}</span>
                    <span>{escape(translate("page", language))} {escape(str(page))}</span>
                  </div>
                  <p>{escape(text[:700])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_home_feature(icon: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="ym-feature-card">
          <div class="ym-feature-icon">{escape(icon)}</div>
          <div>
            <h3>{escape(title)}</h3>
            <p>{escape(body)}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
