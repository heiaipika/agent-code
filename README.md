# AI Agent Code Assistant

An intelligent code assistant based on LangChain/LangGraph with multi-tool integration, knowledge base management, and real-time conversation capabilities.

## Features

### 🤖 AI Assistant Features
- **Intelligent Conversation**: AI assistant based on LangChain supporting natural language interaction
- **Multi-tool Integration**: Integrated file operations, Shell commands, PowerShell and RAG query tools
- **Session Management**: Support for multiple session isolation with independent thread_id for each session

### 📚 Knowledge Base Management
- **Multi-knowledge Base Support**: Create, manage and switch between different knowledge bases
- **File Upload**: Support for TXT, PDF, DOCX, MD, CSV format file uploads
- **Vector Retrieval**: Intelligent retrieval based on Qdrant vector database
- **RAG Enhancement**: More accurate answers by combining knowledge base content

### 🎨 Frontend Interface
- **Modern UI**: Responsive interface based on Next.js and Tailwind CSS
- **Real-time Chat**: Smooth chat interface with message history
- **Knowledge Base Management**: Intuitive knowledge base creation, selection and file upload interface

## Tech Stack

### Backend
- **Python 3.8+**: Primary development language
- **FastAPI**: Web framework
- **LangChain/LangGraph**: AI Agent framework
- **Redis**: Session state storage
- **Qdrant**: Vector database
- **HuggingFace**: Text embedding model (all-MiniLM-L6-v2)

### Frontend
- **Next.js 15**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling framework
- **Lucide React**: Icon library
- **React Context**: State management

## Installation and Setup

### Requirements
- Python 3.8+
- Node.js 18+
- Redis
- Qdrant

### 1. Clone the project
```bash
git clone https://github.com/heiaipika/agent-code.git
```

### 2. Backend Setup

#### Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment variables configuration
Create `.env` file:
```bash
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
DEEPSEEK_API_KEY=api_key
UPLOAD_DIR=./uploads
```

#### Start backend service
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

#### Install Node.js dependencies
```bash
cd frontend
npm install
```

#### Start frontend service
```bash
cd frontend
npm run dev
```

## Usage Guide

### 1. Create Knowledge Base
1. Click the "Settings" button in the left sidebar
2. Click "Create knowledge base" to create a new knowledge base
3. Enter knowledge base name and description
4. Click "Create" to complete

### 2. Upload Files to Knowledge Base
1. Select target knowledge base in the knowledge base management interface
2. Click the file upload area to select files
3. Supported file formats: TXT, PDF, DOCX, MD, CSV
4. Click "Upload to knowledge base" to start upload

### 3. Start Conversation
1. Select the knowledge base to use in the left sidebar (optional)
2. Enter questions in the chat interface
3. AI assistant will answer by combining knowledge base content
4. Support for multi-turn conversations with automatic session state saving

### 4. Manage Sessions
- Click "New chat" to create a new session
- View session history in the left sidebar
- Click on sessions to switch
- Delete unnecessary sessions

## API Endpoints

### Chat API
- `POST /api/chat`: Send messages and get streaming responses

### Knowledge Base Management
- `GET /rag/knowledge-bases`: Get knowledge base list
- `POST /rag/knowledge-bases`: Create knowledge base
- `DELETE /rag/knowledge-bases/{kb_id}`: Delete knowledge base
- `POST /rag/upload`: Upload files to knowledge base
- `POST /rag/query`: Query knowledge base
