# Changes

## Windows Compatibility and Bug Fixes

### Windows Compatibility
- Added Windows compatibility for directory tools (ls, tree, grep)
- Added platform detection to use appropriate commands based on OS
- For Windows:
  - `ls` tool now uses `dir` command
  - `tree` tool uses Windows-specific tree command format
  - `grep` tool uses `findstr` with fallback to Python implementation

### Bug Fixes
- Fixed CRLF issues when copying/pasting prompts with line breaks
- Replaced complex ASCII art with simpler version that works across different terminals
- Improved GlobTool to better handle simple filename patterns with recursive search

### Improvements
- Added more helpful error messages for missing commands on different platforms
- Enhanced error handling for Windows-specific command behavior