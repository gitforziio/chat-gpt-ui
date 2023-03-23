
saved_prompts_refresh_btn__click_js = """(global_state_json, saved_prompts)=>{
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
}"""


selected_saved_prompt_title__change_js = """(global_state_json, selected_saved_prompt_title)=>{
    if(global_state_json=="") {global_state_json=null;};
    const global_state = JSON.parse(global_state_json??"{ }")??{ };
    const found = (global_state?.['saved_prompts']??[]).find(it=>it?.title==selected_saved_prompt_title);
    return [JSON.stringify(global_state), found?.title??'', found?.content??{data:[], headers:["role", "content"]}];
}"""


saved_prompts_delete_btn__click_js = """(global_state_json, saved_prompts, prompt_title, prompt_table)=>{
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
}"""


saved_prompts_save_btn__click_js = """(global_state_json, saved_prompts, prompt_title, prompt_table)=>{
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
}"""


copy_prompt__click_js = """(prompt_title, prompt_table)=>{
    try {
        const txt = JSON.stringify({
            title: prompt_title,
            content: prompt_table,
        }, null, 2);
        console.log(txt);
        const promise = navigator?.clipboard?.writeText?.(txt);
    } catch(error) {console?.log?.(error);};
    return [prompt_title, prompt_table];
}"""


paste_prompt__click_js = """async (prompt_title, prompt_table)=>{
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
}"""


chat_copy_history_btn__click_js = """(txt)=>{
    console.log(txt);
    try {let promise = navigator?.clipboard?.writeText?.(txt);}
    catch(error) {console?.log?.(error);};
}"""


chat_copy_history_md_btn__click_js = """(txt)=>{
    console.log(txt);
    try {let promise = navigator?.clipboard?.writeText?.(txt);}
    catch(error) {console?.log?.(error);};
}"""


api_key_refresh_btn__click_js = """()=>{
    const the_api_key = localStorage?.getItem?.('[gradio][chat-gpt-ui][api_key_text]') ?? '';
    return the_api_key;
}"""


api_key_save_btn__click_js = """(api_key_text)=>{
    localStorage.setItem('[gradio][chat-gpt-ui][api_key_text]', api_key_text);
    return api_key_text;
}"""

