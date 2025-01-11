# Protobase Project

## Overview
Protobase is a web application that provides user authentication, two-factor authentication (2FA), and database management functionalities. The project is built using Flask for the backend and SQLite for the database.

## Features
- User Signup and Signin
- Two-Factor Authentication (2FA) via OTP
- Password Reset via Email
- Project Management Dashboard
- CRUD Operations on Databases

## Technologies Used
- Python
- Flask
- SQLite
- JavaScript
- HTML/CSS

## Usage
- Email Signup: https://protobase.pythonanywhere.com/auth_api/email-signup/
- Username Signup: https://protobase.pythonanywhere.com/auth_api/user-signup/
- Email Signin: https://protobase.pythonanywhere.com/auth_api/email-signin/
- Username Signin: https://protobase.pythonanywhere.com/auth_api/user-signin/

### User Authentication
- **Signup**: Users can sign up using their email and username.
- **Signin**: Users can sign in using their credentials.
- **OTP**: An OTP is sent to the user's email for verification.
- **Password Reset**: Users can reset their password via a link sent to their email.

### Project Management
- **Dashboard**: Users can view their projects on the dashboard.
- **Add Project**: Users can add new projects.
- **Delete Project**: Users can delete existing projects.

### Database Management
- **Create Table**: Users can create new tables in their project databases.
- **Insert Data**: Users can insert data into tables.
- **Read Data**: Users can read data from tables.
- **Update Data**: Users can update existing data in tables.
- **Delete Data**: Users can delete data from tables.

## API Endpoints

### Authentication API
- **Email Signup**: `/auth_api/email-signup/`
- **Username Signup**: `/auth_api/user-signup/`
- **Email Signin**: `/auth_api/email-signin/`
- **Username Signin**: `/auth_api/user-signin/`

### Password Routes
- **Forgot Password**: `/forgot_password`
- **Reset Password**: `/reset_password/<username>`

### Database CRUD Routes
- **Create Table**: `/create_table`
- **Insert Data**: `/insert_data`
- **Read Data**: `/read_data`
- **Update Data**: `/update_data`
- **Delete Data**: `/delete_data`
- **Get Tables**: `/get_tables`
- **DB CRUD Interface**: `/db_crud/<project_name>`

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License
This project is licensed under the MIT License.