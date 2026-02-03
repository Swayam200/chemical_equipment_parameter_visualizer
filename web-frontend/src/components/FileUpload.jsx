import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import api, { formatErrorMessage, MAX_FILE_SIZE, MAX_FILE_SIZE_DISPLAY } from '../api';

const FileUpload = ({ onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [fileName, setFileName] = useState('');

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    };

    const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
        if (rejectedFiles.length > 0) {
            const rejection = rejectedFiles[0];
            if (rejection.errors[0]?.code === 'file-invalid-type') {
                setError('Invalid file type. Only CSV files are accepted.');
            } else {
                setError(rejection.errors[0]?.message || 'File rejected');
            }
            return;
        }

        const file = acceptedFiles[0];
        if (!file) return;

        if (file.size > MAX_FILE_SIZE) {
            setError(`File too large (${formatFileSize(file.size)}). Maximum size is ${MAX_FILE_SIZE_DISPLAY}.`);
            return;
        }

        setFileName(file.name);
        setUploading(true);
        setError(null);
        setSuccess(false);
        setUploadProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    setUploadProgress(percentCompleted);
                },
            });
            setSuccess(true);
            setUploadProgress(100);
            onUploadSuccess(response.data);
            setTimeout(() => {
                setSuccess(false);
                setUploadProgress(0);
                setFileName('');
            }, 3000);
        } catch (err) {
            console.error(err);
            setError(formatErrorMessage(err));
        } finally {
            setUploading(false);
        }
    }, [onUploadSuccess]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'text/csv': ['.csv'] },
        multiple: false,
        maxSize: MAX_FILE_SIZE,
    });

    return (
        <div className="w-full">
            <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${isDragActive
                        ? 'border-primary bg-primary/10'
                        : 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:border-primary/50 dark:hover:border-primary/50'
                    }`}
            >
                <input {...getInputProps()} />
                {uploading ? (
                    <div className="flex flex-col items-center gap-3">
                        <span className="material-symbols-outlined text-4xl text-primary animate-spin">progress_activity</span>
                        <p className="font-medium text-slate-700 dark:text-slate-200 flex items-center gap-2">
                            <span className="material-symbols-outlined text-base">description</span>
                            {fileName}
                        </p>

                        <div className="w-full max-w-xs h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden mt-2">
                            <div
                                className="h-full bg-primary transition-all duration-300 rounded-full"
                                style={{ width: `${uploadProgress}%` }}
                            />
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Processing data...'}
                        </p>
                    </div>
                ) : success ? (
                    <div className="flex flex-col items-center gap-2 text-green-600 dark:text-green-500">
                        <span className="material-symbols-outlined text-4xl">check_circle</span>
                        <p className="font-semibold">Upload Successful!</p>
                    </div>
                ) : error ? (
                    <div className="flex flex-col items-center gap-2 text-red-600 dark:text-red-500">
                        <span className="material-symbols-outlined text-4xl">error</span>
                        <p className="font-medium max-w-xs">{error}</p>
                        <p className="text-xs opacity-75">Click to try again</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-3">
                        <span className="material-symbols-outlined text-5xl text-slate-400 dark:text-slate-500 mb-2">cloud_upload</span>
                        <p className="text-lg font-semibold text-slate-700 dark:text-slate-200">Drag & drop CSV file</p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">or click to browse</p>
                        <p className="text-xs text-slate-400 dark:text-slate-500 mt-4">
                            Max size: {MAX_FILE_SIZE_DISPLAY}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;
