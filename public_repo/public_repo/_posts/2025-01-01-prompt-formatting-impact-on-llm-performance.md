---
title: "纯文本、Markdown、YAML和JSON四种提示词样式对模型输出的影响实证"
date: 2025-01-01 11:06:11 +0800
---

{% raw %}
我之前的项目实践总是把所有的提示词都设计成Markdown格式，因为我认为这样不仅对大模型友好，对我使用Typora编辑特别长的提示词也十分友好,而且直到现在[GPT官方示例](https://platform.openai.com/docs/guides/prompt-generation)也是这样做的。

后来看到[宝玉](https://x.com/dotey)分享的[V0提示词](https://baoyu.io/blog/v0-system-prompt-2024)，我的直觉告诉我应该试一试XML ，因为我用的提示词生成工具（[dify](https://docs.dify.ai/zh-hans)一个内置功能）都是使用这个格式。后来我也频繁使用XML格式，但是到底哪个更好呢？我觉得这篇实证论文挺有参考意义的，因为它给了我使用JSON格式尝试的可能，可惜的是没有XML格式的对比。
<!--more-->
介绍下Does Prompt Formatting Have Any Impact on LLM Performance这篇论文，是由微软和MIT发表的。 结论是提示的格式对基于GPT的模型性能有显著影响，不同格式的效果在不同任务中表现不一致，没有一个格式在所有任务中都是最优的。
## 实验设计

- **数据集**：涵盖自然语言到自然语言、自然语言到代码、代码到代码三类任务，涉及 MMLU、HumanEval 等 6 个基准数据集。

- **提示词设计**：采用纯文本、Markdown、YAML 和 JSON 四种输入格式，保证不同格式提示内容相同，仅结构和语法有差异。

- **模型选择**：基于 Azure 平台的 OpenAI 的 GPT-3.5 和 GPT - 4 系列模型，包括不同上下文窗口和版本。

  

### 数据集

1. 自然语言到自然语言（NL2NL）
   - **Massive Multitask Language Understanding（MMLU）**：涵盖 57 个学科，包括 20 个 STEM 学科、13 个人文学科、12 个社会科学学科和 12 个其他学科。每个学科至少有 100 道选择题，测试世界知识和问题解决能力。使用每个学科含 5 道题的开发集作为少样本示例，用含 14,079 道不同难度问题的测试集评估模型性能，采用准确率作为评估指标。
   - **NER Finance**：来自 OpenAI Evals 框架，数据样本为一到一段长度的金融文档文本。任务是提取文档中的所有实体，评估标准是 LLM 是否按顺序输出每个实体。从该数据集中随机抽取 500 个样本进行实验。
2. 自然语言到代码（NL2Code）
   - **HumanEval**：由一系列 Python 编程问题组成，每个问题包含函数签名、描述问题的文档字符串以及正确实现必须通过的一组单元测试。采用 pass@1 指标评估，即检查生成的代码能否一次通过给定的单元测试，使用了数据集中全部 164 个样本。
   - **FIND**：是自然语言到代码生成任务，LLM 会得到一个未知 Python 函数的 5 组输入和输出，任务是逆向工程原始 Python 代码。通过将测试用例在真实函数上的输出与 LLM 生成函数的输出进行比较来评估，使用 “strings” 类函数，共 500 个函数。为 LLM 提供每个函数的 5 对输入和输出，从指定数据集中随机抽样选择示例，采用字符串指示指标衡量生成函数代码通过的测试用例数量。
3. 代码到代码（Code2Code）
   - **CODEXGLUE**：旨在解决代码智能领域缺乏多样化基准的问题，提供包括代码翻译在内的多样化任务。实验使用 Java 和 C# 的并行代码，采用 BLEU 分数评估 LLMs 将一种编程语言代码翻译成另一种语言的能力，测试集包含 1000 对 Java 和 C# 并行代码。
   - **HumanEval - X**：用于评估代码生成模型的多语言能力，包含 820 个高质量人工编写的数据样本，每个样本都有测试用例，支持多种编程语言。实验聚焦 Java 到 Python 的代码翻译任务，结合 “声明” 和 “规范解决方案” 得到相应语言的整体函数，同样采用 BLEU 分数衡量性能。

### 提示词设计
![image-20250101111412751](/images/20250102-prompt-formatting-impact-on-llm-performance.assets/image-20250101111412751.png)

### 模型

该研究使用了 OpenAI 的 GPT - 3.5 和 GPT - 4 系列模型，并通过 Azure 平台开展实验，具体模型信息如下：

1. GPT - 3.5 系列

- **gpt - 3.5 - turbo - 0613**
- **gpt - 3.5 - turbo - 16k - 0613**：该模型的上下文窗口大小为 16k

1. GPT - 4 系列

- **gpt4 - 32k - 0613**：该模型上下文窗口为 32k，用于测试模型在不同提示格式下的表现。
- **gpt - 4 - 1106 - preview**：是较新、速度更快的变体，拥有 128k 的上下文窗口。

## 实验

### 文本示例

#### Plain text

```markdown
System:
You are a annotator working for large financial data company and are tasked with extracting named entities from financial documents who follows strict guidelines for quality and formatting. The following sentence is from a financial document. List the named entities in the order they appear in the sentence. If an entity appears multiple times, list it multiple times. Entities should be stated in the format NAME - TYPE where TYPE can be PERSON, ORGANIZATION, or LOCATION. State your final answer as a comma-separated list of entities enclosed in square brackets. Example: [BANK - ORGANIZATION, burrows - PERSON]. If there are no entities present, state your final answer as []. Provide your chain of thought first and then respond with your final answer. Here is an example: [ILL EXAMPLE INPUT] [ILL EXAMPLE SOLUTION]
User:
[EMPTY]
```

#### Markdown

```markdown
System:
## Persona
- You are a annotator working for large financial data company are tasked with extracting named entities from financial documents who follows strict guidelines for quality and formatting.

## Instructions
- You will be given a sentence from a financial document.
- List the named entities in the order they appear in the sentence.
- If an entity appears multiple times, list it multiples times.
- Provide your chain of thought first and then respond with your final answer.

## Output Format
- Entities should be stated in the format NAME - TYPE where TYPE can be PERSON, ORGANIZATION, or LOCATION.
- State your final answer as a comma-separated list of entities enclosed in square brackets. Example: [Bank - ORGANIZATION, Borrower - PERSON].
- If there are no entities found, state your final answer as 'No entities found'.

## Example
### DOCUMENT
{ICL EXAMPLE INPUT}

### Solution
{ICL EXAMPLE SOLUTION}

User:
### DOCUMENT
{INPUT}
```

#### YAML

```markdown
System:
Persona:
  Description: You are a annotator working for large financial data company are tasked with extracting named entities from financial documents who follows strict guidelines for quality and formatting.

Instructions:
  - You will be given a sentence from a financial document.
  - List the named entities in the order they appear in the sentence.
  - If an entity appears multiple times, list it multiples times.
  - Provide your chain of thought first and then respond with your final answer.

Output_Format:
  Entities should be stated in the format NAME - TYPE where TYPE can be PERSON, ORGANIZATION, or LOCATION. State your final answer as a comma-separated list of entities enclosed in square brackets.

Examples:
  - Document: {ICL EXAMPLE INPUT}
  - Solution: {ICL EXAMPLE SOLUTION}

User:
Task:
  - Document: {INPUT}
```

#### JSON

```markdown
System: {
  "Persona": "You are a annotator working for large financial data company are tasked with extracting named entities from financial documents who follows strict guidelines for quality and formatting.",
  "Instructions": [
    "You will be given a sentence from a financial document.",
    "List the named entities in the order they appear in the sentence.",
    "If an entity appears multiple times, list it multiples times.",
    "Provide your chain of thought first and then respond with your final answer."
  ],
  "OutputFormat": "Entities should be stated in the format NAME - TYPE where TYPE can be PERSON, ORGANIZATION, or LOCATION. State your final answer as a comma-separated list of entities enclosed in square brackets. Example: [Bank - ORGANIZATION, Borrower - PERSON]. If there are no entities found, state your final answer as 'No entities found'.",
  "Example": "{ICL EXAMPLE INPUT}\n{ICL EXAMPLE SOLUTION}"
}

User: {
  "Task": "{INPUT}"
}
```

### 数据集得分

#### (MMLU Benchmark)

| Model     | GPT-35-turbo-0613 | GPT-35-turbo-16k-0613 | GPT-4-1106-preview | GPT-4-32k-0613  |
| --------- | ----------------- | --------------------- | ------------------ | --------------- |
| Plaintext | 54.464 ± 18.300   | 54.184 ± 19.066       | 81.005 ± 12.979    | 80.638 ± 13.172 |
| Markdown  | 50.021 ± 17.144   | 50.686 ± 17.436       | 81.252 ± 12.932    | 81.349 ± 13.158 |
| YAML      | 56.355 ± 16.792   | 55.901 ± 16.347       | 80.758 ± 13.000    | 81.162 ± 13.110 |
| JSON      | 59.705 ± 16.594   | 59.405 ± 17.092       | 73.918 ± 13.580    | 77.800 ± 13.725 |

#### (NER finance benchmark)

| Model     | GPT-35-turbo-0613 | GPT-35-turbo-16k-0613 | GPT-4-1106-preview | GPT-4-32k-0613 |
| --------- | ----------------- | --------------------- | ------------------ | -------------- |
| Plaintext | 37.20 ± 6.59      | 36.80 ± 6.54          | 49.40 ± 7.86       | 47.20 ± 7.67   |
| Markdown  | 28.00 ± 5.31      | 30.00 ± 5.61          | 51.40 ± 8.01       | 51.60 ± 8.03   |
| YAML      | 24.60 ± 4.78      | 21.80 ± 4.31          | 53.80 ± 8.18       | 53.20 ± 8.14   |
| JSON      | 28.40 ± 5.37      | 31.00 ± 5.76          | 50.80 ± 7.97       | 52.40 ± 8.08   |

#### (HumanEval benchmark)

| Model     | GPT-35-turbo-0613 | GPT-35-turbo-16k-0613 | GPT-4-1106-preview | GPT-4-32k-0613 |
| --------- | ----------------- | --------------------- | ------------------ | -------------- |
| Plaintext | 40.24 ± 3.98      | 37.20 ± 3.77          | 82.93 ± 4.39       | 76.22 ± 4.76   |
| Markdown  | 54.27 ± 4.70      | 48.17 ± 4.44          | 86.59 ± 4.06       | 75.61 ± 4.78   |
| YAML      | 42.68 ± 4.14      | 37.20 ± 3.77          | 85.37 ± 4.18       | 68.29 ± 4.92   |
| JSON      | 59.76 ± 4.85      | 57.93 ± 4.81          | 86.59 ± 4.06       | 21.95 ± 2.48   |

#### (FIND benchmark)

| Model     | gpt-35-turbo-16k-0613 | gpt-35-turbo-0613 | gpt-4-32k-0613 | gpt-4-1106-preview |
| --------- | --------------------- | ----------------- | -------------- | ------------------ |
| plaintext | 15.75±0.142           | 15.9±0.143        | 21.87±0.164    | 20.08±0.161        |
| markdown  | 5.03±0.092            | 5.19±0.089        | 17.42±0.154    | 20.68±0.165        |
| json      | 14.46±0.138           | 14.33±0.144       | 21.15±0.162    | 20.19±0.156        |
| yaml      | 13.06±0.139           | 13.49±0.138       | 21.6±0.163     | 20.28±0.16         |

#### (HumanEval-X benchmark)

| Model     | GPT-35-turbo-0613 | GPT-35-turbo-16k-0613 | GPT-4-1106-preview | GPT-4-32k-0613 |
| --------- | ----------------- | --------------------- | ------------------ | -------------- |
| Plaintext | 62.95 ± 15.64     | 62.92 ± 15.66         | 64.95 ± 15.52      | 63.86 ± 15.83  |
| Markdown  | 69.82 ± 16.26     | 69.84 ± 16.23         | 70.70 ± 17.44      | 71.65 ± 18.10  |
| YAML      | 69.05 ± 17.24     | 69.05 ± 17.24         | 71.16 ± 16.11      | 71.41 ± 17.96  |
| JSON      | 68.85 ± 16.13     | 68.85 ± 16.13         | 72.30 ± 15.97      | 72.39 ± 16.46  |

#### Java to C# 

| Model     | GPT-35-turbo-0613 | GPT-35-turbo-16k-0613 | GPT-4-1106-preview | GPT-4-32k-0613 |
| --------- | ----------------- | --------------------- | ------------------ | -------------- |
| Plaintext | 66.46 ± 16.04     | 66.46 ± 16.04         | 67.16 ± 16.77      | 68.19 ± 13.14  |
| Markdown  | 78.10 ± 18.75     | 78.10 ± 18.75         | 74.16 ± 16.77      | 76.95 ± 18.33  |
| YAML      | 78.28 ± 18.92     | 78.30 ± 18.92         | 70.75 ± 16.08      | 76.41 ± 18.00  |
| JSON      | 78.37 ± 18.93     | 78.40 ± 18.93         | 74.16 ± 16.77      | 76.86 ± 18.31  |

#### C# to Java 

| Model     | GPT-35-turbo-0613 | GPT-35-turbo-16k-0613 | GPT-4-1106-preview | GPT-4-32k-0613 |
| --------- | ----------------- | --------------------- | ------------------ | -------------- |
| Plaintext | 68.81 ± 17.65     | 68.89 ± 17.64         | 67.93 ± 17.72      | 68.11 ± 16.29  |
| Markdown  | 76.19 ± 18.40     | 76.12 ± 18.37         | 74.80 ± 20.14      | 80.36 ± 20.52  |
| YAML      | 75.47 ± 20.16     | 75.39 ± 20.08         | 72.09 ± 17.98      | 78.49 ± 21.23  |
| JSON      | 77.49 ± 19.51     | 77.49 ± 19.50         | 75.00 ± 17.66      | 83.05 ± 18.60  |

我用Claude分析了这个图表：

##### 整体表现

- 不同格式的效果在不同任务中表现不一致，没有一个格式在所有任务中都是最优的

##### 按任务类型分析

###### 自然语言到自然语言任务(MMLU, NER Finance):

- MMLU测试中，对于GPT-3.5，JSON格式表现最好(约60%)，对于GPT-4，纯文本和Markdown格式略优(约81%)
- 在NER Finance任务中，对于GPT-4，YAML格式表现最好(约53%)

###### 自然语言到代码任务(HumanEval, FIND):

- 在HumanEval中，对于GPT-3.5，JSON格式效果最好(约58%)
- 对于GPT-4，Markdown和JSON格式效果相当(约86%)
- 在FIND任务中，纯文本格式普遍表现较好

###### 代码到代码任务(HumanEval-X, Java/C#转换):

- 在代码转换任务中，结构化格式(Markdown/YAML/JSON)普遍比纯文本格式表现更好
- 特别是在Java和C#的相互转换中，结构化格式的优势更为明显(性能提升约10%)



## 参考

1. [Does Prompt Formatting Have Any Impact on LLM Performance? | Cool Papers - Immersive Paper Discovery](https://papers.cool/arxiv/2411.10541)
2. [[2411.10541\] Does Prompt Formatting Have Any Impact on LLM Performance?](https://arxiv.org/abs/2411.10541)
3. https://baoyu.io/blog/v0-system-prompt-2024
4. https://x.com/dotey
5. https://platform.openai.com/docs/guides/prompt-generation
6. https://docs.dify.ai/zh-hans
{% endraw %}
