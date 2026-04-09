from .config import API_KEY, MODEL_NAME
from .tools import TOOL_EXECUTORS, TOOL_FUNCTIONS

try:
    import google.generativeai as genai
except ImportError:
    print(
        "Warning: google-generativeai package is not installed. Please `pip install google-generativeai`."
    )


class Agent:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=API_KEY)
        self.model_name = MODEL_NAME

        system_instruction = (
            "You are Lambda, a minimal and highly efficient AI coding agent. "
            "Your primary goal is to help the user by writing code, executing commands, "
            "and managing files. You have access to tools that let you read files, "
            "write files, and run shell commands. Whenever the user asks you to do "
            "something that requires these tools, you should use them autonomously. "
            "Be concise and professional."
        )

        # Initialize the generative model with the built tools and system instructions
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            tools=TOOL_FUNCTIONS,
        )

        # Gemini manages history cleanly through the ChatSession
        self.chat_session = self.model.start_chat()

    def chat(self, user_input: str) -> str:
        """
        Takes user input, sends it to Gemini, and runs a manual loop observing ToolCalls.
        """
        # Send the initial user message
        response = self.chat_session.send_message(user_input)

        # The loop will continue as long as Gemini decides to call tools
        while True:
            try:
                # 1. Check if the model returned a function_call in any part
                tool_calls = [
                    part.function_call
                    for part in response.parts
                    if getattr(part, "function_call", None)
                ]

                # 2. If it did, act on each function call
                if tool_calls:
                    tool_responses = []

                    for function_call in tool_calls:
                        function_name = function_call.name

                        # Convert protobuf args to dict
                        arguments = {
                            key: value for key, value in function_call.args.items()
                        }
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
                            {
                                "function_response": {
                                    "name": function_name,
                                    "response": {"result": str(tool_result)},
                                }
                            }
                        )

                    # 4. Send ALL the tool responses back to the model
                    # so it can continue reasoning based on the new information
                    response = self.chat_session.send_message(tool_responses)
                    continue  # Start the loop over to see if it calls more tools
                else:
                    # No more tool calls; the LLM has generated a final text response.
                    return response.text
            except Exception as e:
                return f"An error occurred in the agent loop: {str(e)}"
