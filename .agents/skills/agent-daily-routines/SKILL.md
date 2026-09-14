```markdown
# agent-daily-routines Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `agent-daily-routines` TypeScript repository. You'll learn how to structure files, write and organize code, follow commit message standards, and run or write tests, ensuring consistency and maintainability throughout the codebase.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `dailyRoutineManager.ts`, `userProfileHandler.ts`

### Import Style
- Use **relative imports** for modules within the project.
  - Example:
    ```typescript
    import { getUserData } from './userData';
    ```

### Export Style
- Use **named exports** for all modules.
  - Example:
    ```typescript
    // In userData.ts
    export function getUserData(id: string) { ... }
    ```

### Commit Messages
- Follow the **Conventional Commits** format.
- Common prefixes: `docs`, `chore`, `feat`
- Example:
  ```
  feat: add daily routine scheduler for users
  docs: update README with setup instructions
  chore: refactor user data fetching logic
  ```

## Workflows

### Creating a New Feature
**Trigger:** When adding new functionality  
**Command:** `/new-feature`

1. Create a new TypeScript file using camelCase naming.
2. Implement your feature using named exports.
3. Use relative imports for any dependencies.
4. Write or update relevant test files (`*.test.ts`).
5. Commit your changes with a `feat:` prefix and a concise description.

### Updating Documentation
**Trigger:** When modifying or adding documentation  
**Command:** `/update-docs`

1. Edit or add documentation files as needed.
2. Use clear, concise language.
3. Commit changes with a `docs:` prefix and a summary of the update.

### Refactoring or Maintenance
**Trigger:** When improving code structure or dependencies  
**Command:** `/chore-refactor`

1. Refactor code while maintaining existing functionality.
2. Ensure all imports remain relative and exports are named.
3. Update or add tests if necessary.
4. Commit changes with a `chore:` prefix and a brief description.

## Testing Patterns

- Test files follow the pattern: `*.test.ts`
- The testing framework is **unknown**, but tests are colocated with source files or in a dedicated test directory.
- Example test file:
  ```typescript
  // dailyRoutineManager.test.ts
  import { scheduleRoutine } from './dailyRoutineManager';

  describe('scheduleRoutine', () => {
    it('should schedule a routine for a user', () => {
      // test logic here
    });
  });
  ```

## Commands
| Command         | Purpose                                         |
|-----------------|-------------------------------------------------|
| /new-feature    | Start a new feature with proper conventions     |
| /update-docs    | Update or add documentation                     |
| /chore-refactor | Perform refactoring or maintenance tasks        |
```
