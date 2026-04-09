import { useState, useEffect, useRef } from 'react';
import { FileText, Upload, Trash2, Folder, FileDigit, X } from 'lucide-react';
import { apiClient } from '../api';
import { Button, Card, StatCard } from '../components';
import type { CollectionStats } from '../types';

export function DocumentsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [chunkSize, setChunkSize] = useState(1000);
  const [chunkOverlap, setChunkOverlap] = useState(200);
  const [isLoading, setIsLoading] = useState(false);
  const [collections, setCollections] = useState<CollectionStats[]>([]);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    errors?: string[];
  } | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await apiClient.getDocumentStats();
      if (response.success) {
        setCollections(response.collections);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setResult({
        success: false,
        message: '请先选择一个文件',
      });
      return;
    }

    // 检查文件类型
    const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.json', '.py', '.js', '.ts', '.html', '.css'];
    const fileExt = '.' + selectedFile.name.split('.').pop()?.toLowerCase();
    
    if (!allowedExtensions.includes(fileExt)) {
      setResult({
        success: false,
        message: `不支持的文件类型: ${fileExt}。支持的类型: ${allowedExtensions.join(', ')}`,
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const response = await apiClient.uploadDocument(selectedFile, chunkSize, chunkOverlap);

      if (response.success) {
        setResult({
          success: true,
          message: `导入成功！处理了 ${response.processed_chunks} 个片段`,
          errors: response.errors,
        });
        clearFile();
        loadStats();
      } else {
        setResult({
          success: false,
          message: response.errors?.[0] || '导入失败',
          errors: response.errors,
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : '未知错误',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const totalDocs = collections.reduce((sum, c) => sum + (c.count || 0), 0);

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="h-full overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-5 border-b border-apple-border bg-apple-surface">
        <h1 className="text-2xl font-bold text-apple-text flex items-center gap-2">
          <FileText className="w-6 h-6" />
          文档管理
        </h1>
        <p className="text-sm text-apple-text-secondary mt-1">
          上传文档到知识库，支持拖拽上传
        </p>
      </div>

      <div className="p-6 max-w-6xl mx-auto space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            title="集合数量"
            value={collections.length}
            icon={<Folder className="w-5 h-5 text-apple-blue" />}
          />
          <StatCard
            title="文档片段"
            value={totalDocs.toLocaleString()}
            icon={<FileDigit className="w-5 h-5 text-apple-blue" />}
          />
          <StatCard
            title="知识库状态"
            value="正常"
            icon={<FileText className="w-5 h-5 text-apple-blue" />}
          />
        </div>

        {/* Upload Area */}
        <Card padding="lg">
          <h2 className="text-lg font-semibold text-apple-text mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5" />
            上传文档
          </h2>

          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`
              relative border-2 border-dashed rounded-apple-lg p-8 text-center cursor-pointer
              transition-all duration-200
              ${isDragOver 
                ? 'border-apple-blue bg-apple-blue-light/30' 
                : 'border-apple-border hover:border-apple-blue hover:bg-apple-gray/50'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.docx,.doc,.txt,.md,.json,.py,.js,.ts,.html,.css"
              className="hidden"
            />
            
            {selectedFile ? (
              <div className="flex items-center justify-center gap-3">
                <div className="w-12 h-12 rounded-apple bg-apple-blue-light flex items-center justify-center">
                  <FileText className="w-6 h-6 text-apple-blue" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-apple-text">{selectedFile.name}</p>
                  <p className="text-sm text-apple-text-secondary">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    clearFile();
                  }}
                  className="ml-4 p-1 hover:bg-apple-gray rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-apple-text-secondary" />
                </button>
              </div>
            ) : (
              <>
                <div className="w-16 h-16 rounded-full bg-apple-gray flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-8 h-8 text-apple-text-secondary" />
                </div>
                <p className="text-apple-text font-medium mb-1">
                  点击或拖拽文件到此处上传
                </p>
                <p className="text-sm text-apple-text-secondary">
                  支持 PDF, Word, TXT, Markdown, JSON, 代码文件等
                </p>
              </>
            )}
          </div>

          {/* Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1.5">
                分块大小
              </label>
              <input
                type="number"
                min={100}
                max={2000}
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                className="w-full px-4 py-2 bg-apple-surface border border-apple-border rounded-apple focus:outline-none focus:ring-2 focus:ring-apple-blue"
              />
              <p className="text-xs text-apple-text-secondary mt-1">
                每个文档片段的最大字符数
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1.5">
                重叠大小
              </label>
              <input
                type="number"
                min={0}
                max={500}
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(Number(e.target.value))}
                className="w-full px-4 py-2 bg-apple-surface border border-apple-border rounded-apple focus:outline-none focus:ring-2 focus:ring-apple-blue"
              />
              <p className="text-xs text-apple-text-secondary mt-1">
                相邻片段之间的重叠字符数
              </p>
            </div>
          </div>

          {/* Upload Button */}
          <Button
            onClick={handleUpload}
            isLoading={isLoading}
            disabled={!selectedFile}
            className="w-full mt-6"
          >
            <Upload className="w-4 h-4" />
            {isLoading ? '上传中...' : '开始导入'}
          </Button>

          {/* Result */}
          {result && (
            <div
              className={`mt-4 p-4 rounded-apple ${
                result.success
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              <p className="font-medium">
                {result.success ? '✅ 成功' : '❌ 错误'}
              </p>
              <p className="text-sm mt-1">{result.message}</p>
              {result.errors && result.errors.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm font-medium">错误详情:</p>
                  <ul className="text-xs mt-1 space-y-0.5">
                    {result.errors.map((err, i) => (
                      <li key={i}>· {err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Collections List */}
        <div>
          <h2 className="text-lg font-semibold text-apple-text mb-4">知识库概览</h2>
          {collections.length > 0 ? (
            <div className="grid grid-cols-1 gap-3">
              {collections.map((coll) => (
                <Card
                  key={coll.name}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-apple-blue-light flex items-center justify-center">
                      <Folder className="w-5 h-5 text-apple-blue" />
                    </div>
                    <div>
                      <p className="font-medium text-apple-text">{coll.name}</p>
                      <p className="text-sm text-apple-text-secondary">
                        包含 {coll.count?.toLocaleString() || 0} 个文档片段
                      </p>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="text-center py-12">
              <div className="w-16 h-16 rounded-full bg-apple-gray flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-apple-text-secondary" />
              </div>
              <h3 className="text-lg font-medium text-apple-text mb-2">
                知识库为空
              </h3>
              <p className="text-sm text-apple-text-secondary">
                还没有导入任何文档，使用上方上传区域添加您的第一个文档
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
