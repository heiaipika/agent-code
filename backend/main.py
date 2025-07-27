
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.chat_api import app
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="AI Agent API Server")
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="API service host address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="API service port (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Enable hot reload"
    )
    
    args = parser.parse_args()
    
    print("🚀 Start AI Agent API Server...")
    print(f"API service will start at http://{args.host}:{args.port}")
    print("API documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.api.chat_api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API service has stopped")
    except Exception as e:
        print(f"❌ API service startup failed: {e}")

if __name__ == "__main__":
    main() 