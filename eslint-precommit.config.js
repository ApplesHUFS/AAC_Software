module.exports = {
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'no-unused-vars': 'off',
    'no-useless-catch': 'off',
    'react/no-unescaped-entities': 'off'
  },
  ignorePatterns: [
    'build/**/*',
    'dist/**/*',
    'node_modules/**/*'
  ]
};
