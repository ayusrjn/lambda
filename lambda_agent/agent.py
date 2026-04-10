from . import config
from .tools import TOOL_EXECUTORS, TOOL_FUNCTIONS, get_workspace_summary
from .spinner import Spinner

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

        system_instruction = (
            "You are Lambda, a minimal and highly efficient AI coding agent. "
            "Your primary goal is to help the user by writing code, executing commands, "
            "and managing files. You have access to tools that let you read files, "
            "write files, run shell commands, and ask the user questions. "
            "Whenever the user asks you to do something that requires these tools, "
            "you should use them autonomously. "
            "CRITICAL: Do not guess the user's intent. Guessing is bad. "
            "If there is any confusion or ambiguity, you MUST use the ask_user tool "
            "to clarify the job with the human. You can ask multiple questions. "
            "Be concise and professional."
        )

        # Initialize the chat session with the built tools and system instructions
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=TOOL_FUNCTIONS,
            ),
        )

    def chat(self, user_input: str) -> str:
        """
        Takes user input, sends it to Gemini, and runs a manual loop observing ToolCalls.
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

        # Send the initial user message
        with Spinner():
            response = self.chat_session.send_message(payload)

        # The loop will continue as long as Gemini decides to call tools
        while True:
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
                        print(f"\\n[Lambda is executing: {function_name}({arguments})]")

                        # 3. Execute the tool locally
                        if function_name in TOOL_EXECUTORS:
                            function_to_call = TOOL_EXECUTORS[function_name]
                            # Call the function dynamically
                            tool_result = function_to_call(**arguments)
                        else:
                            tool_result = f"Error: Tool {function_name} not found."

                        # Format the result back into Gemini's expected Response format
                        tool_responses.append(
                            types.Part.from_function_response(
                                name=function_name,
                                response={"result": str(tool_result)},
                            )
                        )

                    # 4. Send ALL the tool responses back to the model
                    # so it can continue reasoning based on the new information
                    tool_content = types.Content(role="tool", parts=tool_responses)
                    with Spinner():
                        response = self.chat_session.send_message(tool_content)
                    continue  # Start the loop over to see if it calls more tools
                else:
                    # No more tool calls; the LLM has generated a final text response.
                    return response.text
            except Exception as e:
                return f"An error occurred in the agent loop: {str(e)}"
