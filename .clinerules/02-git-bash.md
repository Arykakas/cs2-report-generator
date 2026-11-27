
# Git Bash Terminal Rules

You are operating on Windows using Git Bash.

## Shell environment
- Always use Bash syntax.
- Never generate PowerShell commands.
- Never launch powershell.exe -Command.
- Use Unix-style commands and paths.
- Use forward slashes for file paths.

## File inspection
- Prefer native IDE file tools for reading files.
- Use grep for searching text.
- Use sed for inspecting specific line ranges.
- Use cat for small files.
- Use head and tail when appropriate.
- Do not print entire large files unnecessarily.

## Search examples
- grep -n "pattern" file.py
- grep -rn "pattern" cs2_report/
- sed -n '300,400p' file.py
- find . -name "*.py"

## Windows compatibility
- The project is located on the Windows filesystem.
- Use Git Bash paths such as /c/Code/cs2-report.
- Do not assume Linux system packages are installed.
- Do not use sudo or Linux package managers.
- Use Windows Python environment and existing
  project dependencies.

## Command reliability
- Never invent command options.
- Read complete error messages.
- Never repeat failed commands unchanged.
- After two failed attempts, stop and reassess.
