+++
title = "R1 系列模型 Chat Template 变更分析与下游解决方案"
date = 2025-02-11T15:24:39+08:00
images = []
tags = []
categories = []
draft = false
+++
DeepSeek-R1-系列开源模型文件 tokenizer_config.json 的 chat_template 对应的 [Jinja 模板](https://jinja.palletsprojects.com/en/stable/) 发生了改变。具体来说，原来的 {'<｜Assistant｜>'}}{% endif %} 变成了 `{'<｜Assistant｜><think>\\n'}}{% endif %}`。造成的结果是，本地部署 DeepSeek-R1-系列模型时，输出仅有 `</think>`，而没有 <think>，也就是说 <think> 标签现在位于提示词中，而不是生成的内容中。
<!--more-->
---
## 原始的：

```json
{
  "add_bos_token": true,
  "add_eos_token": false,
  "bos_token": {
    "__type": "AddedToken",
    "content": "<｜begin▁of▁sentence｜>",
    "lstrip": false,
    "normalized": true,
    "rstrip": false,
    "single_word": false
  },
  "clean_up_tokenization_spaces": false,
  "eos_token": {
    "__type": "AddedToken",
    "content": "<｜end▁of▁sentence｜>",
    "lstrip": false,
    "normalized": true,
    "rstrip": false,
    "single_word": false
  },
  "legacy": true,
  "model_max_length": 16384,
  "pad_token": {
    "__type": "AddedToken",
    "content": "<｜end▁of▁sentence｜>",
    "lstrip": false,
    "normalized": true,
    "rstrip": false,
    "single_word": false
  },
  "sp_model_kwargs": {},
  "unk_token": null,
  "tokenizer_class": "LlamaTokenizerFast",
  "chat_template": "{% if not add_generation_prompt is defined %}{% set add_generation_prompt = false %}{% endif %}{% set ns = namespace(is_first=false, is_tool=false, is_output_first=true, system_prompt='') %}{%- for message in messages %}{%- if message['role'] == 'system' %}{% set ns.system_prompt = message['content'] %}{%- endif %}{%- endfor %}{{bos_token}}{{ns.system_prompt}}{%- for message in messages %}{%- if message['role'] == 'user' %}{%- set ns.is_tool = false -%}{{'<｜User｜>' + message['content']}}{%- endif %}{%- if message['role'] == 'assistant' and message['content'] is none %}{%- set ns.is_tool = false -%}{%- for tool in message['tool_calls']%}{%- if not ns.is_first %}{{'<｜Assistant｜><｜tool▁calls▁begin｜><｜tool▁call▁begin｜>' + tool['type'] + '<｜tool▁sep｜>' + tool['function']['name'] + '
' + 'json' + '\
' + tool['function']['arguments'] + '\
' + '' + '<｜tool▁call▁end｜>'}}{%- set ns.is_first = true -%}{%- else %}{{'
' + '<｜tool▁call▁begin｜>' + tool['type'] + '<｜tool▁sep｜>' + tool['function']['name'] + '
' + 'json' + '\
' + tool['function']['arguments'] + '\
' + '' + '<｜tool▁call▁end｜>'}}{{'<｜tool▁calls▁end｜><｜end▁of▁sentence｜>'}}{%- endif %}{%- endfor %}{%- endif %}{%- if message['role'] == 'assistant' and message['content'] is not none %}{%- if ns.is_tool %}{{'<｜tool▁outputs▁end｜>' + message['content'] + '<｜end▁of▁sentence｜>'}}{%- set ns.is_tool = false -%}{%- else %}{% set content = message['content'] %}{% if '</think>' in content %}{% set content = content.split('</think>')[-1] %}{% endif %}{{'<｜Assistant｜>' + content + '<｜end▁of▁sentence｜>'}}{%- endif %}{%- endif %}{%- if message['role'] == 'tool' %}{%- set ns.is_tool = true -%}{%- if ns.is_output_first %}{{'<｜tool▁outputs▁begin｜><｜tool▁output▁begin｜>' + message['content'] + '<｜tool▁output▁end｜>'}}{%- set ns.is_output_first = false %}{%- else %}{{'
<｜tool▁output▁begin｜>' + message['content'] + '<｜tool▁output▁end｜>'}}{%- endif %}{%- endif %}{%- endfor -%}{% if ns.is_tool %}{{'<｜tool▁outputs▁end｜>'}}{% endif %}{% if add_generation_prompt and not ns.is_tool %}{{'<｜Assistant｜><think>
'}}{% endif %}"
}
```

## 现在的：

```json
{
  "add_bos_token": true,
  "add_eos_token": false,
  "bos_token": {
    "__type": "AddedToken",
    "content": "<｜begin▁of▁sentence｜>",
    "lstrip": false,
    "normalized": true,
    "rstrip": false,
    "single_word": false
  },
  "clean_up_tokenization_spaces": false,
  "eos_token": {
    "__type": "AddedToken",
    "content": "<｜end▁of▁sentence｜>",
    "lstrip": false,
    "normalized": true,
    "rstrip": false,
    "single_word": false
  },
  "legacy": true,
  "model_max_length": 16384,
  "pad_token": {
    "__type": "AddedToken",
    "content": "<｜end▁of▁sentence｜>",
    "lstrip": false,
    "normalized": true,
    "rstrip": false,
    "single_word": false
  },
  "sp_model_kwargs": {},
  "unk_token": null,
  "tokenizer_class": "LlamaTokenizerFast",
  "chat_template": "{% if not add_generation_prompt is defined %}{% set add_generation_prompt = false %}{% endif %}{% set ns = namespace(is_first=false, is_tool=false, is_output_first=true, system_prompt='') %}{%- for message in messages %}{%- if message['role'] == 'system' %}{% set ns.system_prompt = message['content'] %}{%- endif %}{%- endfor %}{{bos_token}}{{ns.system_prompt}}{%- for message in messages %}{%- if message['role'] == 'user' %}{%- set ns.is_tool = false -%}{{'<｜User｜>' + message['content']}}{%- endif %}{%- if message['role'] == 'assistant' and message['content'] is none %}{%- set ns.is_tool = false -%}{%- for tool in message['tool_calls']%}{%- if not ns.is_first %}{{'<｜Assistant｜><｜tool▁calls▁begin｜><｜tool▁call▁begin｜>' + tool['type'] + '<｜tool▁sep｜>' + tool['function']['name'] + '\\n' + '```json' + '\\n' + tool['function']['arguments'] + '\\n' + '```' + '<｜tool▁call▁end｜>'}}{%- set ns.is_first = true -%}{%- else %}{{'\\n' + '<｜tool▁call▁begin｜>' + tool['type'] + '<｜tool▁sep｜>' + tool['function']['name'] + '\\n' + '```json' + '\\n' + tool['function']['arguments'] + '\\n' + '```' + '<｜tool▁call▁end｜>'}}{{'<｜tool▁calls▁end｜><｜end▁of▁sentence｜>'}}{%- endif %}{%- endfor %}{%- endif %}{%- if message['role'] == 'assistant' and message['content'] is not none %}{%- if ns.is_tool %}{{'<｜tool▁outputs▁end｜>' + message['content'] + '<｜end▁of▁sentence｜>'}}{%- set ns.is_tool = false -%}{%- else %}{% set content = message['content'] %}{% if '</think>' in content %}{% set content = content.split('</think>')[-1] %}{% endif %}{{'<｜Assistant｜>' + content + '<｜end▁of▁sentence｜>'}}{%- endif %}{%- endif %}{%- if message['role'] == 'tool' %}{%- set ns.is_tool = true -%}{%- if ns.is_output_first %}{{'<｜tool▁outputs▁begin｜><｜tool▁output▁begin｜>' + message['content'] + '<｜tool▁output▁end｜>'}}{%- set ns.is_output_first = false %}{%- else %}{{'\\n<｜tool▁output▁begin｜>' + message['content'] + '<｜tool▁output▁end｜>'}}{%- endif %}{%- endif %}{%- endfor -%}{% if ns.is_tool %}{{'<｜tool▁outputs▁end｜>'}}{% endif %}{% if add_generation_prompt and not ns.is_tool %}{{'<｜Assistant｜><think>\\n'}}{% endif %}"
}
```



## 解决方案1

可以将 chat_template 中的 `<think>\\n` 去掉，也就是：

```python
template = tokenizer.chat_template
template = template.replace("<think>\\n", "")  # 去掉末尾的 <think>\\n
tokenizer.chat_template = template  # 设置新的模板
```

但是[官方的说法](https://huggingface.co/deepseek-ai/DeepSeek-R1/commit/f7361cd9ff99396dbf6bd644ad846015e59ed4fc)是：


Additionally, we have observed that the DeepSeek-R1 series models tend to bypass thinking pattern (i.e., outputting <think>\n\n</think>) when responding to certain queries, which can adversely affect the model's performance. To ensure that the model engages in thorough reasoning, we recommend enforcing the model to initiate its response with <think>\n at the beginning of every output.

此外，我们观察到 DeepSeek-R1 系列模型在回答某些查询时往往会绕过思考模式（即输出 <think>\n\n</think> ），这可能会对模型性能产生不利影响。为确保模型进行彻底推理，我们建议强制模型在每个输出的开头以 <think>\n 开始其响应。


## 解决方案2

如果不方便修改 deepseek_r1_reasoning_parser.py，可以在 vllm serve 命令中指定 chat template。

具体而言，首先需要创建一个 template_deepseek_r1.jinja 文件，写入 chat template：

*上述 template 是官方模型仓库中更新前的 template*

之后在 vllm serve 命令中指定该 template 即可（--chat-template ./template_deepseek_r1.jinja）：

```bash
vllm serve deepseek-ai/DeepSeek-R1-Distill-Llama-70B \
  --tensor-parallel-size 4 \
  --max-model-len 32768 \
  --enforce-eager \
  --enable-reasoning \
  --reasoning-parser deepseek_r1 \
  --chat-template ./template_deepseek_r1.jinja
```

## 解决方案3

最简单的解决方法是，直接看[代码差异](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/commit/3865e12a1eb7cbd641ab3f9dfc28c588c6b0c1e9)，修改下模型的文件，重新加载模型就可以了。



参考资料

[本地部署DeepSeek-R1-Distill-Qwen-32B,输出仅有，没有 · Issue #352 · deepseek-ai/DeepSeek-R1](https://github.com/deepseek-ai/DeepSeek-R1/issues/352)

[Update tokenizer_config.json · deepseek-ai/DeepSeek-R1-Distill-Qwen-32B at 3865e12](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/commit/3865e12a1eb7cbd641ab3f9dfc28c588c6b0c1e9#d2h-846292)

