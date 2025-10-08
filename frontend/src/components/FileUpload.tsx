import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { File, Upload, AlertCircle } from 'lucide-react';
import { OutputFormatEnum } from '../types';

interface FileUploadProps {
  onFileUpload: (file: File, outputFilename: string, outputFormat: OutputFormatEnum) => void;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, disabled = false }) => {
  const [outputFilename, setOutputFilename] = useState('');
  const [outputFormat, setOutputFormat] = useState<OutputFormatEnum>(OutputFormatEnum.DOCX);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Please upload a .doc or .docx file only.');
      } else if (rejection.errors[0]?.code === 'file-too-large') {
        setError('File size must be less than 10MB.');
      } else {
        setError('Invalid file. Please try again.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      
      // Set default output filename if not provided
      if (!outputFilename) {
        const baseName = file.name.replace(/\.[^/.]+$/, '');
        setOutputFilename(`${baseName}_corrected`);
      }
    }
  }, [outputFilename]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    disabled
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    if (!outputFilename.trim()) {
      setError('Please enter an output filename.');
      return;
    }

    onFileUpload(selectedFile, outputFilename.trim(), outputFormat);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setOutputFilename('');
    setError(null);
  };

  return (
    <div>
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* File Drop Zone */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-gray-900 bg-gray-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {selectedFile ? (
            <div className="space-y-2">
              <File className="h-10 w-10 text-gray-700 mx-auto" />
              <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-xs text-gray-500">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
              <button
                type="button"
                onClick={handleReset}
                className="text-xs text-gray-600 hover:text-gray-900"
              >
                Change file
              </button>
            </div>
          ) : (
            <div className="space-y-1">
              <Upload className="h-10 w-10 text-gray-400 mx-auto" />
              <p className="text-sm text-gray-700">
                {isDragActive ? 'Drop file here' : 'Drop file or click to browse'}
              </p>
              <p className="text-xs text-gray-500">
                .doc, .docx up to 10MB
              </p>
            </div>
          )}
        </div>

        {/* Output Configuration */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="output-filename" className="block text-xs font-medium text-gray-700 mb-1">
              Output Name
            </label>
            <input
              type="text"
              id="output-filename"
              value={outputFilename}
              onChange={(e) => setOutputFilename(e.target.value)}
              placeholder="filename"
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-gray-900"
              disabled={disabled}
            />
          </div>

          <div>
            <label htmlFor="output-format" className="block text-xs font-medium text-gray-700 mb-1">
              Format
            </label>
            <select
              id="output-format"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value as OutputFormatEnum)}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-gray-900"
              disabled={disabled}
            >
              <option value={OutputFormatEnum.DOCX}>DOCX</option>
              <option value={OutputFormatEnum.PDF}>PDF</option>
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedFile || !outputFilename.trim() || disabled}
          className="w-full bg-gray-900 text-white py-2 px-4 rounded text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? 'Processing...' : 'Analyze'}
        </button>
      </form>
    </div>
  );
};
