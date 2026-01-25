import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import api from '../api';
import { FaCloudUploadAlt, FaSpinner, FaCheckCircle, FaExclamationCircle } from 'react-icons/fa';

const FileUpload = ({ onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const onDrop = useCallback(async (acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        setUploading(true);
        setError(null);
        setSuccess(false);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setSuccess(true);
            onUploadSuccess(response.data);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            console.error(err);
            setError("Upload failed. Please try again.");
        } finally {
            setUploading(false);
        }
    }, [onUploadSuccess]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'text/csv': ['.csv'] },
        multiple: false
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
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                        <FaSpinner className="spin" size={32} />
                        <p>Processing CSV...</p>
                    </div>
                ) : success ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', color: 'var(--success)' }}>
                        <FaCheckCircle size={32} />
                        <p>Upload Successful!</p>
                    </div>
                ) : error ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', color: 'var(--danger)' }}>
                        <FaExclamationCircle size={32} />
                        <p>{error}</p>
                        <p style={{ fontSize: '0.8rem' }}>Click to try again</p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                        <FaCloudUploadAlt size={48} />
                        <p>Drag & drop a CSV file here, or click to select</p>
                        <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>Requires columns: Equipment Name, Type, Flowrate, Pressure, Temperature</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;
