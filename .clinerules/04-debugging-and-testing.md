
# Debugging and Testing Rules

## Debugging process
1. Reproduce or understand the reported issue.
2. Read the complete error message.
3. Locate the relevant code.
4. Identify the actual root cause.
5. Explain the proposed fix.
6. Make the smallest reasonable change.
7. Verify the result.

## Failed commands
- Never repeat an identical failed command.
- Never guess alternative command parameters.
- Diagnose the actual error before retrying.
- After two failed attempts, stop and reassess.
- Do not enter repetitive execution loops.
- Report when human intervention is needed.

## Testing
- Inspect existing tests before adding new tests.
- Run relevant tests after modifying code.
- Run lint and type checks when available.
- Run the project build when appropriate.
- Do not modify tests simply to make them pass.
- Never claim tests passed without executing them.

## Regression prevention
- Check whether changes affect other modules.
- Preserve existing behaviour unless explicitly requested.
- Verify imports and function calls after refactoring.
- Review the final Git diff.

## Code Verification Before Completion

- Never assume code is correct simply because it was written.
- Inspect all referenced variables, functions and imports.
- Verify that every referenced constant is defined or imported.
- Check function signatures against their callers.
- Check dictionary keys and expected data structures.
- Run tests that exercise the modified code paths.
- Do not stop after fixing the first error if further
  related errors are likely.
- Never invent missing business logic or data.
- Preserve existing functionality and expected outputs.