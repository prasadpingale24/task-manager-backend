# Frontend Integration Guidelines

This document provides the "Rules of Engagement" for building the frontend application to ensure it cleanly consumes the backend API as a pure service.

## 1. API-First Development
- **Source of Truth**: The `openapi.yaml` (located in `/openapi/`) is the definitive contract. 
- **Code Generation**: **Strongly Recommended.** Use tools like `openapi-typescript`, `swagger-codegen`, or `rtk-query-codegen` to generate API client SDKs and Typescript interfaces directly from the YAML. Do not manually define API types.
- **Heavy Lifting**: All business logic (validation, permission checks, data calculation) resides on the backend. The frontend should focus strictly on **State Display** and **User Interaction**.

## 2. Authentication Strategy
- **Token Type**: The backend uses JWT (JSON Web Tokens).
- **Storage**: Store the access token in a secure place (e.g., `SecureStore` for React Native/Expo or HttpOnly Cookies/Secure LocalStorage for Web).
- **Usage**: Include the token in the `Authorization` header for all protected requests:
  ```http
  Authorization: Bearer <your_access_token>
  ```
- **Session Expiry**: Handle `401 Unauthorized` responses by redirecting the user to the Login screen.

## 3. Data Interaction & State Management
- **Query Pattern**: Use a data-fetching library (e.g., **TanStack Query (React Query)** or **SWR**). 
- **Cache Invalidation**: After a successful "Mutation" (POST, PUT, or DELETE), invalidate the related queries to ensure the UI stays in sync with the backend database.
- **Optimistic Updates**: (Optional) For a premium feel, implement optimistic updates for task status changes, rolling back only if the API returns an error.

## 4. Unified Error Handling
- **Global Catch**: Implement a global error interceptor (e.g., an Axios interceptor).
- **Mapping Backend Errors**:
  - **400 Bad Request**: Display field-specific validation errors from the backend response.
  - **403 Forbidden**: Show a persistent "Access Denied" toast or alert.
  - **500 Internal Error**: Show a generic "Something went wrong" message.

## 5. UI/UX "Must-Haves"
- **Loading States**: Show skeletons or spinners for every asynchronous request.
- **Role-Based UI**:
  - If a user is a **Member**, hide "Edit Project" and "Delete Project" buttons.
  - If a user is not the **Creator** of a task, disable or hide the "Delete Task" button.
- **Empty States**: Provide clear guidance when a project has no tasks or a user has no projects.
