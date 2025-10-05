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
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Upload Document</h2>
        <p className="text-gray-600">
          Upload a Word document (.doc or .docx) for grammar and style analysis.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-error-400 flex-shrink-0" />
            <div className="ml-3">
              <p className="text-sm text-error-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Drop Zone */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-primary-400 bg-primary-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {selectedFile ? (
            <div className="space-y-2">
              <File className="h-12 w-12 text-primary-500 mx-auto" />
              <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
              <button
                type="button"
                onClick={handleReset}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Choose different file
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <Upload className="h-12 w-12 text-gray-400 mx-auto" />
              <p className="text-lg font-medium text-gray-900">
                {isDragActive ? 'Drop the file here' : 'Drag & drop your document here'}
              </p>
              <p className="text-sm text-gray-500">
                or click to browse files
              </p>
              <p className="text-xs text-gray-400">
                Supports .doc and .docx files up to 10MB
              </p>
            </div>
          )}
        </div>

        {/* Output Configuration */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="output-filename" className="block text-sm font-medium text-gray-700 mb-2">
              Output Filename
            </label>
            <input
              type="text"
              id="output-filename"
              value={outputFilename}
              onChange={(e) => setOutputFilename(e.target.value)}
              placeholder="Enter output filename"
              className="input-field"
              disabled={disabled}
            />
            <p className="mt-1 text-xs text-gray-500">
              The extension will be added automatically based on the output format.
            </p>
          </div>

          <div>
            <label htmlFor="output-format" className="block text-sm font-medium text-gray-700 mb-2">
              Output Format
            </label>
            <select
              id="output-format"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value as OutputFormatEnum)}
              className="input-field"
              disabled={disabled}
            >
              <option value={OutputFormatEnum.DOCX}>DOCX</option>
              <option value={OutputFormatEnum.PDF}>PDF</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Choose the format for your correction report.
            </p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!selectedFile || !outputFilename.trim() || disabled}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {disabled ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Start Analysis
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
