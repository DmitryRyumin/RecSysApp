"""
File: event_handlers.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: File containing functions for configuring event handlers for Gradio components.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.event_handlers.account import event_handler_account
from app.event_handlers.auth import event_handler_auth
from app.event_handlers.login import event_handler_login
from app.event_handlers.instruction import event_handler_instruction
from app.event_handlers.generate_response import event_handler_generate_response
from app.event_handlers.message import event_handler_message
from app.event_handlers.chatbot import event_handler_chatbot_clear
from app.event_handlers.evaluate import event_handler_evaluate
from app.event_handlers.settings import (
    event_handler_type_recommendation,
    event_handler_dropdown_models,
)


def setup_app_event_handlers(
    account,
    step_1,
    userid,
    username,
    group_number,
    dropdown_role,
    auth_row,
    auth,
    noti_auth,
    instruction_column,
    instruction,
    instruction_text,
    start_evaluate,
    step_2,
    chatbot_column,
    chatbotid,
    chatbot,
    chatbot_timer,
    message_row,
    message,
    send_message,
    add_evals_column,
    add_vacancy_skills,
    add_subjects_skills,
    add_range,
    feedback,
    evaluate_column,
    send_evaluate,
    type_recommendation,
    top_items,
    max_skill_words,
    dropdown_models,
    settings_row_2,
    dropdown_courses_grades,
):
    account.click(
        fn=event_handler_account,
        inputs=[account, username],
        outputs=[
            account,
            username,
            group_number,
            dropdown_role,
            step_2,
        ],
        queue=True,
    )

    gr.on(
        triggers=[username.change, group_number.change, dropdown_role.change],
        fn=event_handler_auth,
        inputs=[username, group_number, dropdown_role],
        outputs=[
            auth,
            noti_auth,
        ],
        queue=True,
    )

    auth.click(
        fn=event_handler_login,
        inputs=[username, group_number, dropdown_role],
        outputs=[
            account,
            step_1,
            userid,
            username,
            group_number,
            dropdown_role,
            auth_row,
            auth,
            noti_auth,
            instruction_column,
            instruction,
            instruction_text,
            start_evaluate,
            step_2,
            message_row,
            chatbot_column,
            chatbot,
            message,
            send_message,
        ],
        queue=True,
    )

    start_evaluate.click(
        fn=event_handler_instruction,
        inputs=[],
        outputs=[
            instruction_column,
            instruction,
            instruction_text,
            start_evaluate,
            step_2,
            message_row,
            chatbot_column,
            chatbot,
            message,
            send_message,
        ],
        queue=True,
    )

    message.change(
        fn=event_handler_message,
        inputs=[message],
        outputs=[send_message],
        queue=True,
    )

    gr.on(
        triggers=[message.submit, send_message.click],
        fn=event_handler_generate_response,
        inputs=[
            message,
            chatbot,
            type_recommendation,
            top_items,
            max_skill_words,
            dropdown_courses_grades,
        ],
        outputs=[
            message_row,
            message,
            send_message,
            chatbotid,
            chatbot,
            chatbot_timer,
            add_evals_column,
            add_vacancy_skills,
            add_subjects_skills,
            add_range,
            feedback,
            evaluate_column,
            send_evaluate,
        ],
        queue=True,
    )

    chatbot.clear(
        fn=event_handler_chatbot_clear,
        inputs=[],
        outputs=[
            message_row,
            message,
            send_message,
            chatbot,
            add_evals_column,
            add_vacancy_skills,
            add_subjects_skills,
            add_range,
            feedback,
            evaluate_column,
            send_evaluate,
        ],
        queue=True,
    )

    send_evaluate.click(
        fn=event_handler_evaluate,
        inputs=[],
        outputs=[
            message_row,
            message,
            send_message,
            chatbot,
            add_evals_column,
            add_vacancy_skills,
            add_subjects_skills,
            add_range,
            feedback,
            evaluate_column,
            send_evaluate,
        ],
        queue=True,
    )

    type_recommendation.change(
        fn=event_handler_type_recommendation,
        inputs=[message, type_recommendation],
        outputs=[
            top_items,
            dropdown_models,
            settings_row_2,
            dropdown_courses_grades,
            chatbot,
            send_message,
        ],
        queue=True,
    )

    dropdown_models.change(
        fn=event_handler_dropdown_models,
        inputs=[message, type_recommendation, dropdown_models],
        outputs=[send_message],
        queue=True,
    )
