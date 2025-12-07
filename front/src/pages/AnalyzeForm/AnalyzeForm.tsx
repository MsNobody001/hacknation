import React, { useState, useCallback, useMemo } from 'react';
import { Upload, FileText, CheckCircle, XCircle, Loader2, Trash2, AlertTriangle, FileUp } from 'lucide-react';
import { UploadFile } from '@/types';
import { formatFileSize } from '@/utils';
import { analyzeService, FormalAnalysisResponse } from '@/services/analyze';

const ATTEMPTS = 500000;

const ChunkLoader: React.FC = () => (
  <div className=" inset-0 backdrop-blur-sm flex flex-col items-center justify-center z-10 p-4 rounded-xl">
    <Loader2 className="w-10 h-10 text-green-600 animate-spin mb-3" />
    <p className="text-lg font-semibold text-gray-800">Trwa analiza...</p>
    <p className="text-sm text-gray-500">Proszę czekać.</p>
  </div>
);

const FileItem: React.FC<{ file: UploadFile; onRemove: (id: string) => void }> = ({ file, onRemove }) => {
  // Determine icon based on status
  const Icon = useMemo(() => {
    switch (file.status) {
      case 'complete':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'uploading':
        return <FileUp className="w-6 h-6 text-indigo-500" />;
      default:
        return <FileText className="w-6 h-6 text-gray-400" />;
    }
  }, [file.status]);

  return (
    <div className="relative flex flex-col p-4 border border-gray-200 rounded-xl bg-white shadow-sm hover:shadow-lg transition duration-150">
      {/* Top section */}
      <div className="flex justify-between items-center">
        <div className="p-2 rounded-lg bg-gray-50">{Icon}</div>

        {/* File name + size */}
        <div className="flex-grow">
          <p className="text-sm font-medium text-gray-800 truncate" title={file.name}>
            {file.name}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">{formatFileSize(file.size)}</p>
        </div>

        {/* Remove button */}
        <button
          onClick={() => onRemove(file.id)}
          className="p-1 rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 transition"
          aria-label={`Remove ${file.name}`}
        >
          <Trash2 size={25} className="w-4 h-4" />
        </button>
      </div>

      <div className="mt-auto">
        {/* Error message */}
        {file.status === 'error' && (
          <div className="mt-2 text-xs text-red-600 flex items-center">
            <AlertTriangle className="w-3 h-3 mr-1" /> Błąd wgrywania
          </div>
        )}
      </div>
    </div>
  );
};

export const AnalyzeForm: React.FC = () => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [maxUploadsReached, setMaxUploadsReached] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisRes, setAnalysisRes] = useState<FormalAnalysisResponse | undefined>(undefined);

  const MAX_FILES = 5;

  const addFiles = useCallback(
    (fileList: FileList) => {
      const newFiles: UploadFile[] = [];
      let currentFileCount = files.filter(f => f.status !== 'complete').length;

      for (const file of fileList) {
        if (file.type === 'application/pdf' && currentFileCount < MAX_FILES) {
          newFiles.push({
            id: crypto.randomUUID(),
            name: file.name,
            size: file.size,
            status: 'pending',
            progress: 0,
            file: file,
          });
          currentFileCount++;
        }
      }

      const filesExceeded = currentFileCount >= MAX_FILES;
      setMaxUploadsReached(filesExceeded);

      setFiles(prevFiles => {
        const updatedFiles = [...prevFiles, ...newFiles];
        // Keep only the most recent files up to MAX_FILES if needed, but the check above should handle it
        return updatedFiles;
      });

      // Show alert temporarily if no files were added due to limit/type
      if (newFiles.length === 0 && fileList.length > 0) {
        if (filesExceeded) {
          setTimeout(() => setMaxUploadsReached(false), 3000);
        }
      }
    },
    [files]
  );

  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      if (event.target.files) {
        addFiles(event.target.files);
        event.target.value = '';
      }
    },
    [addFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);
      if (e.dataTransfer.files) {
        addFiles(e.dataTransfer.files);
      }
    },
    [addFiles]
  );

  const handleRemoveFile = useCallback((id: string) => {
    setFiles(prevFiles => {
      const updatedFiles = prevFiles.filter(file => file.id !== id);
      const pendingCount = updatedFiles.filter(f => f.status === 'pending' || f.status === 'uploading').length;
      if (pendingCount < MAX_FILES) {
        setMaxUploadsReached(false);
      }
      return updatedFiles;
    });
  }, []);

  // Update file status function (if needed for the analyzeService mock/real implementation)
  //   const updateFileStatus = useCallback((id: string, update: Partial<UploadFile>) => {
  //     setFiles(prevFiles => prevFiles.map(file => (file.id === id ? { ...file, ...update } : file)));
  //   }, []);

  const handleUploadAll = async () => {
    if (isUploading) return;
    setIsUploading(true);

    const filesToUpload = files.filter(f => f.status === 'pending' || f.status === 'error');
    if (filesToUpload.length === 0) {
      setIsUploading(false);
      return;
    }

    // Use analyzeService.uploadFiles to handle the actual upload and final status updates
    const createdAnalyze = await analyzeService.create();
    await analyzeService
      .uploadFiles(
        createdAnalyze.id,
        filesToUpload.map(f => f.file)
      )
      .then(() => {
        // Set all files currently in 'uploading' status to 'complete'
        setFiles(prevFiles =>
          prevFiles.map(file => {
            if (file.status === 'uploading') {
              return { ...file, status: 'complete', progress: 100 };
            }
            return file;
          })
        );
      })
      .catch(() => {
        // Set all files currently in 'uploading' status to 'error'
        setFiles(prevFiles =>
          prevFiles.map(file => {
            if (file.status === 'uploading') {
              return { ...file, status: 'error', progress: 0 };
            }
            return file;
          })
        );
      })
      .finally(() => {
        setIsUploading(false);
      });

    await analyzeService.processing(createdAnalyze.id);
    setAnalyzing(true);

    let attempt = 0;
    for (; attempt <= ATTEMPTS; attempt++) {
      try {
        await new Promise(res => setTimeout(res, 2000));
        const result = await analyzeService.status(createdAnalyze.id);
        if (result.status === 'completed') {
          break; // Exit loop if successful
        } else if (result.status === 'failed') {
          console.error('Failed to get formal analysis after maximum attempts');
        }
      } catch (error) {
        console.error('Failed to get formal analysis after maximum attempts');
      }
    }

    setAnalyzing(false);
    try {
      const analysis = await analyzeService.getFormalAnalysis(createdAnalyze.id);
      setAnalysisRes(analysis);
      console.log('Formal Analysis:', analysis);
    } catch {
      setAnalysisRes({
        qualifies_as_work_accident: false,
        overall_conclusion: 'Błąd podczas analizy formalnej.',
        recommendations: 'Proszę spróbować ponownie później.',
      });
    }
  };

  const pendingFilesCount = files.filter(f => f.status === 'pending' || f.status === 'error').length;
  const isUploadButtonDisabled = isUploading || pendingFilesCount === 0;

  return (
    <div className="bg-gray-100 flex items-start justify-center p-4 sm:p-8 font-sans">
      <div className="w-full max-w-4xl bg-white p-6 sm:p-8 rounded-xl shadow-2xl">
        {!analyzing && (
          <>
            <h1 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">Wgraj pliki PDF do analizy</h1>

            {/* File Drop Area */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
            flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-colors duration-200
            ${isDragOver ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'}
          `}
            >
              <input
                id="file-upload"
                type="file"
                multiple
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
                disabled={isUploading}
              />
              <Upload className="w-10 h-10 text-gray-500 mb-3" />
              <p className="text-lg font-semibold text-gray-800">Przeciągnij i upuść pliki PDF tutaj</p>
              <p className="text-sm text-gray-500 mb-4">
                lub kliknij, aby przeglądać. Maks. {MAX_FILES} plików (.pdf).
              </p>
              <label
                htmlFor="file-upload"
                className={`
              px-6 py-2 text-white font-medium rounded-full shadow-md transition-transform duration-150 ease-in-out cursor-pointer
              ${isUploading ? 'bg-green-300 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 active:scale-95'}
            `}
              >
                Wgraj plik
              </label>
            </div>

            {/* Max Uploads Warning */}
            {maxUploadsReached && (
              <div className="mt-4 p-3 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 rounded-lg flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0" />
                <p className="text-sm">
                  Osiągnięto **maksymalną liczbę {MAX_FILES} plików** w kolejce. Usuń pliki lub poczekaj na zakończenie
                  wysyłania.
                </p>
              </div>
            )}

            {/* File List and Upload Button */}
            {files.length > 0 && (
              <div className="mt-8">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Queue ({files.length})</h2>

                {/* Shared loader for chunk of files */}
                {files.some(f => f.status === 'uploading') && (
                  <div className="flex justify-center items-center mb-4">
                    <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
                    <span className="ml-2 text-indigo-600 font-medium">Uploading files…</span>
                  </div>
                )}

                {/* Grid layout for file items */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-80 overflow-y-auto pr-2">
                  {files.map(file => (
                    <FileItem key={file.id} file={file} onRemove={handleRemoveFile} />
                  ))}
                </div>

                {/* Upload Button */}
                <button
                  onClick={handleUploadAll}
                  disabled={isUploadButtonDisabled}
                  className={`
                w-full mt-6 py-3 px-4 text-white font-semibold rounded-lg shadow-lg transition duration-200 flex items-center justify-center
                ${
                  isUploadButtonDisabled
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 active:scale-[0.98] focus:ring-4 focus:ring-green-500/50'
                }
              `}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Wysyłanie wszystkich...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5 mr-2" />
                      Rozpocznij Wysyłanie ({pendingFilesCount} Plików)
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Empty State */}
            {files.length === 0 && (
              <div className="mt-8 p-10 text-center bg-gray-50 border border-gray-200 rounded-xl text-gray-500">
                <FileText className="w-8 h-8 mx-auto mb-3" />
                <p className="text-base">Nie wybrano plików.</p>
              </div>
            )}

            {analysisRes && (
              <div className="mt-8 p-10 text-center bg-gray-50 border border-gray-200 rounded-xl text-gray-500">
                <p className="text-base">
                  {analysisRes.qualifies_as_work_accident ? 'Zakwalifikowano' : 'Nie zakwalifikowano'}
                </p>
                <p className="text-base">{analysisRes.overall_conclusion}</p>
                <p className="text-base">{analysisRes.recommendations}.</p>
              </div>
            )}
          </>
        )}

        {analyzing && <ChunkLoader />}
      </div>
    </div>
  );
};
