import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def generate(prompt):
    """
    Generate response using Claude API.
    This function handles different versions of the Anthropic library.
    """
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise ValueError("CLAUDE_API_KEY environment variable is not set")
    
    try:
        # Try with the latest Anthropic library
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620", 
            max_tokens=1000,
            temperature=0.6,
            system="You follow tasks exactly as you are told. You have extremely high IQ and is the smartest AI Agent who responds and does exactly as told.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error with current Anthropic client: {e}")
        try:
            # Try with older Anthropic client format
            client = anthropic.Client(api_key=api_key)
            resp = client.completion(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                model="claude-2.0",
                max_tokens_to_sample=1000,
                temperature=0.6,
            )
            return resp.completion
        except Exception as e2:
            print(f"Error with fallback Anthropic client: {e2}")
            # Final fallback - just return an error message
            return f"ERROR: Could not generate response. Please check your Claude API key and Anthropic library version. Error: {e2}"

# For testing
if __name__ == "__main__":
    test_response = generate("Hello, how are you?")
    print(test_response)