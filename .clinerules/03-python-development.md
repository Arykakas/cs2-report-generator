
# Python Development Rules

## Code quality
- Follow PEP 8 conventions.
- Use meaningful variable and function names.
- Prefer small functions with a single responsibility.
- Avoid duplicate code.
- Use existing project dependencies before introducing new ones.
- Add type hints where appropriate.

## Existing implementation
- Inspect imports before changing Python files.
- Check function signatures before calling existing functions.
- Preserve existing function interfaces unless changes are necessary.
- Check how data flows between modules before changing data structures.
- Avoid circular imports.

## Error handling
- Handle expected exceptions explicitly.
- Do not use broad except Exception blocks to hide errors.
- Never silently ignore errors.
- Include useful error messages.

## Dependencies
- Inspect requirements.txt or pyproject.toml first.
- Never install a package without checking whether it
  is already available.
- Do not change dependency versions unnecessarily.

## Data processing
- Preserve existing data formats and schemas.
- Validate input data before processing.
- Handle missing values and unexpected data types.
- Avoid modifying raw input files.
