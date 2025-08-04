
export interface ChatRequest {
  message: string;
  kb_id?: string;
  thread_id?: string;
}

export interface ChatResponse {
  content: string;
  type: 'thinking' | 'tool_result' | 'kb_info' | 'error';
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  file_count: number;
  vector_count: number;
}

export interface KnowledgeBasesResponse {
  knowledge_bases: KnowledgeBase[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function streamChat(
  message: string,
  onChunk: (chunk: ChatResponse) => void,
  kb_id?: string,
  thread_id?: string,
  onError?: (error: string) => void
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        kb_id,
        thread_id,
      } as ChatRequest),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; 
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); 
          
          if (data === '[DONE]') {
            return;
          }
          
          try {
            const parsed = JSON.parse(data);
            onChunk(parsed);
          } catch (e) {
            console.warn('Failed to parse SSE data:', data);
          }
        }
      }
    }
  } catch (error) {
    console.error('Stream chat error:', error);
    onError?.(error instanceof Error ? error.message : 'Unknown error');
  }
}

export async function getKnowledgeBases(): Promise<KnowledgeBasesResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/knowledge-bases`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get knowledge bases error:', error);
    throw error;
  }
}
