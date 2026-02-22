# Feature Documentation - Team Tasks Manager

This document outlines the core features provided by the backend API, which should be implemented in the frontend application.

## 1. Authentication & User Management
- **User Registration**: Create a new account with email, name, and password.
- **User Login**: Secure JWT-based authentication.
- **Persistent Session**: Use the access token for all authenticated requests.
- **User Profile (`/me`)**: Get current user details (id, email, name, role).
- **User Logout**: Clear session and acknowledge termination.

## 2. Project Management
- **Dashboard**: View a list of "Owned Projects" and "Member Projects."
- **Project Creation**: Start new projects with a name and description.
- **Project Details**: Deep dive into a specific project to see tasks and members.
- **Project Editing**: Update project metadata (Owner only).
- **Project Deletion**: Remove a project and all associated tasks (Owner only).

## 3. Team Collaboration
- **Member Management**:
  - Add members to a project via their `user_id`.
  - View all members currently in a project.
  - Remove members from a project (Owner only).
- **Role Awareness**: The UI should adapt based on whether the user is an **Owner** or a **Member**.

## 4. Task Management
- **Task Types**:
  - **Common Tasks**: Visible to the entire team. Progress is tracked individually per member.
  - **Private Tasks**: Personal tasks within a project, visible only to the creator.
- **Task Operations**:
  - **Creation**: Add tasks with title and description (Task type is set to "Common" or "Private").
  - **Editing**: Modify task details (Owner or Task Creator only).
  - **Deletion**: Remove tasks (Creator only).
- **Progress Tracking**:
  - Members can update their personal status (`ACTIVE`, `PENDING`, or `COMPLETE`) for Common Tasks.
  - Project Owners can see a summary of everyone's progress on a task.

## 5. Global System Features
- **Centralized Notifications**: Display clear error messages (e.g., "Permission Denied," "Invalid Input") using the backend's global error responses.
- **Real-time Status Updates**: Immediate UI feedback when a task or project state changes.
- **Search & Filtering**: (Suggested) Filter tasks by title or completion status.
