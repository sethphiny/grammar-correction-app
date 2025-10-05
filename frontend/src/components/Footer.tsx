import React from 'react';
import { Heart, Github, Mail } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-6 h-6 bg-primary-600 rounded flex items-center justify-center">
                <span className="text-white text-xs font-bold">GC</span>
              </div>
              <span className="font-semibold text-gray-900">Grammar Correction</span>
            </div>
            <p className="text-gray-600 text-sm mb-4 max-w-md">
              AI-powered grammar and style analysis for Word documents. 
              Built with hybrid NLP technology combining spaCy and LanguageTool for enhanced accuracy.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="mailto:support@example.com"
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Email Support"
              >
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Features */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Features</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>Document Upload (.doc/.docx)</li>
              <li>Hybrid AI Analysis</li>
              <li>Line-by-Line Checking</li>
              <li>Multiple Output Formats</li>
              <li>Progress Tracking</li>
            </ul>
          </div>

          {/* Technology */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Technology</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>React + TypeScript</li>
              <li>FastAPI + Python</li>
              <li>spaCy NLP</li>
              <li>LanguageTool</li>
              <li>Docker</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-200 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-600 mb-4 md:mb-0">
              © 2024 Grammar Correction App. All rights reserved.
            </p>
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <span>Made with</span>
              <Heart className="h-4 w-4 text-red-500" />
              <span>for better writing</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
