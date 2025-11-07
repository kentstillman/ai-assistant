#!/usr/bin/env python3
"""
Simple test of AI assistant consultation
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import AI assistant
from ai_assistant import AIAssistant

async def test_consultation():
    """Test consultation mechanism"""
    print("🤖 Testing AI Assistant Consultation...")
    
    assistant = AIAssistant()
    
    try:
        # Start session
        print("📋 Starting session...")
        await assistant.start_session()
        
        # Test consultation
        print("💬 Asking OpenCode: 'What files are in this directory?'")
        result = await assistant.consult_opencode("What files are in this directory?")
        
        print(f"✅ Consultation Status: {result['status']}")
        if result['status'] == 'success':
            response = result['response']
            print(f"📝 Response preview: {response[:150]}...")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await assistant.shutdown()
        print("🏁 Test complete")

if __name__ == "__main__":
    asyncio.run(test_consultation())