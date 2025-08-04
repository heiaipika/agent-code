'use client';

import { useState } from 'react';
import { Upload, File, X, Plus, Database } from 'lucide-react';
import { useChatContext } from '@/lib/contexts/ChatContext';

interface KnowledgeBaseManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function KnowledgeBaseManager({ isOpen, onClose }: KnowledgeBaseManagerProps) {
  const { knowledgeBases, refreshKnowledgeBases } = useChatContext();
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<string>('');

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress('Preparing to upload...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      setUploadProgress('Uploading file...');

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      setUploadProgress('File uploaded successfully, processing...');

      await refreshKnowledgeBases();
      
      setUploadProgress('Completed!');
      setTimeout(() => {
        setSelectedFile(null);
        setUploadProgress('');
        onClose();
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress('Upload failed, please try again');
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Database className="w-5 h-5" />
            Knowledge base manager
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Knowledge base list */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Existing knowledge bases
          </h3>
          {knowledgeBases.length === 0 ? (
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              No knowledge base yet
            </div>
          ) : (
            <div className="space-y-2">
              {knowledgeBases.map((kb) => (
                <div
                  key={kb.id}
                  className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {kb.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {kb.file_count} files · {kb.vector_count} vectors
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* File upload */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Upload file to knowledge base
          </h3>
          
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4">
              <input
                type="file"
                onChange={handleFileSelect}
                accept=".txt,.pdf,.docx,.md,.csv"
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <Upload className="w-8 h-8 text-gray-400" />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Click to select a file or drag and drop here
                </span>
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  Supports TXT, PDF, DOCX, MD, CSV formats
                </span>
              </label>
            </div>

            {selectedFile && (
              <div className="flex items-center gap-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <File className="w-4 h-4 text-blue-600" />
                <span className="text-sm text-blue-700 dark:text-blue-300 flex-1">
                  {selectedFile.name}
                </span>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="p-1 rounded hover:bg-blue-100 dark:hover:bg-blue-800"
                >
                  <X className="w-3 h-3 text-blue-600" />
                </button>
              </div>
            )}

            {uploadProgress && (
              <div className="text-sm text-gray-600 dark:text-gray-400 text-center">
                {uploadProgress}
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Upload to knowledge base
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 