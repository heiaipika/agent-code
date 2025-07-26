
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agent.code_agent import run_agent
import asyncio

if __name__ == "__main__":
    print("🚀 Start Code Agent...")
    print("Based on SiliconFlow DeepSeek model")
    print("Input 'exit' to exit the program")
    print("=" * 50)
    
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\n👋 The program has exited")
    except Exception as e:
        print(f"❌ Error running: {e}") 