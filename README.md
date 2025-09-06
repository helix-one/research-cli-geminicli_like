# Gemini Research Agent (科研辅助 Agent)

欢迎使用 Gemini Research Agent，这是一个强大的命令行辅助工具，旨在加速您的科学研究工作流程。本 Agent 将扮演一个主动、智能的伙伴，帮助您分析论文、管理知识并激发新的想法。

## 功能特性

- **交互式对话:** 与一个成熟的 AI 助手进行自然语言对话。
- **专家人设:** Agent 会扮演一名顶尖的科研顾问，提供批判性的分析和主动的建议。
- **双模思维:** 可通过命令在 `convergent` (收敛/逻辑) 和 `divergent` (发散/创意) 两种思维模式间切换。
- **工作记忆:** 使用 `!load_session` 命令将一篇核心文档加载到 Agent 的当前会话记忆中，以进行深入、专注的分析。（目前没有删除文献的功能，load会一直保存在内存中，每次都会发送给llm）
- **知识库管理:** 
    - 使用 `!add_kb` 命令将参考论文添加到可供长期检索的知识库中。
    - Agent 可以在对话中**自主**搜索此知识库，以查找相关信息来支撑其论点。
- **文件生成:** 您可以要求 Agent 撰写总结、大纲或新想法，并将其保存到文件中。
- **会话管理:** 使用 `!save_session` 保存完整的对话历史，并可在日后重新加载。

## 安装指南

1.  **克隆或下载项目:** 
    ```bash
    # 假如使用 git
    git clone <repository_url>
    cd gemini_research_agent
    ```

2.  **创建并激活 Python 虚拟环境:** 
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖:** 
    ```bash
    pip install -r requirements.txt
    ```

4.  **以“可编辑模式”安装项目包:** 
    这个关键步骤能让项目内的模块（如 `core`, `tools`）被正确地导入。
    ```bash
    pip install -e .
    ```
    #python -m pytest(确保同一个python环境)

## 使用方法

1.  **运行 Agent:** 
    ```bash
    python main.py
    ```

2.  **初次配置:** 首次运行时，程序会提示您输入 LLM 的 API Key、API Base URL 和您希望使用的模型名称。

3.  **与 Agent 互动:** 
    - 直接输入您的问题或想法，然后按 Enter。
    - 使用以下命令来管理您的工作流。

### 命令列表

-   **`!load_session <文件的绝对路径>`**: “精读”模式。加载一个文件到 Agent 当前的“工作记忆”中。
-   **`!add_kb <文件的绝对路径>`**: “归档”模式。复制一个文件到 Agent 的长期知识库中 (`knowledge_base/` 文件夹)。
-   **`!save_session [文件的绝对路径]`**: 保存当前完整的对话历史。如果未提供路径，将自动保存为带时间戳的文件。
-   **`!mode <convergent|divergent>`**: 切换 Agent 的思维模式。

### 工作流示例

```
# 1. 首先，将一篇重要的参考论文“归档”到你的长期知识库中
You> !add_kb C:\Users\MyUser\Downloads\Serra-Picamal-2012.md

# 2. 接着，将你的论文草稿“精读”加载到当前会话中，以便进行深入讨论
You> !load_session C:\Users\MyUser\Documents\my_draft.md

# 3. 开始提问。Agent 在回答时，可能会自主地使用它刚刚归档的知识
You> 根据我的草稿，并结合你所知道的 Serra-Picamal 的研究，我的引言部分最大的弱点是什么？

# 4. 让 Agent 为你生成并保存文件
You> 这个观点很好。请根据我们的讨论，重写一个新的结论段落，并保存到 C:\Users\MyUser\Documents\new_conclusion.txt
```