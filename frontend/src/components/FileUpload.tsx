import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { OutputFormat } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { cn } from '../lib/utils';

interface FileUploadProps {
  onFileSelect: (file: File, outputFormat: OutputFormat, customFilename?: string) => void;
  disabled?: boolean;
  darkMode?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, disabled = false, darkMode = false }) => {
  const [outputFormat, setOutputFormat] = useState<OutputFormat>('docx');
  const [customFilename, setCustomFilename] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Check file size (50MB limit)
      const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes
      if (file.size > MAX_FILE_SIZE) {
        alert('File size exceeds 50MB limit. Please choose a smaller file.');
        return;
      }
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxFiles: 1,
    disabled,
  });

  const handleSubmit = () => {
    if (selectedFile) {
      onFileSelect(selectedFile, outputFormat, customFilename || undefined);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
        <CardDescription>
          Upload a Word document (.doc or .docx) for professional grammar and style analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">

        {/* File Upload Area */}
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300",
            isDragActive
              ? "border-primary bg-primary/10"
              : "border-border hover:border-primary/50 bg-muted/50",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 mb-4 text-muted-foreground" />
          {isDragActive ? (
            <p className="font-medium text-primary">
              Drop the file here...
            </p>
          ) : (
            <div>
              <p className="mb-2 text-muted-foreground">
                Drag & drop a Word document here, or click to select
              </p>
              <p className="text-sm text-muted-foreground">
                Supports .doc and .docx files up to 50MB
              </p>
            </div>
          )}
        </div>

        {/* File Rejection Errors */}
        {fileRejections.length > 0 && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Invalid file</AlertTitle>
            <AlertDescription>
              {fileRejections.map(({ file, errors }) => (
                <div key={file.name}>
                  {errors.map((error) => (
                    <div key={error.code}>{error.message}</div>
                  ))}
                </div>
              ))}
            </AlertDescription>
          </Alert>
        )}

        {/* Selected File */}
        {selectedFile && (
          <Alert>
            <FileText className="h-4 w-4" />
            <AlertTitle>File Selected</AlertTitle>
            <AlertDescription>
              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Output Format Selection */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-foreground">
            Output Format
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="outputFormat"
                value="docx"
                checked={outputFormat === 'docx'}
                onChange={(e) => setOutputFormat(e.target.value as OutputFormat)}
                className="mr-2"
              />
              <span className="text-foreground">DOCX</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="outputFormat"
                value="pdf"
                checked={outputFormat === 'pdf'}
                onChange={(e) => setOutputFormat(e.target.value as OutputFormat)}
                className="mr-2"
              />
              <span className="text-foreground">PDF</span>
            </label>
          </div>
        </div>

        {/* Custom Filename */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-foreground">
            Custom Filename (optional)
          </label>
          <input
            type="text"
            value={customFilename}
            onChange={(e) => setCustomFilename(e.target.value)}
            placeholder="Enter custom filename"
            className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 transition-colors"
          />
        </div>

        {/* Submit Button */}
        <Button
          onClick={handleSubmit}
          disabled={!selectedFile || disabled}
          className="w-full"
          size="lg"
        >
          {disabled ? 'Processing...' : 'Start Professional Analysis'}
        </Button>
      </CardContent>
    </Card>
  );
};

export default FileUpload;
