#!/usr/bin/env python3
"""
Script to check Anthropic client installation and setup.
"""

import os
import sys
import importlib.metadata
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_anthropic():
    """
    Check the Anthropic client installation.
    """
    print("Checking Anthropic client installation...\n")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if CLAUDE_API_KEY is set
    api_key = os.environ.get("CLAUDE_API_KEY")
    if api_key:
        print("CLAUDE_API_KEY environment variable is set ✓")
        # Print first few characters of API key for verification
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        print(f"API key: {masked_key}")
    else:
        print("CLAUDE_API_KEY environment variable is NOT set ✗")
        print("Please set your API key with: export CLAUDE_API_KEY=your_key_here")
        print("Or add it to a .env file in the project root")
        return
    
    # Check installed anthropic version
    try:
        anthropic_version = importlib.metadata.version("anthropic")
        print(f"Anthropic library version: {anthropic_version} ✓")
    except importlib.metadata.PackageNotFoundError:
        print("Anthropic library is NOT installed ✗")
        print("Please install with: pip install anthropic")
        return
    
    # Try to import and instantiate client
    try:
        import anthropic
        print(f"Successfully imported anthropic module ✓")
        
        # Try to detect which client class/format to use
        if hasattr(anthropic, "Anthropic") and hasattr(anthropic, "Client"):
            print("Detected both client formats - this can cause conflicts ✗")
            print("Strange situation: both Anthropic and Client classes found in this version.")
            
            # Try older Client first as we're using anthropic==0.5.0
            try:
                print("\nTesting older Anthropic client...")
                client = anthropic.Client(api_key=api_key)
                print("Successfully created Client instance ✓")
                client_class = "Client"
            except Exception as e:
                print(f"Error creating Client: {e} ✗")
                client_class = None
                
        elif hasattr(anthropic, "Anthropic"):
            print("Using new Anthropic client format (messages API) ✓")
            client_class = "Anthropic"
            
            # Try to create a client with the newer format
            try:
                print("\nTesting newer Anthropic client...")
                client = anthropic.Anthropic(api_key=api_key)
                print("Successfully created Anthropic client instance ✓")
            except Exception as e:
                print(f"Error creating Anthropic client: {e} ✗")
                print("This may be because you're using an older version of the Anthropic package.")
                client_class = None
                
        elif hasattr(anthropic, "Client"):
            print("Using old Anthropic client format (completion API) ✓")
            client_class = "Client"
            
            # Try to create a client with the older format
            try:
                print("\nTesting older Anthropic client...")
                client = anthropic.Client(api_key=api_key)
                print("Successfully created Client instance ✓")
            except Exception as e:
                print(f"Error creating Client: {e} ✗")
                client_class = None
        else:
            print("Could not detect Anthropic client class ✗")
            client_class = None
        
        if client_class:    
            # Try generator function
            print("\nTesting generator function...")
            from generator import generate
            test_prompt = "Say hello in one sentence."
            print(f"Test prompt: '{test_prompt}'")
            response = generate(test_prompt)
            print(f"Response: '{response}'")
            print("Generator function test complete ✓")
        else:
            print("\nFIX RECOMMENDATION:")
            print("Based on your Anthropic version, try one of these fixes:")
            print("1. For older client (v0.x): pip install 'anthropic==0.5.0'")
            print("2. For newer client (v1.x+): pip install --upgrade anthropic")
            print("Then run this script again to verify the fix.")
        
    except Exception as e:
        print(f"Error when trying to use Anthropic client: {e} ✗")
        print("Please check your installation and API key.")

if __name__ == "__main__":
    check_anthropic()