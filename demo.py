import gradio as gr
import gradio
import lmdb
import base64
import io
import random
import time
import json
import copy
import sqlite3
from urllib.parse import urljoin
import openai


DEFAULT_PROMPT = [
    ["system", "You(assistant) are a helpful assistant, you are helping user(user) to solve problems."],
    ["user", "Who won the world series in 2020?"],
    ["assistant", "The Los Angeles Dodgers won the World Series in 2020."],
]


def get_settings(old_state):
    db_path = './my_app_state'
    env = lmdb.open(db_path, max_dbs=2*1024*1024)
    # print(env.stat())
    txn = env.begin()
    saved_api_key = txn.get(key=b'api_key').decode('utf-8') or ''
    txn.commit()
    env.close()

    new_state = copy.deepcopy(old_state) or {}
    new_state['api_key'] = saved_api_key

    return new_state, saved_api_key


def on_click_send_btn(old_state, api_key_text, chat_input, prompt_table, chat_use_history, chat_log):
    new_state = copy.deepcopy(old_state) or {}

    print(prompt_table)

    hist = prompt_table or []

    if chat_use_history:
        for hh in (chat_log or []):
            hist.append(hh)

    if chat_input:
        hist.append(['user', chat_input])

    openai.api_key = api_key_text
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[xx for xx in map(lambda it: {'role':it[0], 'content':it[1]}, hist)]
    )
    print('')
    print(completion)
    the_response = completion.choices[0].message.content
    print(the_response)
    print('')
    chat_last_resp = json.dumps(completion.__dict__)

    chat_log = chat_log or []
    chat_log.append(['user', chat_input])
    chat_log.append(['assistant', the_response])

    chat_log_md = "\n".join([xx for xx in map(lambda it: f"### {it[0]}\n\n{it[1]}\n\n", chat_log)])

    return new_state, chat_log, chat_log_md, chat_last_resp


def save_settings(old_state, api_key_text):
    db_path = './my_app_state'
    env = lmdb.open(db_path, max_dbs=2*1024*1024)
    # print(env.stat())
    txn = env.begin(write=True)
    txn.put(key=b'api_key', value=api_key_text.encode('utf-8'))
    # 提交事务
    txn.commit()
    return get_settings(old_state)


with gradio.Blocks(title="ChatGPT", css=".table-wrap .cell-wrap input {min-width:80%}") as demo:
    global_state = gradio.State(value={})

    with gradio.Tab("ChatGPT"):
        with gradio.Row():
            with gradio.Column(scale=10):
                gradio.Markdown("Go to https://platform.openai.com/account/api-keys to get your API key.")
                api_key_text = gradio.Textbox(label="Your API key")
        with gradio.Row():
            with gradio.Column(scale=2):
                api_key_refresh_btn = gradio.Button("🔄")
                api_key_refresh_btn.click(get_settings, inputs=[global_state], outputs=[global_state, api_key_text])
            with gradio.Column(scale=2):
                api_key_save_btn = gradio.Button("💾")
                api_key_save_btn.click(save_settings, inputs=[global_state, api_key_text], outputs=[global_state, api_key_text])

        with gradio.Row():
            with gradio.Column(scale=10):
                with gradio.Box():
                    prompt_table = gradio.Dataframe(
                        type='array',
                        label='Prompt', col_count=(2, 'fixed'), max_cols=2,
                        value=DEFAULT_PROMPT, headers=['role', 'content'], interactive=True,
                    )
                    gradio.Markdown("Will be added to the beginning of the conversation. See https://platform.openai.com/docs/guides/chat/introduction .")

        with gradio.Row():
            with gradio.Column(scale=10):
                chat_log = gradio.State()
                with gradio.Box():
                    chat_log_box = gradio.Markdown(label='chat history')
                chat_last_resp = gradio.JSON(label='last response')
                chat_input = gradio.Textbox(lines=4, label='input')
        with gradio.Row():
            chat_clear_history_btn = gradio.Button("clear history")
            chat_use_history = gradio.Checkbox(label='send with history', value=True)
            chat_send_btn = gradio.Button("send")
            chat_send_btn.click(
                on_click_send_btn,
                inputs=[global_state, api_key_text, chat_input, prompt_table, chat_use_history, chat_log],
                outputs=[global_state, chat_log, chat_log_box, chat_last_resp])


        pass

















    with gradio.Tab("Settings"):
        pass


if __name__ == "__main__":
    demo.queue(concurrency_count=20).launch()
