from dataclasses import dataclass
from . import config
from .tools import TOOL_EXECUTORS, TOOL_FUNCTIONS, get_workspace_summary
from .context import Transcript, trim_chat_history
from .spinner import Spinner, console

from rich.text import Text
from rich.panel import Panel
from rich import box


@dataclass
class TokenUsage:
    prompt: int = 0
    completion: int = 0

    @property
    def total(self) -> int:
        return self.prompt + self.completion

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            self.prompt + other.prompt, self.completion + other.completion
        )


try:
    from google import genai
    from google.genai import types
except ImportError:
    print(
        "Warning: google-genai package is not installed. Please `pip install google-genai`."
    )


class Agent:
    def __init__(self):
        # Configure Gemini API client
        self.client = genai.Client(api_key=config.API_KEY)
        self.model_name = config.MODEL_NAME

        self.workspace_context = get_workspace_summary()
        self.is_first_message = True

        # Cumulative token usage for this session
        self.token_usage: TokenUsage = TokenUsage()

        # Full transcript — append-only log that is never truncated
        self.transcript = Transcript()

        self.system_instruction = (
            "You are Lambda, a minimal and highly efficient AI coding agent. "
            "Your primary goal is to help the user by writing code, executing commands, "
            "and managing files. You have access to tools that let you read files, "
            "write files, run shell commands, and ask the user questions. "
            "Whenever the user asks you to do something that requires these tools, "
            "you should use them autonomously. "
            "CRITICAL: Do not guess the user's intent. Guessing is bad. "
            "If there is any confusion or ambiguity, you MUST use the ask_user tool "
            "to clarify the job with the human. You can ask multiple questions. "
            "Be concise and professional.\n\n"
            "## Error Handling\n"
            "If you encounter an error when executing a tool or command, DO NOT immediately guess "
            "and try to fix it in a fast loop. First, take a moment to fully understand the error. "
            "Investigate the specific context (e.g., read the file, check the directory) to figure "
            "out why it failed before trying a new command.\n\n"
            "## Scratchpad\n"
            "You have a persistent scratchpad file (.agent/scratchpad.md) available "
            "in the working directory. Use it for complex or multi-step tasks:\n"
            "1. **Planning**: Before starting a large task, use write_scratchpad to "
            "outline your plan with sections like '## Plan', '## Implementation Steps', "
            "'## Open Questions'.\n"
            "2. **Progress tracking**: As you complete steps, use update_scratchpad to "
            "log your progress under a '## Progress' section.\n"
            "3. **Context persistence**: If a task spans many turns, read_scratchpad "
            "at the start of each turn to recall your plan.\n"
            "4. **Cleanup**: Use clear_scratchpad when a task is fully complete.\n"
            "The scratchpad is stored in a hidden .agent/ directory — it is for your "
            "internal use only and is not shown to the user.\n\n"
            "## Sub-Agents\n"
            "You can spawn lightweight sub-agents using dispatch_subagent to perform "
            "independent, parallelizable work. Sub-agents run in separate threads "
            "with their own Gemini sessions and return short result summaries.\n"
            "WHEN TO USE:\n"
            "- Parallel research: reading multiple files, searching for patterns, "
            "analyzing independent parts of the codebase simultaneously.\n"
            "- Running investigative commands in parallel.\n"
            "- Any task where two or more pieces of work don't depend on each other.\n"
            "WHEN NOT TO USE:\n"
            "- Sequential tasks where step 2 depends on step 1's output.\n"
            "- Tasks that require writing to the same file (risk of conflicts).\n"
            "- Simple tasks that you can do faster yourself with a single tool call.\n"
            "HOW TO USE:\n"
            "- Call dispatch_subagent with a clear, self-contained task description.\n"
            "- Provide minimal context (the sub-agent has NO access to your chat history).\n"
            "- You can call dispatch_subagent multiple times in the same turn — they "
            "will execute in parallel.\n"
            "- Each sub-agent returns a concise summary. Use it to inform your next steps."
        )

        # Initialize the chat session with the built tools and system instructions
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=TOOL_FUNCTIONS,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

    def switch_model(self, new_model: str) -> str:
        """Switch to a different model mid-session. Returns confirmation message."""
        old_model = self.model_name
        self.model_name = new_model

        # Re-create the chat session with the new model
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=TOOL_FUNCTIONS,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )
        self.is_first_message = True
        return f"Switched model from [cyan]{old_model}[/cyan] → [bold cyan]{new_model}[/bold cyan]"

    def _accumulate(self, response) -> TokenUsage:
        """Extract token counts from a response and add them to the session total."""
        usage = getattr(response, "usage_metadata", None)
        if usage is None:
            return TokenUsage()
        delta = TokenUsage(
            prompt=getattr(usage, "prompt_token_count", 0) or 0,
            completion=getattr(usage, "candidates_token_count", 0) or 0,
        )
        self.token_usage = self.token_usage + delta
        return delta

    def chat(self, user_input: str) -> tuple[str, TokenUsage]:
        """
        Takes user input, sends it to Gemini, and runs a manual loop observing ToolCalls.
        Returns (response_text, turn_token_usage).
        """
        if self.is_first_message:
            payload = (
                "--- WORKSPACE CONTEXT ---\n"
                f"{self.workspace_context}\n"
                "-------------------------\n\n"
                f"User Request: {user_input}"
            )
            self.is_first_message = False
        else:
            payload = user_input

        # Track tokens for this turn
        turn_usage = TokenUsage()

        # Log the user message to the full transcript
        self.transcript.log("user", user_input)

        # Send the initial user message
        with Spinner():
            response = self.chat_session.send_message(payload)
        turn_usage = turn_usage + self._accumulate(response)

        max_tool_iterations = 10
        iterations = 0

        # The loop will continue as long as Gemini decides to call tools
        while True:
            iterations += 1
            if iterations > max_tool_iterations:
                error_msg = f"Error: Maximum tool call limit ({max_tool_iterations}) reached to prevent infinite loops."
                self.transcript.log("assistant", error_msg)
                return error_msg, turn_usage

            try:
                # 1. Check if the model returned a function_call
                tool_calls = response.function_calls if response.function_calls else []

                # 2. If it did, act on each function call
                if tool_calls:
                    tool_responses = []

                    for function_call in tool_calls:
                        function_name = function_call.name

                        # Convert protobuf args to dict if possible
                        arguments = function_call.args
                        if hasattr(arguments, "items"):
                            arguments = {key: value for key, value in arguments.items()}
                        elif not isinstance(arguments, dict):
                            arguments = dict(arguments) if arguments else {}
                        # Pretty-print the tool call with rich
                        # Hide scratchpad operations from the user
                        _HIDDEN_TOOLS = {
                            "read_scratchpad",
                            "write_scratchpad",
                            "update_scratchpad",
                            "clear_scratchpad",
                        }
                        if function_name not in _HIDDEN_TOOLS:
                            # Sub-agent dispatches get a distinct green style
                            if function_name == "dispatch_subagent":
                                # The subagent module handles its own display,
                                # so we only show a lightweight header here.
                                pass
                            else:
                                tool_label = Text.assemble(
                                    (" ⚙ TOOL ", "bold black on magenta"),
                                    (f"  {function_name}", "bold magenta"),
                                )
                                args_str = ", ".join(
                                    f"[dim]{k}[/dim]=[yellow]{repr(v)}[/yellow]"
                                    for k, v in arguments.items()
                                )
                                console.print()
                                console.print(tool_label)
                                console.print(
                                    Panel(
                                        args_str or "[dim](no arguments)[/dim]",
                                        border_style="magenta",
                                        box=box.SIMPLE,
                                        padding=(0, 2),
                                    )
                                )

                        # 3. Execute the tool locally
                        if function_name in TOOL_EXECUTORS:
                            function_to_call = TOOL_EXECUTORS[function_name]
                            # Call the function dynamically
                            tool_result = function_to_call(**arguments)
                        else:
                            tool_result = f"Error: Tool {function_name} not found."

                        # Log full tool call + result to the untruncated transcript
                        self.transcript.log(
                            "tool_call",
                            function_name,
                            meta={"args": {k: str(v) for k, v in arguments.items()}},
                        )
                        self.transcript.log(
                            "tool_result",
                            str(tool_result),
                            meta={"tool": function_name},
                        )

                        # Format the result back into Gemini's expected Response format
                        tool_responses.append(
                            types.Part.from_function_response(
                                name=function_name,
                                response={"result": str(tool_result)},
                            )
                        )

                    # 4. Send ALL the tool responses back to the model
                    # so it can continue reasoning based on the new information
                    with Spinner():
                        response = self.chat_session.send_message(tool_responses)
                    turn_usage = turn_usage + self._accumulate(response)
                    continue  # Start the loop over to see if it calls more tools
                else:
                    # No more tool calls; the LLM has generated a final text response.
                    # Trim older tool responses in the chat history (sliding window)
                    try:
                        trim_chat_history(self.chat_session._curated_history)
                    except Exception:
                        pass  # Never let trimming crash the agent

                    self.transcript.log("assistant", response.text or "")
                    return response.text, turn_usage
            except Exception as e:
                return f"An error occurred in the agent loop: {str(e)}", turn_usage
