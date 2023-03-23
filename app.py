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


DEFAULT_PROMPT = [
    ["system", "You(assistant) are a helpful AI assistant."],
]


# def get_settings(old_state):
#     db_path = './my_app_state'
#     env = lmdb.open(db_path, max_dbs=2*1024*1024)
#     # print(env.stat())
#     txn = env.begin()
#     saved_api_key = txn.get(key=b'api_key').decode('utf-8') or ''
#     txn.commit()
#     env.close()

#     new_state = copy.deepcopy(old_state) or {}
#     new_state['api_key'] = saved_api_key

#     return new_state, saved_api_key


# def save_settings(old_state, api_key_text):
#     db_path = './my_app_state'
#     env = lmdb.open(db_path, max_dbs=2*1024*1024)
#     # print(env.stat())
#     txn = env.begin(write=True)
#     txn.put(key=b'api_key', value=api_key_text.encode('utf-8'))
#     # 提交事务
#     txn.commit()
#     return get_settings(old_state)


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
                                api_name="load-settings",
                                _js="""()=>{
                                    const the_api_key = localStorage?.getItem?.('[gradio][chat-gpt-ui][api_key_text]') ?? '';
                                    return the_api_key;
                                }""",
                            )
                        with gradio.Column(scale=2):
                            api_key_save_btn = gradio.Button("💾 Save to browser storage")
                            api_key_save_btn.click(
                                # save_settings,
                                None,
                                inputs=[api_key_text],
                                outputs=[api_key_text],
                                api_name="save-settings",
                                _js="""(api_key_text)=>{
                                    localStorage.setItem('[gradio][chat-gpt-ui][api_key_text]', api_key_text);
                                    return api_key_text;
                                }""",
                            )
                    with gradio.Row():
                        gradio.Markdown("Go to https://platform.openai.com/account/api-keys to get your API key.")

        with gradio.Row():
            with gradio.Box():
                gradio.Markdown("**Prompt**")
                with gradio.Column(scale=12):
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
                    with gradio.Row():
                        prompt_table = gradio.Dataframe(
                            type='array',
                            label='Prompt content', col_count=(2, 'fixed'), max_cols=2,
                            value=DEFAULT_PROMPT, headers=['role', 'content'], interactive=True,
                        )
                    with gradio.Row():
                        gradio.Markdown("The Table above is editable. The content will be added to the beginning of the conversation (if you check 'send with prompt' as `√`). See https://platform.openai.com/docs/guides/chat/introduction .")

                copy_prompt.click(None, inputs=[prompt_title, prompt_table], outputs=[prompt_title, prompt_table], _js="""(prompt_title, prompt_table)=>{
                    try {
                        const txt = JSON.stringify({
                            title: prompt_title,
                            content: prompt_table,
                        }, null, 2);
                        console.log(txt);
                        const promise = navigator?.clipboard?.writeText?.(txt);
                    } catch(error) {console?.log?.(error);};
                    return [prompt_title, prompt_table];
                }""")
                paste_prompt.click(None, inputs=[prompt_title, prompt_table], outputs=[prompt_title, prompt_table], _js="""async (prompt_title, prompt_table)=>{
                    console.log("flag1");
                    try {
                        const promise = navigator?.clipboard?.readText?.();
                        console.log(promise);
                        console.log("flag1 p");
                        const result = await promise?.then?.((txt)=>{
                            console.log("flag1 t");
                            const json = JSON.parse(txt);
                            const title = json?.title ?? "";
                            console.log("flag1 0");
                            console.log(title);
                            const content = json?.content ?? {data: [], headers: ['role', 'content']};
                            console.log(content);
                            const result = [title, content];
                            console.log("flag1 1");
                            console.log(result);
                            console.log("flag1 2");
                            return result;
                        });
                        console.log("flag1 3");
                        if (result!=null) {
                            return result;
                        };
                    } catch(error) {console?.log?.(error);};
                    console.log("flag2");
                    try {
                        const promise = navigator?.clipboard?.read?.();
                        console.log(promise);
                        promise?.then?.((data)=>{
                            console.log(data);
                        });
                    } catch(error) {console?.log?.(error);};
                    console.log("flag3");
                    return [prompt_title, prompt_table];
                }""")
                saved_prompts_refresh_btn.click(None, inputs=[global_state_json, selected_saved_prompt_title], outputs=[global_state_json, selected_saved_prompt_title], _js="""(global_state_json, saved_prompts)=>{
                    try {
                        if(global_state_json=="") {global_state_json=null;};
                        console.log('global_state_json:\\n', global_state_json);
                        const global_state = JSON.parse(global_state_json??"{ }")??{ };

                        const saved = (JSON.parse(localStorage?.getItem?.('[gradio][chat-gpt-ui][prompts]') ?? '[]'));
                        console.log('saved:\\n', saved);
                        global_state['saved_prompts'] = saved;
                        global_state['selected_saved_prompt_title'] = saved.map(it=>it?.title??"[untitled]")[0];

                        const results = [JSON.stringify(global_state), global_state['selected_saved_prompt_title']];
                        console.log(results);
                        return results;
                    } catch(error) {
                        console.log(error);
                        return ["{ }", ""];
                    };
                }""")

                saved_prompts_list_refresh_btn.click(
                    update_saved_prompt_titles, inputs=[global_state_json, selected_saved_prompt_title], outputs=[selected_saved_prompt_title],
                )

                selected_saved_prompt_title.change(None, inputs=[global_state_json, selected_saved_prompt_title], outputs=[global_state_json, prompt_title, prompt_table], _js="""(global_state_json, selected_saved_prompt_title)=>{
                    if(global_state_json=="") {global_state_json=null;};
                    const global_state = JSON.parse(global_state_json??"{ }")??{ };
                    const found = (global_state?.['saved_prompts']??[]).find(it=>it?.title==selected_saved_prompt_title);
                    return [JSON.stringify(global_state), found?.title??'', found?.content??{data:[], headers:["role", "content"]}];
                }""")

                saved_prompts_delete_btn.click(None, inputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], outputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], _js="""(global_state_json, saved_prompts, prompt_title, prompt_table)=>{
                    if(prompt_title==""||!prompt_title){
                        return [global_state_json, selected_saved_prompt_title, prompt_title, prompt_table];
                    };
                    console.log('global_state_json:\\n', global_state_json);

                    if(global_state_json=="") {global_state_json=null;};
                    const global_state = JSON.parse(global_state_json??"{ }")??{ };
                    console.log(global_state);

                    const saved = (JSON.parse(localStorage?.getItem?.('[gradio][chat-gpt-ui][prompts]') ?? '[]'));
                    console.log('saved:\\n', saved);


                    global_state['saved_prompts'] = saved?.filter?.(it=>it.title!=prompt_title)??[];

                    global_state['selected_saved_prompt_title'] = "";

                    console.log(global_state);

                    localStorage?.setItem?.('[gradio][chat-gpt-ui][prompts]', JSON.stringify(global_state['saved_prompts']));

                    return [JSON.stringify(global_state), "", "", {data: [], headers: ['role', 'content']}];
                }""")

                saved_prompts_save_btn.click(None, inputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], outputs=[global_state_json, selected_saved_prompt_title, prompt_title, prompt_table], _js="""(global_state_json, saved_prompts, prompt_title, prompt_table)=>{
                    if(prompt_title==""||!prompt_title){
                        return [global_state_json, selected_saved_prompt_title, prompt_title, prompt_table];
                    };
                    console.log('global_state_json:\\n', global_state_json);

                    if(global_state_json=="") {global_state_json=null;};
                    const global_state = JSON.parse(global_state_json??"{ }")??{ };
                    console.log(global_state);

                    const saved = (JSON.parse(localStorage?.getItem?.('[gradio][chat-gpt-ui][prompts]') ?? '[]'));
                    console.log('saved:\\n', saved);


                    const new_prompt_obj = {
                        title: prompt_title, content: prompt_table,
                    };

                    global_state['saved_prompts'] = saved?.filter?.(it=>it.title!=prompt_title)??[];

                    global_state['saved_prompts'].unshift(new_prompt_obj);

                    global_state['selected_saved_prompt_title'] = prompt_title;

                    console.log(global_state);

                    localStorage?.setItem?.('[gradio][chat-gpt-ui][prompts]', JSON.stringify(global_state['saved_prompts']));

                    return [JSON.stringify(global_state), prompt_title, prompt_title, prompt_table];
                }""")


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
                                _js="""(txt)=>{
                                    console.log(txt);
                                    try {let promise = navigator?.clipboard?.writeText?.(txt);}
                                    catch(error) {console?.log?.(error);};
                                }""",
                            )
                            chat_copy_history_md_btn.click(
                                copy_history, inputs=[real_md_box],
                                _js="""(txt)=>{
                                    console.log(txt);
                                    try {let promise = navigator?.clipboard?.writeText?.(txt);}
                                    catch(error) {console?.log?.(error);};
                                }""",
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
