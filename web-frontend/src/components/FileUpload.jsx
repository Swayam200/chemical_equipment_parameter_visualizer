import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import api, { formatErrorMessage, MAX_FILE_SIZE, MAX_FILE_SIZE_DISPLAY } from '../api';
import { FaCloudUploadAlt, FaSpinner, FaCheckCircle, FaExclamationCircle, FaFile } from 'react-icons/fa';

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
        // Handle rejected files (wrong type)
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

        // File size validation
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
        <div className="glass-card">
            <h2>Upload Data</h2>
            <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
                <input {...getInputProps()} />
                {uploading ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', width: '100%' }}>
                        <FaSpinner className="spin" size={32} />
                        <p style={{ margin: 0 }}>
                            <FaFile style={{ marginRight: '8px' }} />
                            {fileName}
                        </p>

                        {/* Progress Bar */}
                        <div style={{
                            width: '80%',
                            maxWidth: '300px',
                            height: '8px',
                            backgroundColor: 'var(--border-color)',
                            borderRadius: '4px',
                            overflow: 'hidden'
                        }}>
                            <div style={{
                                width: `${uploadProgress}%`,
                                height: '100%',
                                backgroundColor: 'var(--accent-color)',
                                transition: 'width 0.3s ease',
                                borderRadius: '4px'
                            }} />
                        </div>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                            {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Processing data...'}
                        </p>
                    </div>
                ) : success ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', color: 'var(--success)' }}>
                        <FaCheckCircle size={32} />
                        <p>Upload Successful!</p>
                    </div>
                ) : error ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', color: 'var(--danger)' }}>
                        <FaExclamationCircle size={32} />
                        <p style={{ textAlign: 'center', maxWidth: '400px' }}>{error}</p>
                        <p style={{ fontSize: '0.8rem' }}>Click to try again</p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                        <FaCloudUploadAlt size={48} />
                        <p>Drag & drop a CSV file here, or click to select</p>
                        <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                            Requires columns: Equipment Name, Type, Flowrate, Pressure, Temperature
                        </p>
                        <p style={{ fontSize: '0.75rem', opacity: 0.5, marginTop: '8px' }}>
                            Maximum file size: {MAX_FILE_SIZE_DISPLAY}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;
