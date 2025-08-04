
export interface ChatRequest {
  message: string;
  thread_id?: string;
}

export interface ChatResponse {
  content: string;
  type: 'thinking' | 'tool_result' | 'kb_info' | 'DONE';
  error?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function streamChat(
  message: string,
  onChunk: (chunk: ChatResponse) => void,
  kbId?: string,
  threadId?: string,
  onError?: (error: string) => void
): Promise<void> {
  try {
    console.log('streamChat called with:', { message, kbId, threadId });
    
    const requestBody = {
      message,
      kb_id: kbId,
      thread_id: threadId,
    };
    
    console.log('Request body:', JSON.stringify(requestBody));
    
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', errorText);
      onError?.(`HTTP ${response.status}: ${errorText}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError?.('No response body');
      return;
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
            onChunk({ content: '', type: 'DONE' });
            return;
          }

          try {
            const parsed = JSON.parse(data);
            console.log('Parsed chunk:', parsed);
            onChunk(parsed);
          } catch (e) {
            console.error('Failed to parse chunk:', data, e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Stream chat error:', error);
    onError?.(error instanceof Error ? error.message : 'Unknown error');
  }
}
