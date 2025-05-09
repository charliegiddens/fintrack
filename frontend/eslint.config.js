// Convert to CommonJS format
const { defineConfig } = require('eslint-define-config');
const js = require('@eslint/js');
const globals = require('globals');
const pluginReact = require('eslint-plugin-react');
const babelParser = require('@babel/eslint-parser');

module.exports = defineConfig([
  {
    files: ['**/*.{js,mjs,cjs,jsx}'],
    languageOptions: {
      parser: babelParser, // Use the imported parser object
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true, // Enable JSX parsing
        },
        requireConfigFile: false, // Add this to avoid requiring a babel config file
        babelOptions: {
          presets: ['@babel/preset-react'], // Add React preset for JSX parsing
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node, // Add Node.js globals
        process: 'readonly', // Add process explicitly
        jest: 'readonly',
        describe: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        test: 'readonly',
        expect: 'readonly',
      },
    },
    plugins: {
      js,
    },
    rules: {
      ...js.configs.recommended.rules,
    },
  },
  {
    files: ['**/*.jsx', '**/*.js'],
    plugins: {
      react: pluginReact,
    },
    rules: {
      ...pluginReact.configs.recommended.rules,
    },
  },
  {
    files: ['**/*.jsx', '**/*.js'],
    settings: {
      react: {
        version: 'detect', // Automatically detect React version
      },
    },
  },
]);