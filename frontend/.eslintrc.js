module.exports = {
  extends: [
    'react-app',
    'react-app/jest'
  ],
  rules: {
    // Disable conflicting rules
    'react/jsx-uses-react': 'off',
    'react/react-in-jsx-scope': 'off',
    // Allow unused vars in development
    '@typescript-eslint/no-unused-vars': ['warn', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }]
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
};
