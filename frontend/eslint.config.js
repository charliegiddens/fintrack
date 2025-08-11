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
      parser: babelParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
        requireConfigFile: false,
        babelOptions: {
          presets: ['@babel/preset-react'],
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        process: 'readonly',
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
        version: 'detect',
      },
    },
  },
]);