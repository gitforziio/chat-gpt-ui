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


def on_click_send_btn(
        old_state, api_key_text, chat_input_role, chat_input, prompt_table, chat_use_history, chat_log,
        temperature, top_p, choices_num, stream, max_tokens, presence_penalty, frequency_penalty, logit_bias,
    ):

    chat_log = chat_log or []
    chat_log_md = "\n".join([xx for xx in map(lambda it: f"#### `{it[0]}`\n\n{it[1]}\n\n", chat_log)])

    try:
        logit_bias_json = json.dumps(logit_bias) if logit_bias else None
    except:
        return old_state, chat_log, chat_log_md, None, None, chat_input

    new_state = copy.deepcopy(old_state) or {}

    print(prompt_table)

    hist = prompt_table or []

    if chat_use_history:
        for hh in (chat_log or []):
            hist.append(hh)

    if chat_input and chat_input!="":
        hist.append([(chat_input_role or 'user'), chat_input])

    openai.api_key = api_key_text

    props = {
        'model': "gpt-3.5-turbo",
        'messages': [xx for xx in map(lambda it: {'role':it[0], 'content':it[1]}, hist)],
        'temperature': temperature,
        'top_p': top_p,
        'n': choices_num,
        'stream': stream,
        'presence_penalty': presence_penalty,
        'frequency_penalty': frequency_penalty,
    }
    if max_tokens>0:
        props['max_tokens'] = max_tokens
    if logit_bias_json is not None:
        props['logit_bias'] = logit_bias_json

    props_json = json.dumps(props)

    try:
        completion = openai.ChatCompletion.create(**props)
        print('')
        print(completion)
        the_response_role = completion.choices[0].message.role
        the_response = completion.choices[0].message.content
        print(the_response)
        print('')
        chat_last_resp = json.dumps(completion.__dict__)

        if chat_input and chat_input!="":
            chat_log.append([(chat_input_role or 'user'), chat_input])
        chat_log.append([the_response_role, the_response])

        chat_log_md = "\n".join([xx for xx in map(lambda it: f"#### `{it[0]}`\n\n{it[1]}\n\n", chat_log)])

        return new_state, chat_log, chat_log_md, chat_last_resp, props_json, ''
    except Exception as error:
        print(error)
        chat_log_md = "\n".join([xx for xx in map(lambda it: f"#### `{it[0]}`\n\n{it[1]}\n\n", chat_log)])
        chat_log_md += "\n"
        chat_log_md += str(error)
        return new_state, chat_log, chat_log_md, None, props_json, chat_input


def save_settings(old_state, api_key_text):
    db_path = './my_app_state'
    env = lmdb.open(db_path, max_dbs=2*1024*1024)
    # print(env.stat())
    txn = env.begin(write=True)
    txn.put(key=b'api_key', value=api_key_text.encode('utf-8'))
    # 提交事务
    txn.commit()
    return get_settings(old_state)


css = """
.table-wrap .cell-wrap input {min-width:80%}
#api-key-textbox textarea {filter:blur(8px); transition: filter 0.25s}
#api-key-textbox textarea:focus {filter:none}
"""
with gradio.Blocks(title="ChatGPT", css=css) as demo:
    global_state = gradio.State(value={})

    # https://gradio.app/docs
    # https://platform.openai.com/docs/api-reference/chat/create

    with gradio.Tab("ChatGPT"):

        with gradio.Row():
            with gradio.Column(scale=10):
                gradio.Markdown("Go to https://platform.openai.com/account/api-keys to get your API key.")
                api_key_text = gradio.Textbox(label="Your API key", elem_id="api-key-textbox")

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
            with gradio.Column(scale=4):
                with gradio.Box():
                    gradio.Markdown("See https://platform.openai.com/docs/api-reference/chat/create .")
                    chat_temperature = gradio.Slider(label="temperature", value=1, minimum=0, maximum=2)
                    chat_top_p = gradio.Slider(label="top_p", value=1, minimum=0, maximum=1)
                    chat_choices_num = gradio.Slider(label="choices num(n)", value=1, minimum=1, maximum=20)
                    chat_stream = gradio.Checkbox(label="stream", value=False, visible=False)
                    chat_max_tokens = gradio.Slider(label="max_tokens", value=-1, minimum=-1, maximum=4096)
                    chat_presence_penalty = gradio.Slider(label="presence_penalty", value=0, minimum=-2, maximum=2)
                    chat_frequency_penalty = gradio.Slider(label="frequency_penalty", value=0, minimum=-2, maximum=2)
                    chat_logit_bias = gradio.Textbox(label="logit_bias", visible=False)
                pass
            with gradio.Column(scale=8):
                with gradio.Row():
                    with gradio.Column(scale=10):
                        chat_log = gradio.State()
                        with gradio.Box():
                            chat_log_box = gradio.Markdown(label='chat history')
                        chat_input_role = gradio.Textbox(lines=1, label='role', value='user')
                        chat_input = gradio.Textbox(lines=4, label='input')
                with gradio.Row():
                    chat_clear_history_btn = gradio.Button("clear history")
                    chat_use_history = gradio.Checkbox(label='send with history', value=True)
                    chat_send_btn = gradio.Button("send")
                pass

        with gradio.Row():
            chat_last_resp = gradio.JSON(label='last response')
            chat_last_req = gradio.JSON(label='last request')
            chat_send_btn.click(
                on_click_send_btn,
                inputs=[
                    global_state, api_key_text, chat_input_role, chat_input, prompt_table, chat_use_history, chat_log,
                    chat_temperature, chat_top_p, chat_choices_num, chat_stream, chat_max_tokens, chat_presence_penalty, chat_frequency_penalty, chat_logit_bias,
                ],
                outputs=[global_state, chat_log, chat_log_box, chat_last_resp, chat_last_req, chat_input])

        pass

















    with gradio.Tab("Settings"):
        pass


if __name__ == "__main__":
    demo.queue(concurrency_count=20).launch()
