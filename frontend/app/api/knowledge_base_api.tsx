export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  file_count: number;
  vector_count: number;
  created_at: string;
  updated_at: string;
  status: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;
  description: string;
}

export interface UploadFileRequest {
  file: File;
  kb_id?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/rag/knowledge-bases`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get knowledge bases error:', error);
    throw error;
  }
}

export async function createKnowledgeBase(request: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
  try {
    const response = await fetch(`${API_BASE_URL}/rag/knowledge-bases`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create knowledge base');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Create knowledge base error:', error);
    throw error;
  }
}

export async function deleteKnowledgeBase(kbId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/rag/knowledge-bases/${kbId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to delete knowledge base');
    }
  } catch (error) {
    console.error('Delete knowledge base error:', error);
    throw error;
  }
}

export async function uploadFileToKnowledgeBase(request: UploadFileRequest): Promise<any> {
  try {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.kb_id) {
      formData.append('kb_id', request.kb_id);
    }

    const response = await fetch(`${API_BASE_URL}/rag/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Upload failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Upload file error:', error);
    throw error;
  }
} 