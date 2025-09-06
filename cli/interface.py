from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage
from datetime import datetime

from core.agent import ResearchAgent
from tools.file_io import read_file, add_file_to_kb, save_session_history

def run_cli():
    """
    The main function to run the command-line interface.
    """
    console = Console()
    console.print("[bold cyan]Welcome to the Gemini Research Agent![/bold cyan]")
    console.print("Let's get you set up.")

    # --- Configuration on Startup ---
    api_key = Prompt.ask("[yellow]Enter your API Key[/yellow]")
    api_base = Prompt.ask("[yellow]Enter the API Base URL[/yellow]", default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name = Prompt.ask("[yellow]Enter the model name[/yellow]", default="qwen-plus")

    console.print("\n[bold green]Setup complete. You can now start chatting.[/bold green]")
    console.print("Type 'exit' or 'quit' to end the session.")

    # --- Initialize Agent ---
    try:
        agent = ResearchAgent(model=model_name, api_key=api_key, api_base=api_base)
    except Exception as e:
        console.print(f"[bold red]Error initializing agent: {e}[/bold red]")
        return

    # --- Session State ---
    current_mode = "convergent" # Default mode

    # --- Main Chat Loop ---
    while True:
        user_input = Prompt.ask("\n[bold]You[/bold]")

        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break
        
        # --- Command Handling ---
        if user_input.startswith("!"):
            if user_input.startswith("!load_session "):
                filepath = user_input.split(" ", 1)[1]
                console.print(f"[italic]Attempting to load file into session memory: {filepath}[/italic]")
                content, error = read_file(filepath)
                if error:
                    console.print(f"[bold red]{error}[/bold red]")
                else:
                    memory_content = f"""I have just loaded the following document into my working memory for this session. 
It is now part of our conversation history. 
Please acknowledge you have read it, then await my specific questions about it.

--- DOCUMENT START ---
{content}
--- DOCUMENT END ---"""
                    agent.chat_history.append(HumanMessage(content=memory_content))
                    console.print(f"[bold green]Successfully loaded document into agent's working memory.[/bold green]")
            
            elif user_input.startswith("!add_kb "):
                filepath = user_input.split(" ", 1)[1]
                console.print(f"[italic]Attempting to add file to knowledge base: {filepath}[/italic]")
                success_msg, error_msg = add_file_to_kb(filepath)
                if error_msg:
                    console.print(f"[bold red]{error_msg}[/bold red]")
                else:
                    console.print(f"[bold green]{success_msg}[/bold green]")

            elif user_input.startswith("!save_session"):
                args = user_input.split(" ", 1)
                if len(args) > 1:
                    filepath = args[1]
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = f"session_history_{timestamp}.md"
                
                console.print(f"[italic]Saving session to {filepath}...[/italic]")
                success_msg, error_msg = save_session_history(agent.chat_history, filepath)
                if error_msg:
                    console.print(f"[bold red]{error_msg}[/bold red]")
                else:
                    console.print(f"[bold green]{success_msg}[/bold green]")

            elif user_input.startswith("!mode "):
                mode_name = user_input.split(" ", 1)[1].lower()
                if mode_name in ["convergent", "divergent"]:
                    current_mode = mode_name
                    console.print(f"[italic yellow]Agent mode switched to: {current_mode}[/italic yellow]")
                else:
                    console.print(f"[bold red]Error: Invalid mode. Please choose 'convergent' or 'divergent'.[/bold red]")

            else:
                console.print("[bold red]Error: Unknown command. Available commands: !load_session <path>, !add_kb <path>, !save_session [path], !mode <name>[/bold red]")
            continue # Skip the chat part and wait for next input

        # Inject mode instruction into the user input
        mode_instruction = f"[SYSTEM INSTRUCTION: For this turn, you MUST operate in {current_mode.upper()} mode.]"
        final_input = f"{mode_instruction}\n\nUSER QUESTION: {user_input}"

        with console.status("[bold green]Thinking...[/bold green]"): 
            raw_response = agent.chat(final_input)
        
        # Extract only the final answer part for clean display
        final_answer_marker = "**Final Answer:**"
        if final_answer_marker in raw_response:
            final_answer = raw_response.split(final_answer_marker, 1)[1].strip()
        else:
            final_answer = raw_response # Fallback for tool calls or other formats

        console.print("\n[bold cyan]Agent:[/bold cyan]")
        markdown_output = Markdown(final_answer)
        console.print(markdown_output)

