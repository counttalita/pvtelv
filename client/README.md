# PVTElA Digital Wallet - Frontend Client

This is the frontend client for the PVTElA Digital Wallet application. It provides the user interface for interacting with the PVTElA backend services.

## Key Technologies

This project is built with:
- Vite
- TypeScript
- React
- React Router DOM (`react-router-dom`) for routing
- TanStack Query (`@tanstack/react-query`) for server state management
- shadcn/ui (UI components)
- Tailwind CSS (utility-first CSS framework)
- ESLint with TypeScript ESLint & React plugins for code quality
- Vitest (for unit/integration tests)

## Project Structure Overview

The client-side code is organized as follows within the `src/` directory:
- `pages/`: Top-level components representing different pages/views.
- `components/`: Reusable UI components, including feature-specific (e.g., `auth/`, `dashboard/`) and general UI elements (from `ui/`).
- `services/`: Modules responsible for external interactions, primarily API calls (`api.ts`, `auth.ts`, `walletApiService.ts`).
- `hooks/`: Custom React hooks for reusable component logic.
- `types/`: TypeScript type definitions, especially for API data structures (`apiData.ts`).
- `lib/`: Utility functions.
- `App.tsx`: Root application component, sets up routing and global providers.
- `main.tsx`: Main entry point of the application.

## Key Architectural Decisions & Features

- **API Communication:** A central API service (`src/services/api.ts`) handles all HTTP requests to the backend. It includes logic for adding authentication tokens to headers and standardized error handling from responses.
- **Authentication:** User authentication is phone/OTP-based, managed by `src/services/auth.ts`. Session tokens obtained from the backend are stored in `localStorage`. Protected routes are enforced using a higher-order component pattern.
- **State Management:** Server state (data fetching, caching, background updates) is managed by `@tanstack/react-query`. Local component state is handled using React's built-in hooks (`useState`, `useReducer`, etc.).
- **UI & Responsiveness:** The UI is built with shadcn/ui components and styled with Tailwind CSS, aiming for a consistent and responsive design across various screen sizes. Responsive utility classes are used to adapt layouts.
- **Error Handling:** Global error handling for React component rendering errors is provided by an `ErrorBoundary` component (`src/components/layout/ErrorBoundary.tsx`). API call errors are logged via the central API service.
- **Code Quality:** ESLint is configured with rules for TypeScript and React, including `@typescript-eslint/no-unused-vars` (configured to allow underscore-prefixed exceptions) to maintain code hygiene.

## Setup & Development

1.  Navigate to the `client` directory:
    ```sh
    cd client
    ```
2.  Install dependencies:
    ```sh
    npm i
    ```
3.  Start the development server (usually on `http://localhost:5173` or similar):
    ```sh
    npm run dev
    ```

## Testing

Basic unit and integration tests for services like `api.ts` are implemented using Vitest. To run tests (if a test script is configured in `package.json`):
```sh
# (Assuming 'npm test' or 'npm run test:unit' is configured)
# npm test 
```
*(If no specific test script is known, this part can be omitted or made more generic).*
