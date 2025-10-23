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
  onFileUpload: (file: File, outputFilename: string, outputFormat: OutputFormatEnum, categories: string[], useLLMEnhancement: boolean, useLLMDetection: boolean, useFullLLM: boolean) => void;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, disabled = false }) => {
  const [outputFilename, setOutputFilename] = useState('');
  const [outputFormat, setOutputFormat] = useState<OutputFormatEnum>(OutputFormatEnum.DOCX);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(false);
  const [aiMode, setAiMode] = useState<'free' | 'competitive' | 'premium' | 'ultra'>('competitive'); // Default to competitive
  const [useLLMEnhancement, setUseLLMEnhancement] = useState(true);
  const [useLLMDetection, setUseLLMDetection] = useState(false); // Default OFF for speed
  const [useFullLLM, setUseFullLLM] = useState(false); // Pure LLM mode

  // Fetch available categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await apiClient.get('/categories');
        const cats = response.data.categories;
        setCategories(cats);
        // Select essential categories by default for better user experience
        const essentialCategories = ['agreement', 'grammar', 'spelling', 'punctuation'];
        setSelectedCategories(new Set(essentialCategories));
        setSelectAll(false);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };
    fetchCategories();
  }, []);

  // Update AI settings when mode changes
  useEffect(() => {
    switch (aiMode) {
      case 'free':
        setUseLLMEnhancement(false);
        setUseLLMDetection(false);
        setUseFullLLM(false);
        break;
      case 'competitive':
        setUseLLMEnhancement(true);
        setUseLLMDetection(false);  // Enhancement only for speed
        setUseFullLLM(false);
        break;
      case 'premium':
        setUseLLMEnhancement(true);
        setUseLLMDetection(true);  // Full AI for maximum quality
        setUseFullLLM(false);
        break;
      case 'ultra':
        setUseLLMEnhancement(false);  // Not used in pure LLM mode
        setUseLLMDetection(false);    // Not used in pure LLM mode
        setUseFullLLM(true);          // 100% LLM-based checking
        break;
    }
  }, [aiMode]);

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
    
    // Safety check: if somehow no categories are selected, use essential ones
    const categoriesToUse = selectedCategories.size > 0 ? Array.from(selectedCategories) : ['agreement', 'grammar', 'spelling', 'punctuation'];

    onFileUpload(selectedFile, outputFilename.trim(), outputFormat, categoriesToUse, useLLMEnhancement, useLLMDetection, useFullLLM);
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

        {/* Category Selection - Modern Multi-Select */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-semibold text-gray-900 uppercase tracking-wide">
              Choose What to Check
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleSelectAll}
                disabled={disabled}
                className="text-xs px-3 py-1 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 font-medium transition-colors disabled:opacity-50"
              >
                {selectAll ? 'Deselect All' : 'Select All'}
              </button>
              <button
                type="button"
                onClick={() => {
                  // Select common/essential categories
                  const essential = ['grammar', 'spelling', 'punctuation', 'agreement', 'tense_consistency'];
                  const essentialSet = new Set(categories.filter(c => essential.includes(c.id)).map(c => c.id));
                  setSelectedCategories(essentialSet);
                  setSelectAll(false);
                }}
                disabled={disabled}
                className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 font-medium transition-colors disabled:opacity-50"
              >
                Essential Only
              </button>
            </div>
          </div>
          
          <div className="space-y-3">
            {/* Grammar & Structure Group */}
            <div>
              <div className="text-xs font-medium text-gray-600 mb-2 pl-1">🧠 Grammar & Structure</div>
              <div className="grid grid-cols-2 gap-2">
                {categories
                  .filter(c => ['agreement', 'grammar', 'tense_consistency', 'article_specificity', 'ambiguous_pronouns', 'dangling_clause', 'fragment', 'run_on', 'split_line', 'word_order'].includes(c.id))
                  .map((category) => (
                    <button
                      key={category.id}
                      type="button"
                      onClick={() => toggleCategory(category.id)}
                      disabled={disabled}
                      className={`text-left px-3 py-2 rounded-lg border-2 text-xs font-medium transition-all ${
                        selectedCategories.has(category.id)
                          ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-sm'
                          : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      {selectedCategories.has(category.id) && <span className="mr-1">✓</span>}
                      {category.name}
                    </button>
                  ))}
              </div>
            </div>

            {/* Style & Clarity Group */}
            <div>
              <div className="text-xs font-medium text-gray-600 mb-2 pl-1">✍️ Style & Clarity</div>
              <div className="grid grid-cols-2 gap-2">
                {categories
                  .filter(c => ['awkward_phrasing', 'redundancy', 'parallelism_concision', 'clarity', 'contrast', 'preposition', 'register', 'repetition'].includes(c.id))
                  .map((category) => (
                    <button
                      key={category.id}
                      type="button"
                      onClick={() => toggleCategory(category.id)}
                      disabled={disabled}
                      className={`text-left px-3 py-2 rounded-lg border-2 text-xs font-medium transition-all ${
                        selectedCategories.has(category.id)
                          ? 'border-purple-500 bg-purple-50 text-purple-900 shadow-sm'
                          : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      {selectedCategories.has(category.id) && <span className="mr-1">✓</span>}
                      {category.name}
                    </button>
                  ))}
              </div>
            </div>

            {/* Mechanics & Basics Group */}
            <div>
              <div className="text-xs font-medium text-gray-600 mb-2 pl-1">🔤 Mechanics & Basics</div>
              <div className="grid grid-cols-2 gap-2">
                {categories
                  .filter(c => ['spelling', 'punctuation', 'capitalisation', 'dialogue', 'comma_splice', 'coordination', 'ellipsis', 'hyphenation', 'missing_period', 'number_style', 'possessive', 'broken_quote', 'compounds', 'pronoun_reference'].includes(c.id))
                  .map((category) => (
                    <button
                      key={category.id}
                      type="button"
                      onClick={() => toggleCategory(category.id)}
                      disabled={disabled}
                      className={`text-left px-3 py-2 rounded-lg border-2 text-xs font-medium transition-all ${
                        selectedCategories.has(category.id)
                          ? 'border-green-500 bg-green-50 text-green-900 shadow-sm'
                          : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      {selectedCategories.has(category.id) && <span className="mr-1">✓</span>}
                      {category.name}
                    </button>
                  ))}
              </div>
            </div>
          </div>
          
          {/* Selection Summary */}
          <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-900">
                {selectedCategories.size > 0 
                  ? `${selectedCategories.size} of ${categories.length} categories selected`
                  : 'No categories selected'}
              </span>
              {selectedCategories.size > 0 && (
                <span className="text-xs text-gray-600">
                  {selectedCategories.size === categories.length ? '(All)' : '(Custom)'}
                </span>
              )}
            </div>
            {selectedCategories.size === 0 && (
              <p className="text-xs text-orange-600 mt-2">
                ⚠️ Please select at least one category to analyze
              </p>
            )}
          </div>
        </div>

        {/* AI Mode Selection */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-2">
            Quality Mode
          </label>
          <div className="space-y-2">
            {/* Free Mode */}
            <label className={`flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
              aiMode === 'free' 
                ? 'border-gray-900 bg-gray-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}>
              <input
                type="radio"
                name="aiMode"
                value="free"
                checked={aiMode === 'free'}
                onChange={(e) => setAiMode(e.target.value as 'free' | 'competitive' | 'premium' | 'ultra')}
                disabled={disabled}
                className="mt-0.5 w-4 h-4 text-gray-900 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">🆓 Free Mode</span>
                  <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full">Pattern-Only</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  470+ rules • 85-90% accuracy • Instant results • No cost
                </p>
              </div>
            </label>

            {/* Competitive Mode */}
            <label className={`flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
              aiMode === 'competitive' 
                ? 'border-blue-600 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}>
              <input
                type="radio"
                name="aiMode"
                value="competitive"
                checked={aiMode === 'competitive'}
                onChange={(e) => setAiMode(e.target.value as 'free' | 'competitive' | 'premium' | 'ultra')}
                disabled={disabled}
                className="mt-0.5 w-4 h-4 text-blue-600 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">⭐ Competitive Mode</span>
                  <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">RECOMMENDED</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Patterns + AI Enhancement • 92-95% accuracy • Fast
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  ~$0.01-0.03/MB • Best value for quality
                </p>
              </div>
            </label>

            {/* Premium Mode */}
            <label className={`flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
              aiMode === 'premium' 
                ? 'border-purple-600 bg-purple-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}>
              <input
                type="radio"
                name="aiMode"
                value="premium"
                checked={aiMode === 'premium'}
                onChange={(e) => setAiMode(e.target.value as 'free' | 'competitive' | 'premium' | 'ultra')}
                disabled={disabled}
                className="mt-0.5 w-4 h-4 text-purple-600 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">💎 Premium Mode</span>
                  <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">Maximum Quality</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Patterns + AI Detection + Enhancement • 95-98% accuracy
                </p>
                <p className="text-xs text-purple-600 mt-1">
                  ~$0.05-0.15/MB • Deep analysis for complex documents
                </p>
              </div>
            </label>

            {/* Ultra Mode - Full LLM */}
            <label className={`flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
              aiMode === 'ultra' 
                ? 'border-orange-600 bg-orange-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}>
              <input
                type="radio"
                name="aiMode"
                value="ultra"
                checked={aiMode === 'ultra'}
                onChange={(e) => setAiMode(e.target.value as 'free' | 'competitive' | 'premium' | 'ultra')}
                disabled={disabled}
                className="mt-0.5 w-4 h-4 text-orange-600 border-gray-300"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">🤖 Ultra Mode</span>
                  <span className="text-xs px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full font-medium">100% AI</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Pure AI-powered checking • 98-99% accuracy • Context-aware
                </p>
                <p className="text-xs text-orange-600 mt-1">
                  ~$0.10-0.30/MB • Most accurate, understands context & style
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedFile || !outputFilename.trim() || selectedCategories.size === 0 || disabled}
          className={`w-full py-3.5 px-6 rounded-lg text-sm font-semibold transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed ${
            aiMode === 'competitive' 
              ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white'
              : aiMode === 'premium'
              ? 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white'
              : aiMode === 'ultra'
              ? 'bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white'
              : 'bg-gray-900 hover:bg-gray-800 text-white'
          }`}
        >
          {disabled ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              Processing...
            </span>
          ) : (
            <span>
              {aiMode === 'competitive' ? '⭐ Analyze with AI (Recommended)' 
               : aiMode === 'premium' ? '💎 Analyze with Premium AI'
               : aiMode === 'ultra' ? '🤖 Analyze with Ultra AI (100% AI)'
               : '🔍 Analyze with Patterns'}
            </span>
          )}
        </button>
        
        {/* Helpful Tip */}
        {selectedCategories.size > 0 && (
          <div className="text-center">
            <p className="text-xs text-gray-500">
              {aiMode === 'free' && '💡 Tip: Try Competitive Mode for AI-enhanced suggestions'}
              {aiMode === 'competitive' && '✨ Fast processing with AI-enhanced fixes'}
              {aiMode === 'premium' && '🔍 Deep AI analysis - finds the most subtle issues'}
              {aiMode === 'ultra' && '🤖 Pure AI - most accurate, context-aware analysis'}
            </p>
          </div>
        )}
      </form>
    </div>
  );
};
