#!/usr/bin/env python3
"""
Child Script Orchestration Demo
Shows how AI assistant can coordinate multiple scripts
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_assistant import AIAssistant

async def demonstrate_orchestration():
    """Demonstrate script orchestration capabilities"""
    print("🎭 Child Script Orchestration Demo")
    print("=" * 40)
    
    assistant = AIAssistant()
    
    try:
        # Start session
        await assistant.start_session()
        await assistant.set_task("Demonstrate script orchestration")
        
        # Orchestrate multiple scripts in sequence
        scripts_to_run = [
            ("session_manager.py", ["start"], "📋 Starting session manager"),
            ("opencode_manager.py", ["status"], "🔍 Checking OpenCode status"),
            ("session_manager.py", ["quick-finish", "Orchestration demo", "All scripts executed successfully", "Continue with Phase 3", "Demo completed"], "💾 Saving session")
        ]
        
        results = []
        
        for script_name, args, description in scripts_to_run:
            print(f"\n{description}")
            print(f"🚀 Executing: {script_name} {' '.join(args)}")
            
            result = await assistant.execute_script(script_name, args)
            results.append(result)
            
            if result['status'] == 'success':
                print(f"✅ Success: {result['stdout'][:100]}...")
            else:
                print(f"❌ Error: {result.get('stderr', result.get('error', 'Unknown error'))}")
        
        # Summary
        print(f"\n📊 Orchestration Summary:")
        successful = sum(1 for r in results if r['status'] == 'success')
        print(f"✅ Successful: {successful}/{len(results)} scripts")
        
        # Complete task
        await assistant.complete_task(
            f"Successfully orchestrated {len(results)} scripts",
            "Move to final Phase 3 task"
        )
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
    
    finally:
        await assistant.shutdown()

if __name__ == "__main__":
    asyncio.run(demonstrate_orchestration())