# import gradio as gr
import gradio
# import lmdb
# import base64
# import io
# import random
# import time
import json
import copy
# import sqlite3
from urllib.parse import urljoin
import openai

from app_js import saved_prompts_refresh_btn__click_js, selected_saved_prompt_title__change_js, saved_prompts_delete_btn__click_js, saved_prompts_save_btn__click_js, copy_prompt__click_js, paste_prompt__click_js, chat_copy_history_btn__click_js, chat_copy_history_md_btn__click_js, api_key_refresh_btn__click_js, api_key_save_btn__click_js

DEFAULT_PROMPT = [
    ["system", "You(assistant) are a helpful AI assistant."],
]


def on_click_send_btn(
        global_state_json, api_key_text, chat_input_role, chat_input, prompt_table, chat_use_prompt, chat_use_history, chat_log,
        chat_model, temperature, top_p, choices_num, stream, max_tokens, presence_penalty, frequency_penalty, logit_bias,
    ):

    old_state = json.loads(global_state_json or "{}")

    print('\n\n\n\n\n')
    print(prompt_table)
    prompt_table = prompt_table or []

    chat_log = chat_log or []

    chat_log_md = ''
    if chat_use_prompt:
        chat_log_md += '<center>(prompt)</center>\n\n'
        chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", prompt_table)])
        chat_log_md += '\n---\n'
    if True:
        chat_log_md += '<center>(history)</center>\n\n' if chat_use_history else '<center>(not used history)</center>\n\n'
        chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", chat_log)])
        chat_log_md += '\n---\n'

    # if chat_input=='':
    #     return json.dumps(old_state), chat_log, chat_log_md, chat_log_md, None, None, chat_input

    print('\n')
    print(chat_input)
    print('')

    try:
        logit_bias_json = json.dumps(logit_bias) if logit_bias else None
    except:
        return json.dumps(old_state), chat_log, chat_log_md, chat_log_md, None, None, chat_input

    new_state = copy.deepcopy(old_state) or {}



    req_hist = copy.deepcopy(prompt_table) if chat_use_prompt else []

    if chat_use_history:
        for hh in (chat_log or []):
            req_hist.append(hh)

    if chat_input and chat_input!="":
        req_hist.append([(chat_input_role or 'user'), chat_input])

    openai.api_key = api_key_text

    props = {
        'model': chat_model,
        'messages': [xx for xx in map(lambda it: {'role':it[0], 'content':it[1]}, req_hist)],
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
        print(completion.choices)
        the_response_role = completion.choices[0].message.role
        the_response = completion.choices[0].message.content
        print(the_response)
        print('')
        chat_last_resp = json.dumps(completion.__dict__)
        chat_last_resp_dict = json.loads(chat_last_resp)
        chat_last_resp_dict['api_key'] = "hidden by UI"
        chat_last_resp_dict['organization'] = "hidden by UI"
        chat_last_resp = json.dumps(chat_last_resp_dict)

        chat_log_md = ''
        if chat_use_prompt:
            chat_log_md += '<center>(prompt)</center>\n\n'
            chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", prompt_table)])
            chat_log_md += '\n---\n'
        if True:
            chat_log_md += '<center>(history)</center>\n\n' if chat_use_history else '<center>(not used history)</center>\n\n'
            chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", chat_log)])
            chat_log_md += '\n---\n'

        if chat_input and chat_input!="":
            chat_log.append([(chat_input_role or 'user'), chat_input])
            chat_log_md += f"##### `{(chat_input_role or 'user')}`\n\n{chat_input}\n\n"
        chat_log.append([the_response_role, the_response])
        chat_log_md += f"##### `{the_response_role}`\n\n{the_response}\n\n"

        return json.dumps(new_state), chat_log, chat_log_md, chat_log_md, chat_last_resp, props_json, ''
    except Exception as error:
        print(error)

        chat_log_md = ''
        if chat_use_prompt:
            chat_log_md += '<center>(prompt)</center>\n\n'
            chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", prompt_table)])
            chat_log_md += '\n---\n'
        if True:
            chat_log_md += '<center>(history)</center>\n\n' if chat_use_history else '<center>(not used history)</center>\n\n'
            chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", chat_log)])
            chat_log_md += '\n---\n'

        # chat_log_md = ''
        # chat_log_md = "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", prompt_table)]) if chat_use_prompt else ''
        # chat_log_md += "\n".join([xx for xx in map(lambda it: f"##### `{it[0]}`\n\n{it[1]}\n\n", hist)])

        chat_log_md += "\n"
        chat_log_md += str(error)
        return json.dumps(new_state), chat_log, chat_log_md, chat_log_md, None, props_json, chat_input


def clear_history():
    return [], ""


def copy_history(txt):
    # print('\n\n copying')
    # print(txt)
    # print('\n\n')
    pass


def update_saved_prompt_titles(global_state_json, selected_saved_prompt_title):
    print('')
    global_state = json.loads(global_state_json or "{}")
    print(global_state)
    print(selected_saved_prompt_title)
    saved_prompts = global_state.get('saved_prompts') or []
    print(saved_prompts)
    the_choices = [(it.get('title') or '[untitled]') for it in saved_prompts]
    print(the_choices)
    print('')
    return gradio.Dropdown.update(choices=the_choices)


def save_prompt(global_state_json, saved_prompts, prompt_title, prompt_table):
    the_choices = []
    global_state = json.loads(global_state_json or "{}")
    saved_prompts = global_state.get('saved_prompts') or []
    if len(saved_prompts):
        the_choices = [it.get('title') or '[untitled]' for it in saved_prompts]
        pass
    return global_state_json, gradio.Dropdown.update(choices=the_choices, value=prompt_title), prompt_title, prompt_table


def load_saved_prompt(title):
    pass


css = """
.table-wrap .cell-wrap input {min-width:80%}
#api-key-textbox textarea {filter:blur(8px); transition: filter 0.25s}
#api-key-textbox textarea:focus {filter:none}
#chat-log-md hr {margin-top: 1rem; margin-bottom: 1rem;}
"""
with gradio.Blocks(title="ChatGPT", css=css) as demo:
    global_state_json = gradio.Textbox(visible=False)

    # https://gradio.app/docs
    # https://platform.openai.com/docs/api-reference/chat/create

    with gradio.Tab("ChatGPT"):

        with gradio.Row():
            with gradio.Box():
                with gradio.Column(scale=12):
                    with gradio.Row():
                        api_key_text = gradio.Textbox(label="Your API key", elem_id="api-key-textbox")
                    with gradio.Row():
                        with gradio.Column(scale=2):
                            api_key_refresh_btn = gradio.Button("🔄 Load from browser storage")
                            api_key_refresh_btn.click(
                                # get_settings,
                                None,
                                inputs=[],
                                outputs=[api_key_text],
                                # api_name="load-api-key",
                                _js=api_key_refresh_btn__click_js,
                            )
                        with gradio.Column(scale=2):
                            api_key_save_btn = gradio.Button("💾 Save to browser storage")
                            api_key_save_btn.click(
                                # save_settings,
                                None,
                                inputs=[api_key_text],
                                outputs=[api_key_text],
                                # api_name="save-api-key",
                                _js=api_key_save_btn__click_js,
                            )
                    with gradio.Row():
                        gradio.Markdown("Go to https://platform.openai.com/account/api-keys to get your API key.")

        with gradio.Row():
            with gradio.Box():
                gradio.Markdown("**Prompt**")
                with gradio.Column(scale=12):
                    with gradio.Row():
                        prompt_table = gradio.Dataframe(
                            type='array',
                            label='Prompt content', col_count=(2, 'fixed'), max_cols=2,
                            value=DEFAULT_PROMPT, headers=['role', 'content'], interactive=True,
                        )
                    with gradio.Row():
                        gradio.Markdown("The Table above is editable. The content will be added to the beginning of the conversation (if you check 'send with prompt' as `√`). See https://platform.openai.com/docs/guides/chat/introduction .")
                    with gradio.Row():
                        with gradio.Column(scale=6):
                            prompt_title = gradio.Textbox(label='Prompt title (only for saving)')
                        with gradio.Column(scale=6):
                            selected_saved_prompt_title = gradio.Dropdown(label='Select prompt from saved list (click ♻️ then 🔄)')
                    with gradio.Row():
                        with gradio.Column(scale=1, min_width=100):
                            saved_prompts_refresh_btn = gradio.Button("♻️")
                        with gradio.Column(scale=1, min_width=100):
                            saved_prompts_save_btn = gradio.Button("💾")
                        with gradio.Column(scale=1, min_width=100):
                            saved_prompts_delete_btn = gradio.Button("🗑")
                        with gradio.Column(scale=1, min_width=100):
                            saved_prompts_list_refresh_btn = gradio.Button("🔄")
                        with gradio.Column(scale=1, min_width=100):
                            copy_prompt = gradio.Button("📑")
                        with gradio.Column(scale=1, min_width=100):
                            paste_prompt = gradio.Button("📋")
                    with gradio.Row():
                        gradio.Markdown("""Buttons above:  ♻️ then 🔄: Load prompts from browser storage.  💾 then 🔄: Save current prompt to browser storage, overwrite the prompt with the same title.  🗑 then 🔄: Delete prompt with the same title from browser storage.  🔄 : Update the selector list.  📑 : Copy current prompt to clipboard.  📋 : Paste prompt from clipboard (need [permission](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/readText#browser_compatibility)).""")

                copy_prompt.click(None, inputs=[prompt_title, prompt_table], outputs=[prompt_title, prompt_table], _js=copy_prompt__click_js)
                paste_prompt.click(None, inputs=[prompt_title, prompt_table], outputs=[prompt_title, prompt_table], _js=paste_prompt__click_js)
                saved_prompts_refresh_btn.click(None, inputs=[global_state_json, selected_saved_prompt_title], outputs=[global_state_json, selected_saved_prompt_title], _js=saved_prompts_refresh_btn__click_js)

                saved_prompts_list_refresh_btn.click(
                    update_saved_prompt_titles, inputs=[global_state_json, selected_saved_prompt_title], outputs=[selected_saved_prompt_title],
                )

                selected_saved_prompt_title.change(None, inputs=[global_state_json, selected_saved_prompt_title], outputs=[global_state_json, prompt_title, prompt_table], _js=selected_saved_prompt_title__change_js)

                saved_prompts_delete_btn.click(None, inputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], outputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], _js=saved_prompts_delete_btn__click_js)

                saved_prompts_save_btn.click(None, inputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], outputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], _js=saved_prompts_save_btn__click_js)


        with gradio.Row():
            with gradio.Column(scale=4):
                with gradio.Box():
                    gradio.Markdown("See https://platform.openai.com/docs/api-reference/chat/create .")
                    chat_model = gradio.Dropdown(label="model", choices=[
                        "gpt-3.5-turbo", "gpt-3.5-turbo-0301",
                        "gpt-4", "gpt-4-0314", "gpt-4-32k", "gpt-4-32k-0314",
                    ], value="gpt-3.5-turbo")
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
                            with gradio.Column(scale=10):
                                chat_log_box = gradio.Markdown(label='chat history', value="<center>(empty)</center>", elem_id="chat-log-md")
                                real_md_box = gradio.Textbox(value="", visible=False)
                                with gradio.Row():
                                    chat_copy_history_btn = gradio.Button("Copy all (as HTML)")
                                    chat_copy_history_md_btn = gradio.Button("Copy all (as Markdown)")

                            chat_copy_history_btn.click(
                                copy_history, inputs=[chat_log_box],
                                _js=chat_copy_history_btn__click_js,
                            )
                            chat_copy_history_md_btn.click(
                                copy_history, inputs=[real_md_box],
                                _js=chat_copy_history_md_btn__click_js,
                            )
                        chat_input_role = gradio.Dropdown(label='role', choices=['user', 'system', 'assistant'], value='user')
                        chat_input = gradio.Textbox(lines=4, label='input')
                with gradio.Row():
                    chat_clear_history_btn = gradio.Button("clear history")
                    chat_clear_history_btn.click(clear_history, inputs=[], outputs=[chat_log, chat_log_box])
                    chat_use_prompt = gradio.Checkbox(label='send with prompt', value=True)
                    chat_use_history = gradio.Checkbox(label='send with history', value=True)
                    chat_send_btn = gradio.Button("send")
                pass

        with gradio.Row():
            chat_last_req = gradio.JSON(label='last request')
            chat_last_resp = gradio.JSON(label='last response')
            chat_send_btn.click(
                on_click_send_btn,
                inputs=[
                    global_state_json, api_key_text, chat_input_role, chat_input, prompt_table, chat_use_prompt, chat_use_history, chat_log,
                    chat_model, chat_temperature, chat_top_p, chat_choices_num, chat_stream, chat_max_tokens, chat_presence_penalty, chat_frequency_penalty, chat_logit_bias,
                ],
                outputs=[global_state_json, chat_log, chat_log_box, real_md_box, chat_last_resp, chat_last_req, chat_input],
                api_name="click-send-btn",
            )

        pass



    with gradio.Tab("Settings"):
        gradio.Markdown('Currently nothing.')
        pass


if __name__ == "__main__":
    demo.queue(concurrency_count=20).launch()
