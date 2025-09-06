# 教程：如何构建一个类 Gemini CLI 的科研 Agent

欢迎！本教程是此项目的核心交付物。它的目的不只是展示代码，更是为了解释构建一个现代 AI Agent 背后的**架构决策**与**设计哲学**。

我们的最终目标是：当您理解了这个项目后，您将有能力去审视一个生产级系统（如 Google 的 Gemini CLI）的源码，并能识别出其核心的设计思想。

---

## 第一章：Agent 的哲学 —— 从“聊天”到“行动”

一个 AI Agent 的核心，远超一个简单的聊天机器人。它是一个能够**推理、规划并行动**的系统。我们的 Agent 构建于三大基本支柱之上：

1.  **LLM 作为推理引擎:** 大语言模型是 Agent 的“大脑”。我们不只让它回答问题，而是赋予它一个**角色 (Persona)**、一项**使命 (Mission)** 和一套**工具 (Tools)**，然后让它自己**决策**出最佳的行动路线。这一切都通过精心设计的**系统提示 (System Prompt)** 来实现 (参见 `core/prompt_manager.py`)。

2.  **工作记忆 vs. 长期记忆:** 这是我们项目中一个关键的架构决策。通过分离两种记忆，Agent 才能高效地处理信息：
    -   **工作记忆 (Working Memory):** Agent 的短期焦点，如同摊在桌面上的几篇核心论文。它由 `!load_session` 命令管理，存在于 `chat_history` 中。它的“成本”很高（每次交互都会被发送给 LLM），但因此也获得了最高的关注度。
    -   **长期记忆 (Long-Term Memory / Knowledge Base):** Agent 的图书馆。它容量巨大、存储成本低，但必须通过一次明确的**行动 (Tool Call)** 才能从中检索信息。这种分离设计让 Agent 能处理海量信息而不被“淹没”。

3.  **自主工具使用:** 这是区分 Agent 与普通程序的关键。它不只会“说”，更能够“做”。它能读文件、查资料、写报告。整个决策过程由 **Agent Executor** (`core/agent.py` 中的核心组件) 来自动协调。

---

## 第二章：架构对比 —— 我们的项目 vs. Gemini CLI

Gemini CLI 这样的生产级系统非常复杂，但它遵循的模块化思想，我们在这个项目中用一种更简洁的方式进行了模拟。

-   **我们的简单结构:** `core`, `cli`, `tools` 三个清晰的目录，分别代表“大脑”、“外观”和“双手”。
-   **Gemini CLI 的生产级结构:**
    -   **Monorepo (`packages/`):** Gemini CLI 是一个“单体仓库”，所有子项目（如 `@google/generative-ai` SDK, `cli` 等）都在一个仓库中。这便于代码共享和统一管理，是大型项目的标准实践。我们的 `core` 和 `cli` 目录，就类似于它 `packages/` 下的两个子包。
    -   **TypeScript:** Gemini CLI 使用 TypeScript（带类型的 JavaScript）。它在前端领域扮演的角色，与 Python 中的类型提示 (Type Hint) 类似，都是为了增加代码的健壮性。
    -   **构建系统 (`esbuild.config.js`, `scripts/`):** 生产级项目需要复杂的“构建”步骤来打包和优化代码。我们的 Python 项目比较简单，可以直接运行，无需这一步。
    -   **UI 框架 (Ink):** 它的命令行界面是用 `React` 和 `Ink` 库构建的，远比我们的 `rich` 库复杂。它允许用“组件化”的方式来开发交互式界面，提供了更丰富的可能性。

---

## 第三章：“大脑”的核心 —— Agent Executor 与提示工程

魔法发生在 `ResearchAgent` 类中。我们没有手写一个复杂的 `if/else` 来决定何时调用工具，而是完全交给了 LangChain 的 **Agent Executor**。

它的工作流是：
1.  **定义工具集:** `self.tools = [search_knowledge_base, write_file]`。
2.  **设计提示模板:** 我们使用了一个为 Agent 设计的特殊 `ChatPromptTemplate`，其中包含了 `agent_scratchpad` 这样的占位符。“暂存盘 (Scratchpad)”是 Agent 的“草稿纸”，它会在这里思考“我应该用哪个工具？”、“参数是什么？”、“工具返回了什么？”等问题。
3.  **绑定与执行:** `create_openai_tools_agent` 将 LLM、工具和提示绑定成一个认知单元，再由 `AgentExecutor` 包装成一个可执行的循环。我们调用 `agent_executor.invoke()` 时，这个复杂的“思考-行动-观察”循环就自动开始了。

---

## 第四章：“五官”与“双手” —— 可靠的工具系统

Agent 如何理解我们的 Python 函数？答案是 `@tool` 装饰器。

```python
from langchain.tools import tool

@tool
def write_file(filepath: str, content: str) -> str:
    """
    Writes or overwrites a file with the given content.
    Use with caution, as this will replace any existing content.
    """
    # ... function logic ...
```

当 Agent 启动时，LangChain 会“阅读”这个函数，并提取出三样东西：
1.  **函数名:** `write_file`
2.  **参数与类型:** `filepath: str`, `content: str`
3.  **文档字符串 (Docstring):** `"""Writes or overwrites..."""`

这些信息会被格式化后，作为一条隐藏的系统提示发送给 LLM，相当于给了 LLM 一本“工具使用说明书”。因此，**文档字符串对于工具的性能至关重要**，它必须清晰地解释工具的用途。

**深入一步：与 MCP 的关系**

Gemini CLI 的文档中提到了 **Model-centric Protocols (MCP)**。这听起来很复杂，但其核心思想我们已经实现了！MCP 本质上就是一套**用于向模型描述工具的标准化“模式” (Schema)**。我们用 `@tool` 装饰器和文档字符串所做的事情，正是 MCP 的一种轻量级、自动化的实现。当您在 Gemini CLI 源码中看到一个用于定义工具的 JSON 或 TypeScript 对象时，就可以理解为，那只是我们文档字符串的一种更严格、更形式化的版本。

---

## 第五章：“状态管理” —— 对话记忆与会话状态

-   **我们的实现:** 我们用一个简单的列表 `chat_history` 来保存对话历史，用一个简单的变量 `current_mode` 来管理 CLI 的当前状态。这对于单用户会话是有效的。
-   **Gemini CLI 的实现:** 生产级应用需要更复杂的会话管理。它们需要同时处理多个用户的会话，可能会将会话状态（如 `chat_history`）存储在数据库或缓存中，而不是内存里。Gemini CLI 文档中提到的 **Checkpointing** 功能，就是一种更高级的会话保存/恢复机制，远比我们的 `!save_session` 命令要强大。

---

## 第六章：“安全”与“健壮性” —— 沙箱与测试

-   **测试 (`tests/`):** 我们用 `pytest` 测试了工具的确定性行为。这是保证代码质量的基础。
-   **沙箱 (Sandbox) (我们未实现，但至关重要):** 这是我们项目和 Gemini CLI 之间一个巨大的差异。我们的 Agent 在执行工具（特别是 `write_file`）时，拥有与您当前用户完全相同的权限，这是有风险的。Gemini CLI 这样的生产级工具，在执行任何可能影响系统的操作时（如执行 shell 命令），会先启动一个**沙箱**环境（例如一个临时的 Docker 容器），然后在那个被严格隔离和限制的环境里执行工具。这样，即使工具出现 bug 或被恶意利用，也无法破坏您的主系统。这是所有专业级 Agent 必须具备的核心安全特性。

---

## 第七章：您的下一步 —— 阅读 Gemini CLI 源码

现在，您可以带着我们项目的经验去探索 Gemini CLI 的世界了。

-   当您看到 `packages/core/src/tool-use/...` 目录时，可以联想到我们的 `core/agent.py` 和 `AgentExecutor`。
-   当您看到一个用于定义工具的复杂 JSON Schema 时，可以联想到我们的 `@tool` 装饰器和我们精心编写的文档字符串。
-   当您看到它执行 shell 命令的代码时，可以特别关注一下它是如何启动和管理**沙箱**的，并与我们直接执行的简单方式做对比。

恭喜您完成本项目！您不仅构建了一个强大的工具，更重要的是，您已经掌握了理解和剖析现代 AI Agent 的核心知识与思想框架。