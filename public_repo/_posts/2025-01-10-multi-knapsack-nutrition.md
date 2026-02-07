---
title: "用多重背包算法解决大模型长距离依赖和数字约束遗忘问题"
date: 2025-01-10 20:53:39 +0800
---

{% raw %}
最近在做医疗诊断+食谱生成的一个项目，遇到了一个棘手难题：数值敏感度不足，长距离依赖和约束遗忘。 我们需要利用大模型根据患者病情自动生成个性化食谱，首先生成一日营养目标摄入总量，然后生成早餐，中餐，晚餐各个食材的设定目标，结果是各个食材营养摄入总和总是超过总量预设值。LLM虽能生成流畅食谱，却难以精确控制营养素摄入量，为解决此问题，我们提出将食谱生成转化为多重背包问题，利用动态规划算法，在满足每日营养目标（背包容量）的约束下，选择最优菜品组合（价值最大化）。通过检索和约束优化，替代LLM的直接生成。

<!--more-->
---


## 一、 项目目标

我们的项目目标是构建一个基于大型语言模型 (LLM) 的智能菜谱生成系统，根据患者的健康状况，自动生成个性化、符合特定营养需求的每日菜谱。具体来说，系统需要能够：

- 理解患者病情评估结论和饮食建议： 系统需要能够解析输入的患者病情信息，包括各项生理指标、疾病诊断以及医生给出的饮食建议。
- 确定每日营养目标摄入总量： 基于病情信息和饮食建议，系统需要自动计算出患者每日应摄入的能量、蛋白质、钾、磷、钠和液体的总量。
- 生成每日详细菜谱： 系统需要生成包含早餐、午餐、晚餐和加餐（如有需要）的详细菜谱，并明确列出每道菜的食材、份量以及对应的营养成分含量（蛋白质、钾、钠、磷等）。
- 确保菜谱符合营养目标：  最重要的是，生成的每日菜谱中各项营养素的总摄入量必须符合预先设定的每日营养目标，以确保其科学性和安全性，满足患者的特定健康需求。

## 二、 大模型生成示例

我们使用 LLM（Qwen2-72B） 进行菜谱生成，输入的是患者的病情评估结论和饮食建议。以下是一个简化的示例：

输入（病情评估结论及饮食建议）：

```
病情评估结论
患者目前处于慢性肾脏病（CKD）5期（eGFR值: 无法计算），BMI值为26.2，超重，且存在高血压、高尿酸血症、高钾血症和低白蛋白血症等多种慢性疾病。

病情分析与饮食建议
...（省略）...
营养目标
能量：1500 kcal/day
蛋白质：35 g/day
钾：2000 mg/day
磷：600 mg/day
钠：1500 mg/day（约3.75 g盐）
液体：1000-1500 mL/day
```

模型初步生成的菜谱（存在问题）：

```
第一天
早餐

鸡蛋：1个（水煮）
营养成分：蛋白质6 g，钾60 mg，钠70 mg，磷80 mg
全麦面包：2片（约50 g）
营养成分：蛋白质4 g，钾150 mg，钠150 mg，磷70 mg
无糖豆浆：200 mL
营养成分：蛋白质6 g，钾150 mg，钠20 mg，磷30 mg
午餐

清蒸鸡胸肉：100 g
营养成分：蛋白质31 g，钾250 mg，钠70 mg，磷180 mg
西兰花：100 g（焯水后炒）
营养成分：蛋白质2 g，钾150 mg，钠30 mg，磷50 mg
米饭：100 g（约半碗）
营养成分：蛋白质2 g，钾15 mg，钠5 mg，磷30 mg
晚餐

豆腐：100 g（清蒸）
营养成分：蛋白质8 g，钾130 mg，钠10 mg，磷120 mg
炒小白菜：100 g（焯水后炒）
营养成分：蛋白质2 g，钾150 mg，钠30 mg，磷50 mg
小米粥：200 g
营养成分：蛋白质2 g，钾50 mg，钠5 mg，磷30 mg
加餐

苹果：1个（小，约100 g）
营养成分：蛋白质0.5 g，钾100 mg，钠1 mg，磷10 mg

... (第二天菜谱省略) ...
```

## 三、 遇到的难题

1. 数值敏感度不足：
   *   问题： LLM 难以精确控制每种食材的份量及其对应的营养素含量。虽然模型能生成看似合理的菜谱，但各项营养素的实际总摄入量往往与预设的每日目标存在较大偏差。
   *   示例说明： 例如，在上面的示例中，模型虽然指定了每日蛋白质摄入量为 35g，但仅第一天的早餐、午餐的蛋白质摄入量就已经超过49g（6+4+6+31+2+2=51），模型没有进行总量的约束，只保证了语义上的通顺。
2. 长距离依赖和约束遗忘：
   *   问题描述： 随着生成内容的增加，模型容易“遗忘”最初设定的每日营养目标。在生成后续的菜谱内容时，模型可能无法有效控制之前已生成的菜谱中的营养素累积量，导致最终结果超出限制。
   *   问题原因： LLM 的注意力机制在处理长文本时能力有限，难以始终将注意力放在所有相关的约束条件上，缺乏对已生成内容的整体感知和总结能力。
   *   示例说明： 比如在指定了一天 35g 蛋白质的摄入，但是在生成了一天中的前两餐之后，模型可能已经忘记了 35g 的限制，继续生成了高蛋白质摄入的第三餐。
3. 复杂约束的推理能力不足：
   *   问题描述： 我们的场景涉及多种营养素的限制（能量、蛋白质、钾、磷、钠、液体），这些约束条件相互关联，需要模型进行一定的逻辑推理才能生成符合要求的菜谱。但 LLM 在处理这种复杂的多约束推理任务时表现不佳。
   *   问题原因： LLM 主要学习到的是隐式的知识表示，难以进行显式的逻辑推理和数值计算，缺乏规划能力。
   *   示例说明： 例如，模型可能难以在限制蛋白质摄入的同时，兼顾低钾、低磷、低钠的要求。因为某些高蛋白食物可能同时含有较高的钾或磷，模型需要进行权衡和选择，但 LLM 难以处理这种复杂的约束关系。

## 四、 初步解决方法

我们不再直接让 LLM 从零开始“创造”菜谱，而是将其转变为背包问题。一个检索式 + 约束优化的问题。具体来说，我们将问题分解为以下几个步骤：

### 具体步骤

- 将每个食物（鸡蛋、面包等）视为一个独立的背包问题。其营养成分（能量、蛋白质、钾、磷、钠、液体）视为物品的“重量”。
- 使用动态规划求解算法，在满足当前餐次营养素上限（背包容量）的前提下，选择“价值”总和最高的菜品组合。
- 关键： 在选择菜品时，需要考虑之前餐次已摄入的营养素总量，动态调整当前餐次的营养素上限。

### 问题求解

- 1.多重背包问题： 每个餐次都是一个多重背包问题，因为我们需要考虑多种营养素（能量、蛋白质、钾、磷、钠、液体）的限制。

- 2.动态规划算法： 可以使用动态规划算法来求解多重背包问题。具体步骤如下：

  - 2.1 定义状态：

    ```
      dp[i][j1][j2][j3][j4][j5][j6] 表示考虑前 i 个菜品，在能量不超过 j1，蛋白质不超过 j2，钾不超过 j3，磷不超过 j4，钠不超过 j5，液体不超过 j6 的情况下的最大价值。
      ```

  - 2.2 状态转移方程：对于每个菜品，可以选择放入背包或不放入背包。

    - 2.2.1 不放入背包：

      ```
        dp[i][j1][j2][j3][j4][j5][j6] = dp[i-1][j1][j2][j3][j4][j5][j6]
        ```

    - 2.2.2 放入背包：

    ```
        dp[i][j1][j2][j3][j4][j5][j6] = max(dp[i][j1][j2][j3][j4][j5][j6], dp[i-1][j1-w1][j2-w2][j3-w3][j4-w4][j5-w5][j6-w6] + value)
    ```

         其中 w1, w2, w3, w4, w5, w6 分别表示第 i 个菜品的能量、蛋白质、钾、磷、钠、液体含量，value 表示第 i 个菜品的价值。

  - 2.3 边界条件：

    ```
      dp[0][...][...] = 0
      ```

         最终结果：

      ```
        dp[n][energy_limit][protein_limit][potassium_limit][phosphorus_limit][sodium_limit][liquid_limit]
    ```

         其中 n 表示菜品数量，*_limit 表示各营养素的上限。

## 附录

### demo代码示例

```python
def multi_dimensional_knapsack(items, limits):
    """
    多维度背包问题解决方案
    """
    n = len(items)  # 物品数量
    dimensions = len(limits)  # 维度数量

    # 1. 创建多维dp数组
    dp = {}
    # 初始化：加入零状态
    dp[tuple([0] * dimensions)] = 0  # 添加这一行来处理初始状态

    def get_dp_value(state):
        """获取dp值，不存在则返回0"""
        return dp.get(state, 0)

    # 2. 实现状态转移
    for i in range(n):  # 遍历每个物品
        new_states = {}

        # 获取当前物品的各维度值
        current_item = items[i]
        item_values = [
            current_item['energy'],
            current_item['protein'],
            current_item['potassium'],
            current_item['phosphorus'],
            current_item['sodium'],
            current_item['liquid']
        ]

        # 遍历当前已存在的所有状态
        current_states = list(dp.items())  # 转换为列表避免运行时修改字典
        for state, value in current_states:
            # 检查加入当前物品是否超出限制
            can_add = True
            new_state = []
            for dim in range(dimensions):
                new_value = state[dim] + item_values[dim]
                if new_value > limits[dim]:
                    can_add = False
                    break
                new_state.append(new_value)

            if can_add:
                new_state_tuple = tuple(new_state)
                # 更新状态：选择当前物品
                new_value = value + current_item['value']
                if new_value > get_dp_value(new_state_tuple):
                    new_states[new_state_tuple] = new_value

        # 将新状态合并到dp中
        dp.update(new_states)

    # 如果dp为空，说明没有可行解
    if not dp:
        return []

    # 3. 回溯找出选择的物品
    selected_items = []
    # 找出价值最大的可行状态
    max_value = -1
    best_state = None
    for state, value in dp.items():
        if value > max_value:
            max_value = value
            best_state = state

    if best_state is None:
        return []

    # 回溯过程
    current_state = best_state
    remaining_value = dp[current_state]

    for i in range(n - 1, -1, -1):
        item = items[i]
        item_values = [
            item['energy'],
            item['protein'],
            item['potassium'],
            item['phosphorus'],
            item['sodium'],
            item['liquid']
        ]

        # 检查是否选择了当前物品
        previous_state = []
        for dim in range(dimensions):
            previous_state.append(current_state[dim] - item_values[dim])

        previous_state_tuple = tuple(previous_state)
        if (all(v >= 0 for v in previous_state) and
                get_dp_value(previous_state_tuple) == remaining_value - item['value']):
            selected_items.append(item)
            current_state = previous_state_tuple
            remaining_value = dp[current_state]

    return selected_items


# 测试
if __name__ == '__main__':
    items = [
        {
            'name': '鸡蛋',
            'energy': 70,  # 70千卡
            'protein': 6,  # 6克蛋白质
            'potassium': 100,  # 100毫克钾
            'phosphorus': 80,  # 80毫克磷
            'sodium': 70,  # 70毫克钠
            'liquid': 0,  # 0毫升液体
            'value': 5  # 价值评分
        },
        {
            'name': '牛奶',
            'energy': 120,  # 120千卡
            'protein': 8,  # 8克蛋白质
            'potassium': 150,  # 150毫克钾
            'phosphorus': 90,  # 90毫克磷
            'sodium': 50,  # 50毫克钠
            'liquid': 200,  # 200毫升液体
            'value': 4  # 价值评分
        },
        {
            'name': '鸡胸肉',
            'energy': 165,  # 165千卡
            'protein': 31,  # 31克蛋白质
            'potassium': 250,  # 250毫克钾
            'phosphorus': 200,  # 200毫克磷
            'sodium': 75,  # 75毫克钠
            'liquid': 0,  # 0毫升液体
            'value': 8  # 价值评分
        },
        {
            'name': '全麦面包',
            'energy': 150,  # 150千卡
            'protein': 4,  # 4克蛋白质
            'potassium': 80,  # 80毫克钾
            'phosphorus': 60,  # 60毫克磷
            'sodium': 180,  # 180毫克钠
            'liquid': 0,  # 0毫升液体
            'value': 3  # 价值评分
        },
        {
            'name': '香蕉',
            'energy': 90,  # 90千卡
            'protein': 1,  # 1克蛋白质
            'potassium': 350,  # 350毫克钾
            'phosphorus': 20,  # 20毫克磷
            'sodium': 1,  # 1毫克钠
            'liquid': 0,  # 0毫升液体
            'value': 2  # 价值评分
        }
    ]

    limits = [
        1500,  # 能量上限（千卡）
        15,  # 蛋白质上限（克）
        2000,  # 钾上限（毫克）
        800,  # 磷上限（毫克）
        2300,  # 钠上限（毫克）
        1500  # 液体上限（毫升）
    ]

    result = multi_dimensional_knapsack(items, limits)

    # 打印结果
    print("选择的食物：")
    total_values = [0] * len(limits)
    total_value = 0
    for item in result:
        print(f"- {item['name']}")
        total_values[0] += item['energy']
        total_values[1] += item['protein']
        total_values[2] += item['potassium']
        total_values[3] += item['phosphorus']
        total_values[4] += item['sodium']
        total_values[5] += item['liquid']
        total_value += item['value']

    print("\n总计：")
    print(f"能量: {total_values[0]}/{limits[0]} 千卡")
    print(f"蛋白质: {total_values[1]}/{limits[1]} 克")
    print(f"钾: {total_values[2]}/{limits[2]} 毫克")
    print(f"磷: {total_values[3]}/{limits[3]} 毫克")
    print(f"钠: {total_values[4]}/{limits[4]} 毫克")
    print(f"液体: {total_values[5]}/{limits[5]} 毫升")
    print(f"总价值: {total_value}")

```

### 返回示例1

```
limits = [
1500,  # 能量上限（千卡）
15,  # 蛋白质上限（克）
2000,  # 钾上限（毫克）
800,  # 磷上限（毫克）
2300,  # 钠上限（毫克）
1500  # 液体上限（毫升）
]
选择的食物：
- 香蕉
- 牛奶
- 鸡蛋

总计：
能量: 280/1500 千卡
蛋白质: 15/15 克
钾: 600/2000 毫克
磷: 190/800 毫克
钠: 121/2300 毫克
液体: 200/1500 毫升
总价值: 11
```

### 返回示例2

```
limits = [
1500,  # 能量上限（千卡）
15,  # 蛋白质上限（克）
2000,  # 钾上限（毫克）
800,  # 磷上限（毫克）
2300,  # 钠上限（毫克）
1500  # 液体上限（毫升）
]
选择的食物：
- 鸡蛋

总计：
能量: 70/150 千卡
蛋白质: 6/15 克
钾: 100/2000 毫克
磷: 80/800 毫克
钠: 70/2300 毫克
液体: 0/1500 毫升
总价值: 5
```

### 返回示例3

```
limits = [
1500,  # 能量上限（千卡）
15,  # 蛋白质上限（克）
2000,  # 钾上限（毫克）
800,  # 磷上限（毫克）
2300,  # 钠上限（毫克）
1500  # 液体上限（毫升）
]
选择的食物：
- 鸡蛋

总计：
能量: 70/150 千卡
蛋白质: 6/15 克
钾: 100/2000 毫克
磷: 80/800 毫克
钠: 70/2300 毫克
液体: 0/1500 毫升
总价值: 5
```

### 返回示例4

```
limits = [
1500,  # 能量上限（千卡）
50,  # 蛋白质上限（克）
2000,  # 钾上限（毫克）
800,  # 磷上限（毫克）
2300,  # 钠上限（毫克）
1500  # 液体上限（毫升）
]
选择的食物：
- 香蕉
- 全麦面包
- 鸡胸肉
- 牛奶
- 鸡蛋

总计：
能量: 595/1500 千卡
蛋白质: 50/50 克
钾: 930/2000 毫克
磷: 450/800 毫克
钠: 376/2300 毫克
液体: 200/1500 毫升
总价值: 22
```



- 未来优化策略：
  - 降维打击: 由于限制条件较多, 可以尝试将磷和钾合并考虑, 因为通常含钾高的食物含磷也高, 这样可以降低约束条件的数量, 降低计算复杂度.
  - 预先筛选： 在进行动态规划之前，可以根据患者的病情和饮食建议，预先筛选出一些不合适的菜品（例如，高钾血症患者应避免选择高钾的菜品），减少搜索空间。
  - 启发式搜索： 可以结合启发式搜索算法（如遗传算法、模拟退火算法）来优化菜品组合，例如，优先选择营养素密度高、患者喜爱的菜品。
{% endraw %}
