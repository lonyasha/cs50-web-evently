# Evently - README

Evently is a web application designed to manage events efficiently. This project is built using the Django framework and incorporates several distinctive features that make it both unique and complex.

## Distinctiveness and Complexity: Why This Project Satisfies the Requirements

This Evently is a complex and feature-rich web application that goes beyond basic event management, providing functionalities such as RSVP tracking, task assignment, real-time chat between users, asynchronous background tasks, and much more. Unlike simple social network applications or e-commerce platforms, this project focuses on a specialized niche—event organization, task management, and interaction within events, which makes it both distinct and highly functional.

### **Distinctiveness**:

The project stands out due to the following features and functionality:

- **Event Management**: Users can create, edit, and delete events. Events are categorized into upcoming and past events, and users can view detailed information for each event.
- **Task Management**: Each event includes task management capabilities. Users can create tasks, assign them to attendees of the event, edit, and delete tasks. This ensures seamless organization and delegation of responsibilities within an event.
- **RSVP Management**: The event organizer can send RSVP invitations to users. Users have a dedicated list of RSVPs where unresolved ones are highlighted. They can respond to RSVPs with "Yes," "No," or "Maybe," streamlining attendance tracking.
- **Real-Time Chat**: A chat is automatically created for each event in the background, and participants are added automatically using Django signals. Chat participants include the event organizer and users who have responded "Yes" to the RSVP. Messages are stored in the database, and the chat interface is dynamically updated using JavaScript.
- **Automatic Cleanup of Past Events**: Events older than 2 days are automatically deleted, including associated tasks, RSVPs, chats, and chat participants. This background functionality is handled using cron tasks managed by Django-Q.
- **Advanced User Interface**: Custom form widgets are used throughout the application, ensuring that users interact with forms efficiently. This is made possible by the widget_tweaks package.

These features combine to create a highly functional and interactive event management system, incorporating seamless user experiences and powerful background automation.

### **Complexity**:

The complexity of the project arises from the integration of multiple advanced features and the seamless automation of event and user management tasks:

- **Event CRUD Operations**: The project provides robust functionality to create, read, update, and delete events. These operations are enhanced with categorized views for upcoming and past events.

- **Task Management**: Each event includes a task management system. Tasks can be created, assigned to attendees, edited, and deleted. This ensures efficient delegation and tracking of responsibilities.

- **RSVP Functionality**: RSVP management allows organizers to send invitations and users to respond with "Yes," "No," or "Maybe." Unresolved RSVPs are highlighted in the user’s RSVP list, streamlining decision-making.

- **Automated Chat Management**: Using Django signals, the system automatically creates chats for each event and adds participants based on RSVP responses. The chat interface is built with a JavaScript-powered dynamic UI and stores messages in the database for persistence.

- **Automatic Event Cleanup**: Events older than 2 days are automatically deleted along with their associated chats, tasks, RSVP records, and chat participants. This is implemented as a cron task managed by Django-Q.

- **Database Optimization**: Efficient database queries ensure the application remains responsive while managing the cascade deletions and automated status updates.

- **Background Task Management**: Asynchronous operations such as automatic chat creation, participant management, and event cleanup are handled using Django-Q and signals, providing scalability and responsiveness to the application.

This combination of front-end interactivity, seamless background automation, and robust data management highlights the project's technical depth and architectural complexity.

---

## Project Files and Their Purpose

### **1. `evently/settings.py`**:

Contains all the essential configuration for the Django project. It includes settings for the database, static files, middleware, and security. Additionally, it includes settings for the integration of `widget_tweaks`, `django_q`, `debug_toolbar` and Redis caching.

- **Redis for caching**: Configured with Django’s caching framework.
- `widget_tweaks`: Added to `INSTALLED_APPS` for custom form rendering.
- `django_q`: Configured for asynchronous background task handling.
- `debug_toolbar`: Only enabled in the development environment.

### **2. `evently/urls.py`**:

Handles the routing of incoming requests to the appropriate view functions. It includes the main routes for event management, tasks, RSVP, chat, user authentication (login, logout, registration), and password change functionality.

### **3. `events/models.py`**:

Defines the data models used throughout the application. This includes:

- `Event`: Represents an event with fields for title, date, description, location, organizer, and status (ACTIVE or INACTIVE). Includes methods for attendee count and validation to prevent creating events in the past. The model also utilizes database indexes for efficient querying.
- `RSVP`: Tracks attendance for events, linking users and events. RSVP responses can be "Yes", "No", or "Maybe". Ensures that a user can RSVP to an event only once using a unique constraint.
- `Task`: Represents tasks associated with an event. Tasks can be assigned to users, marked as completed, and are linked to a specific event.
- `Chat`: Automatically created for each event and linked via a one-to-one relationship. Includes a method to check if the chat is deletable (based on the event date being older than 2 days).
- `ChatParticipant`: Tracks participants in a chat. Automatically adds and removes users (event organizers or those with a "Yes" RSVP) to the chat. Ensures that a user cannot be added to the same chat more than once using a unique constraint.
- `Message`: Stores messages sent in chats, including the sender (`user`), the chat to which it belongs, and a timestamp. Messages are persistently saved in the database for retrieval.

### **4. `events/views`**:

The views directory is organized into separate files to handle different aspects of the application’s functionality, ensuring a clean and modular codebase. The views include:

- `auth_views.py`: Handles user authentication, including login, logout, and registration functionalities.
- `chat_views.py`: Manages the real-time chat system for event participants, including fetching chat messages and sending new messages.
- `event_views.py`: Includes views for event-related operations such as creating, updating, deleting, and viewing event details.
- `rsvp_views.py`: Handles RSVP management, including displaying a user’s RSVP list, and updating RSVP responses.
- `task_views.py`: Manages task tracking for events, including creating, assigning tasks to users, editing, marking as completed, and deleting tasks.

This structure ensures a clear separation of concerns, making the code easier to maintain and extend.

### **5. `events/forms.py`**:

Defines form classes that manage user input across the application. These forms handle tasks like user registration, login, password resets, and managing event-related data such as tasks and RSVP responses. Each form ensures proper validation and sanitization before data is processed.

### **6. `events/signals.py`**:

Defines automated actions triggered by specific events in the application, ensuring seamless integration between related features.

1. `create_chat_for_event`:

   Triggered when a new event is created.
   Automatically creates a Chat instance for the event and adds the event creator as a participant.

2. `update_chat_participants`:

   Triggered when an RSVP is created or updated.
   Adds users with an RSVP status of "Yes" to the event's chat as participants and removes them if their status changes to "No" or "Maybe."

These signals automate chat and participant management, reducing the need for manual updates and ensuring consistency across the system.

### **7. `events/tasks.py`**:

Contains utility functions to automate background operations related to events. These tasks are executed periodically using Django-Q's cron cluster, ensuring the application remains up-to-date without manual intervention.

1. `update_event_status`:

   Checks all events with an "ACTIVE" status and a date that has passed.
   Updates their status to "INACTIVE" in bulk, ensuring the status reflects the current state of the events.

2. `delete_old_events`:

   Deletes events that are older than two days.
   Ensures that all associated data, such as RSVP records, tasks, and chats, are removed through cascading deletions, keeping the database clean and efficient.

These tasks are scheduled to run automatically via the Django-Q cron cluster, providing a scalable solution for background management of events and related data.

### **8. `events/templates`**:

Contains all the HTML templates for rendering views. These include:

- **`accounts/`**:

  - `login.html`: Template for user login.
  - `register.html`: Template for user registration.
  - `password_reset.html`: Template for initiating password reset.
  - `password_reset_complete.html`: Template for confirming password reset.
  - `password_reset_confirm.html`: Template for resetting the password.
  - `password_reset_done.html`: Template shown after password reset completion.

- **`events/`**:

  - `event_list.html`: Displays a list of events separated into upcoming and past.
  - `event_detail.html`: Shows detailed information about a specific event.
  - `event_form.html`: Form for creating or editing events.
  - `index.html`: Homepage or main entry point.
  - `layout.html`: Base layout for other pages.
  - `rsvp_list.html`: Displays a list of RSVPs for events.
  - `chat_tabs.html`: Template for chat tabs.

- **`includes/`**:
  - `event_card.html`: Partial for rendering event cards.
  - `rsvp_list_partial.html`: Partial for rendering a list of RSVPss.
  - `task_form_partial.html`: Partial for rendering task creation/edit form.
  - `task_list_partial.html`: Partial for rendering a list of tasks.

This structure helps keep related templates organized by feature or functionality, making it easier to maintain and scale the project.

## **10. `event/templatetags`**:

Custom template tags and filters used within the `events` app are defined in this directory. Template tags allow for enhanced functionality in templates by adding custom behavior or filters.

- `custom_widget_tweaks.py` file defines a custom Django template filter to enhance form rendering. It extends the widget_tweaks library by adding a conditional filter, add_class_if, which applies a specified CSS class to a form field only if the field has validation errors. This helps in dynamically styling form fields based on their validation state, improving user feedback in forms.

### **11. `events/context_processors.py`**:

This file contains a custom context processor that provides the count of RSVP invitations with a status of "Maybe" for the currently logged-in user. The `maybe_count` variable is used globally in templates, such as in the site header, to display a badge showing the number of pending RSVP decisions.

### **12. `events/static`**:

Contains all the CSS and JavaScript used by the web application. This includes custom styles for event pages, task management, and chat interfaces, as well as any JavaScript functionality required for dynamic behavior.

### **13. `events/tests`**:

Contains unit tests to ensure the reliability and correctness of the application's core functionality. The tests are organized into the following files:

- **`test_forms.py`**: Tests for form validation and functionality, such as event creation and RSVP submissions.
- **`test_models.py`**: Tests for model behavior, including event creation, RSVP tracking, and database constraints.
- **`test_signals.py`**: Tests for signal-based automation, such as automatic chat creation and participant management.
- **`test_tasks.py`**: Tests for background tasks like updating event statuses and deleting old events.
- **`test_urls.py`**: Tests for URL routing to ensure proper redirection to views.
- **`test_views.py`**: Tests for view logic, including event listing, task management, and chat functionality.

### **14. `requirements.txt`**:

Lists all the Python dependencies required to run the project. It includes Django, `django_q`, `widget_tweaks`, `debug_toolbar` and other essential libraries.

---

## How to Run the Application

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd evently
   ```

2. **Install Dependencies**:
   Ensure Python and pip are installed on your machine. Run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Redis**: Redis is required for caching and task management. Install and start the Redis server:

   - On Linux:

     ```bash
     sudo apt update
     sudo apt install redis
     sudo systemctl start redis
     sudo systemctl enable redis
     ```

   - on macOS:

   ```bash
   brew install redis
   brew services start redis
   ```

   - On Windows: [Use Redis for Windows](https://github.com/microsoftarchive/redis/releases).

   Verify that Redis is running:

   ```bash
   redis-cli ping
   ```

   It should respond with `PONG`.

4. **Start the Django-Q cluster**:
   Django-Q is used for managing cron tasks.

   ```bash
   python manage.py qcluster
   ```

5. **Run Migrations**:
   Apply database migrations to set up the database schema:

   ```bash
   python manage.py migrate
   ```

6. **Create an Admin User**:
   Generate a superuser account for accessing the admin interface:

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**:
   Start the Django development server:

   ```bash
   python manage.py runserver
   ```

8. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

## Notes on Django-Q Compatibility Issue

If you encounter an error originating from the `django-q` package related to the removal of the `baseconv` module in newer versions of Django (4.0 or later), follow these steps to resolve it:

1. **Locate the File**: Open the file at:

```bash
<your-environment-path>/Lib/site-packages/django_q/core_signing.py
```

2. **Edit the Import**: Replace:

```python
from django.utils import baseconv
```

With:

```python
from django.core import signing
```

3. **Update Usage**: Replace any usage of `baseconv` with Django's `signing` module or equivalent functionality from another library.

4. **Save and Restart**: Save the file and restart your server.

This is a known compatibility issue with `django-q` and can be patched manually if necessary.

## Additional Information

- **Static Files**: Ensure to collect static files when deploying the app to production using:
  ```bash
  python manage.py collectstatic
  ```
- **Asynchronous Tasks**: Ensure Redis and Django-Q are running for scheduled and background tasks to function.

## Requirements

The project requires additional Python packages listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## Notes

- Ensure that you have configured your database and other settings correctly in `settings.py`.
- If you encounter issues, check the logs or consult the documentation for further guidance.
