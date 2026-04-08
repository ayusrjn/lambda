import sys
from .agent import Agent

def main():
    print("========================================")
    print("      Lambda Coding Agent Started       ")
    print("========================================")
    
    try:
        agent = Agent()
        print("Lambda is ready! Type 'exit' or 'quit' to stop.")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\\nYou: ")
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if not user_input.strip():
                    continue
                    
                response = agent.chat(user_input)
                print(f"\\nLambda: {response}")
                
            except KeyboardInterrupt:
                print("\\nGoodbye!")
                break
    except Exception as e:
        print(f"Failed to initialize Lambda: {str(e)}")

if __name__ == "__main__":
    main()
