'use client';

import { useState, useEffect } from 'react';
import { Upload, File, X, Plus, Database, Trash2, Settings, Edit } from 'lucide-react';
import { useChatContext } from '@/lib/contexts/ChatContext';
import { 
  getKnowledgeBases, 
  createKnowledgeBase, 
  deleteKnowledgeBase, 
  uploadFileToKnowledgeBase,
  KnowledgeBase,
  CreateKnowledgeBaseRequest
} from '@/app/api/knowledge_base_api';

interface KnowledgeBaseManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function KnowledgeBaseManager({ isOpen, onClose }: KnowledgeBaseManagerProps) {
  const { refreshKnowledgeBases } = useChatContext();
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [selectedKbId, setSelectedKbId] = useState<string>('');
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loadingKb, setLoadingKb] = useState(true);
  const [selectionFeedback, setSelectionFeedback] = useState<string>('');
  
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creatingKb, setCreatingKb] = useState(false);
  const [newKbName, setNewKbName] = useState('');
  const [newKbDescription, setNewKbDescription] = useState('');

  const handleSelectKnowledgeBase = (kbId: string, kbName: string) => {
    setSelectedKbId(kbId);
    setSelectionFeedback(`Selected knowledge base: ${kbName}`);
    setTimeout(() => setSelectionFeedback(''), 2000);
  };

  const loadKnowledgeBases = async () => {
    try {
      setLoadingKb(true);
      const kbs = await getKnowledgeBases();
      setKnowledgeBases(kbs);
      if (kbs.length > 0 && !selectedKbId) {
        setSelectedKbId(kbs[0].id);
      }
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
    } finally {
      setLoadingKb(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadKnowledgeBases();
    }
  }, [isOpen]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleCreateKnowledgeBase = async () => {
    if (!newKbName.trim()) return;

    setCreatingKb(true);
    try {
      const request: CreateKnowledgeBaseRequest = {
        name: newKbName.trim(),
        description: newKbDescription.trim()
      };

      await createKnowledgeBase(request);
      
      await loadKnowledgeBases();
      await refreshKnowledgeBases();
      
      setNewKbName('');
      setNewKbDescription('');
      setShowCreateForm(false);
      
    } catch (error) {
      console.error('Failed to create knowledge base:', error);
      alert(`error to create knowledge base: ${error instanceof Error ? error.message : 'unknown error'}`);
    } finally {
      setCreatingKb(false);
    }
  };

  const handleDeleteKnowledgeBase = async (kbId: string, kbName: string) => {
    if (!confirm(`Are you sure you want to delete the knowledge base "${kbName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteKnowledgeBase(kbId);
      
      await loadKnowledgeBases();
      await refreshKnowledgeBases();
      
      if (selectedKbId === kbId) {
        if (knowledgeBases.length > 1) {
          const remainingKbs = knowledgeBases.filter(kb => kb.id !== kbId);
          setSelectedKbId(remainingKbs[0].id);
        } else {
          setSelectedKbId('');
        }
      }
      
    } catch (error) {
      console.error('Failed to delete knowledge base:', error);
      alert(`error to delete knowledge base: ${error instanceof Error ? error.message : 'unknown error'}`);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress('Preparing to upload...');

    try {
      setUploadProgress('Uploading file...');

      const result = await uploadFileToKnowledgeBase({
        file: selectedFile,
        kb_id: selectedKbId || undefined
      });
      
      console.log('Upload result:', result);
      
      setUploadProgress('File uploaded successfully, processing...');

      await loadKnowledgeBases();
      await refreshKnowledgeBases();
      
      setUploadProgress('Completed!');
      setTimeout(() => {
        setSelectedFile(null);
        setUploadProgress('');
        onClose();
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress(`Upload failed: ${error instanceof Error ? error.message : 'unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
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

        {/* knowledge base list */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Existing knowledge bases
            </h3>
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              <Plus className="w-3 h-3" />
              Create knowledge base
            </button>
          </div>
          
          {selectionFeedback && (
            <div className="mb-3 p-2 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-sm rounded-lg">
              {selectionFeedback}
            </div>
          )}

          {loadingKb ? (
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              Loading...
            </div>
          ) : knowledgeBases.length === 0 ? (
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              No knowledge bases yet
            </div>
          ) : (
            <div className="space-y-2">
              {knowledgeBases.map((kb) => (
                <div
                  key={kb.id}
                  className={`p-3 rounded-lg border transition-all duration-200 cursor-pointer ${
                    selectedKbId === kb.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700 shadow-sm'
                      : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleSelectKnowledgeBase(kb.id, kb.name);
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-sm font-medium px-2 py-1 rounded transition-all duration-200 ${
                            selectedKbId === kb.id
                              ? 'text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-900/30'
                              : 'text-gray-900 dark:text-white'
                          }`}
                        >
                          {kb.name}
                        </span>
                        {selectedKbId === kb.id && (
                          <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                            Selected
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {kb.description || 'No description'}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {kb.file_count} files · {kb.vector_count} vectors
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDeleteKnowledgeBase(kb.id, kb.name);
                      }}
                      className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors"
                      title="Delete knowledge base"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* create knowledge base form */}
        {showCreateForm && (
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Create new knowledge base
            </h4>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                  Knowledge base name *
                </label>
                <input
                  type="text"
                  value={newKbName}
                  onChange={(e) => setNewKbName(e.target.value)}
                  placeholder="Enter knowledge base name"
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-white"
                  disabled={creatingKb}
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                  Description
                </label>
                <textarea
                  value={newKbDescription}
                  onChange={(e) => setNewKbDescription(e.target.value)}
                  placeholder="Enter knowledge base description (optional)"
                  rows={2}
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-white"
                  disabled={creatingKb}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleCreateKnowledgeBase}
                  disabled={!newKbName.trim() || creatingKb}
                  className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded transition-colors"
                >
                  {creatingKb ? 'Creating...' : 'Create'}
                </button>
                <button
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewKbName('');
                    setNewKbDescription('');
                  }}
                  className="px-3 py-1 text-sm bg-gray-500 hover:bg-gray-600 text-white rounded transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* upload file to knowledge base */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Upload file to knowledge base
          </h3>
          
          {selectedKbId && (
            <div className="mb-3 p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                Current selected: <span className="font-medium">{knowledgeBases.find(kb => kb.id === selectedKbId)?.name}</span>
              </p>
            </div>
          )}
          
          {knowledgeBases.length === 0 ? (
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              Please create a knowledge base first
            </div>
          ) : (
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
                disabled={!selectedFile || uploading || !selectedKbId}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {uploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Uploading...
                  </>
                ) : !selectedKbId ? (
                  <>
                    <Database className="w-4 h-4" />
                    Please select a knowledge base first
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Upload to knowledge base
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 