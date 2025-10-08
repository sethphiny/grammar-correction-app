import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { File, Upload, AlertCircle } from 'lucide-react';
import { OutputFormatEnum } from '../types';
import { apiClient } from '../services/api';

interface Category {
  id: string;
  name: string;
}

interface FileUploadProps {
  onFileUpload: (file: File, outputFilename: string, outputFormat: OutputFormatEnum, categories: string[]) => void;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, disabled = false }) => {
  const [outputFilename, setOutputFilename] = useState('');
  const [outputFormat, setOutputFormat] = useState<OutputFormatEnum>(OutputFormatEnum.DOCX);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(true);

  // Fetch available categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await apiClient.get('/categories');
        const cats = response.data.categories;
        setCategories(cats);
        // Select all by default
        setSelectedCategories(new Set(cats.map((c: Category) => c.id)));
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };
    fetchCategories();
  }, []);

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

  const toggleCategory = (categoryId: string) => {
    const newSelected = new Set(selectedCategories);
    if (newSelected.has(categoryId)) {
      newSelected.delete(categoryId);
    } else {
      newSelected.add(categoryId);
    }
    setSelectedCategories(newSelected);
    setSelectAll(newSelected.size === categories.length);
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedCategories(new Set());
      setSelectAll(false);
    } else {
      setSelectedCategories(new Set(categories.map(c => c.id)));
      setSelectAll(true);
    }
  };

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

    if (selectedCategories.size === 0) {
      setError('Please select at least one category to analyze.');
      return;
    }

    onFileUpload(selectedFile, outputFilename.trim(), outputFormat, Array.from(selectedCategories));
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

        {/* Category Selection */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-2">
            Select Categories to Analyze
          </label>
          <div className="border border-gray-300 rounded p-3 space-y-2 max-h-64 overflow-y-auto">
            {/* Select All */}
            <label className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
              <input
                type="checkbox"
                checked={selectAll}
                onChange={handleSelectAll}
                disabled={disabled}
                className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
              />
              <span className="text-sm font-medium text-gray-900">Select All</span>
            </label>
            <div className="border-t border-gray-200 my-2"></div>
            {/* Individual Categories */}
            {categories.map((category) => (
              <label
                key={category.id}
                className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
              >
                <input
                  type="checkbox"
                  checked={selectedCategories.has(category.id)}
                  onChange={() => toggleCategory(category.id)}
                  disabled={disabled}
                  className="w-4 h-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                />
                <span className="text-sm text-gray-700">{category.name}</span>
              </label>
            ))}
          </div>
          {selectedCategories.size > 0 && (
            <p className="text-xs text-gray-500 mt-1">
              {selectedCategories.size} {selectedCategories.size === 1 ? 'category' : 'categories'} selected
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedFile || !outputFilename.trim() || selectedCategories.size === 0 || disabled}
          className="w-full bg-gray-900 text-white py-2 px-4 rounded text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? 'Processing...' : 'Analyze'}
        </button>
      </form>
    </div>
  );
};
