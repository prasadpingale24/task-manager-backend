# User Flow Documentation - Team Tasks Manager

This document maps out the specific journeys for the two primary roles within the application: **Project Owner** and **Project Member**.

---

## 👑 Role: Project Owner
The Project Owner is the "Admin" of a project. They manage the project structure, team composition, and core task definitions.

### 1. Project Initialization Flow
1. **Login**: User authenticates and lands on the Dashboard.
2. **Action**: Clicks "Create New Project."
3. **Input**: Enters Project Name and Description.
4. **Result**: Project is created, and the user is redirected to the Project Detail view.

### 2. Team Management Flow
1. **Entry**: Inside the Project Detail view, navigates to "Manage Members."
2. **Action**: Searches/Enters a `user_id` to add to the team.
3. **Result**: Member is added and will now see this project on their dashboard.

### 3. Task Orchestration Flow
1. **Action**: Clicks "Add New Task."
2. **Configuration**: Enters details (Title, Description) and selects "Common Task."
3. **Result**: Task appears for all project members.
4. **Monitoring**: Owner can click on the task to see a list of all members and their current status (e.g., "John: COMPLETE", "Sarah: ACTIVE").

---

## 👥 Role: Project Member
The Project Member is a collaborator. They focus on executing tasks assigned to the team and managing their own personal workflow.

### 1. Collaboration Flow
1. **Login**: User sees the project under "Member Projects" on their dashboard.
2. **Entry**: Opens the project to see the task list.
3. **Action**: Selects a **Common Task** created by the Owner.
4. **Engagement**: Updates their status from `PENDING` to `ACTIVE` or `COMPLETE`.
5. **Result**: Their personal progress is updated, and the Owner can see this change immediately.

### 2. Personal Productivity Flow
1. **Entry**: Inside the Project view.
2. **Action**: Clicks "Add New Task."
3. **Configuration**: Enters details and selects "Private Task."
4. **Result**: The task is created but is **only visible to this user**. It helps them manage their individual workload without cluttering the team's space.

---

## 🛠 Shared Flows (All Users)

### Account Management
1. **Signup**: Register for an account.
2. **Profile**: Fetch profile details using `/me` to display name/role in the UI.
3. **Logout**: Click logout to clear local tokens and call the `/logout` endpoint.

### Error Recovery
1. **Action**: User tries to delete a project they don't own.
2. **Feedback**: System displays a "Permission Denied" notification (standard 403 response).
3. **Recovery**: User is guided back to their dashboard or allowed actions.
