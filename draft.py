import gradio as gr
# import os
# import sys
# from pathlib import Path
import time

models =[
    "CompVis/stable-diffusion-v1-4",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "stabilityai/stable-diffusion-2-1",
    "stabilityai/stable-diffusion-2-1-base",
    "andite/anything-v4.0",
    "Linaqruf/anything-v3.0",
    "eimiss/EimisAnimeDiffusion_1.0v",
    "nitrosocke/Nitro-Diffusion",
    "wavymulder/portraitplus",
    "22h/vintedois-diffusion-v0-1",
    "dreamlike-art/dreamlike-photoreal-2.0",
    "dreamlike-art/dreamlike-diffusion-1.0",
    "wavymulder/Analog-Diffusion",
    "nitrosocke/redshift-diffusion",
    "claudfuen/photorealistic-fuen-v1",
    "prompthero/openjourney-v2",
    "johnslegers/epic-diffusion",
    "nitrosocke/Arcane-Diffusion",
    "darkstorm2150/Protogen_x5.8_Official_Release",
]


model_functions = {}
model_idx = 1
for model_path in models:
    try:
        model_functions[model_idx] = gr.Interface.load(f"models/{model_path}", live=False, preprocess=True, postprocess=False)
    except Exception as error:
        def the_fn(txt):
            return None
        model_functions[model_idx] = gr.Interface(fn=the_fn, inputs=["text"], outputs=["image"])
    model_idx+=1


def send_it_idx(idx):
    def send_it_fn(prompt):
        output = (model_functions.get(str(idx)) or model_functions.get(str(1)))(prompt)
        return output
    return send_it_fn

def get_prompts(prompt_text):
    return prompt_text

def clear_it(val):
    if int(val) != 0:
        val = 0
    else:
        val = 0
        pass
    return val

def all_task_end(cnt,t_stamp):
    to = t_stamp + 60
    et = time.time()
    if et > to and t_stamp != 0:
        d = gr.update(value=0)
        tog = gr.update(value=1)
        #print(f'to: {to}  et: {et}')
    else:
        if cnt != 0:
            d = gr.update(value=et)
        else:
            d = gr.update(value=0)
        tog = gr.update(value=0)
        #print (f'passing:  to: {to}  et: {et}')
        pass
    return d, tog

def all_task_start():
    print("\n\n\n\n\n\n\n")
    t = time.gmtime()
    t_stamp = time.time()
    current_time = time.strftime("%H:%M:%S", t)
    return gr.update(value=t_stamp), gr.update(value=t_stamp), gr.update(value=0)

def clear_fn():
    nn = len(models)
    return tuple([None, *[None for _ in range(nn)]])



with gr.Blocks(title="SD Models") as my_interface:
    with gr.Column(scale=12):
        # with gr.Row():
        #     gr.Markdown("""- Primary prompt: 你想画的内容(英文单词，如 a cat, 加英文逗号效果更好；点 Improve 按钮进行完善)\n- Real prompt: 完善后的提示词，出现后再点右边的 Run 按钮开始运行""")
        with gr.Row():
            with gr.Column(scale=6):
                primary_prompt=gr.Textbox(label="Prompt")
                # real_prompt=gr.Textbox(label="Real prompt")
            with gr.Column(scale=6):
                # improve_prompts_btn=gr.Button("Improve")
                with gr.Row():
                    run=gr.Button("Run")
                    clear_btn=gr.Button("Clear")
        with gr.Row():
            sd_outputs = {}
            model_idx = 1
            for model_path in models:
                with gr.Column(scale=3, min_width=320):
                    with gr.Box():
                        sd_outputs[model_idx] = gr.Image(label=model_path)
                    pass
                model_idx += 1
                pass
            pass

        with gr.Row(visible=False):
            start_box=gr.Number(interactive=False)
            end_box=gr.Number(interactive=False)
            tog_box=gr.Textbox(value=0,interactive=False)

        start_box.change(
            all_task_end,
            [start_box, end_box],
            [start_box, tog_box],
            every=1,
            show_progress=False)

        run.click(all_task_start, None, [start_box, end_box, tog_box])
        runs_dict = {}
        model_idx = 1
        for model_path in models:
            runs_dict[model_idx] = run.click(model_functions[model_idx], inputs=[primary_prompt], outputs=[sd_outputs[model_idx]])
            model_idx += 1
            pass
        pass

        # improve_prompts_btn_clicked=improve_prompts_btn.click(
        #     get_prompts,
        #     inputs=[primary_prompt],
        #     outputs=[primary_prompt],
        #     cancels=list(runs_dict.values()))
        clear_btn.click(
            clear_fn,
            None,
            [primary_prompt, *list(sd_outputs.values())],
            cancels=[*list(runs_dict.values())])
        tog_box.change(
            clear_it,
            tog_box,
            tog_box,
            cancels=[*list(runs_dict.values())])

my_interface.queue(concurrency_count=600, status_update_rate=1)
my_interface.launch(inline=True, show_api=False)
