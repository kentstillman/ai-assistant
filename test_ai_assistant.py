#!/usr/bin/env python3
"""
Test AI Assistant Consultation
Demonstrates AI assistant consulting with OpenCode
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_assistant import AIAssistant

async def test_consultation():
    """Test AI assistant consultation with OpenCode"""
    assistant = AIAssistant()
    
    try:
        # Start session
        print("🚀 Starting AI Assistant session...")
        await assistant.start_session()
        
        # Set a task
        print("\n📝 Setting task: 'Test consultation mechanism'")
        await assistant.set_task("Test consultation mechanism")
        
        # Test consultation
        print("\n🤖 Consulting OpenCode: 'How can I improve this Python script?'")
        consultation_result = await assistant.consult_opencode(
            "How can I improve this Python script for better performance and readability?"
        )
        
        print(f"\n📊 Consultation Result:")
        print(f"Status: {consultation_result['status']}")
        if consultation_result['status'] == 'success':
            print(f"Response: {consultation_result['response'][:200]}...")
        else:
            print(f"Error: {consultation_result.get('error', 'Unknown error')}")
        
        # Test script execution
        print("\n🔧 Testing script execution: 'session_manager.py start'")
        script_result = await assistant.execute_script("session_manager.py", ["start"])
        
        print(f"\n📊 Script Execution Result:")
        print(f"Status: {script_result['status']}")
        if script_result['status'] == 'success':
            print(f"Output: {script_result['stdout'][:200]}...")
        else:
            print(f"Error: {script_result.get('error', 'Unknown error')}")
        
        # Complete task
        print("\n✅ Completing task...")
        completion_result = await assistant.complete_task(
            "Successfully tested AI assistant consultation and script execution",
            "Continue with Phase 3 development"
        )
        
        print(f"\n📊 Task Completion Result:")
        print(f"Status: {completion_result['status']}")
        print(f"Session ID: {completion_result.get('session_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Shutdown
        print("\n🛑 Shutting down AI Assistant...")
        await assistant.shutdown()

if __name__ == "__main__":
    asyncio.run(test_consultation())