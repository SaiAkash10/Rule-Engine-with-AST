# Rule-Engine-with-AST-main

Here's a complete `README.md` for project:

```markdown
# Rule-Engine-with-AST

A simple Flask-based rule engine application with a user-friendly UI, API, and backend. This application determines user eligibility based on attributes like age, department, income, spend, etc. The system uses an Abstract Syntax Tree (AST) to represent conditional rules and allows for dynamic creation, combination, and modification of these rules.

## Features

- Add new rules to the database.
- Evaluate rules against provided data.
- Combine multiple rules using AND/OR operators.
- Fetch and display existing rules.

## Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Rule-Engine-with-AST
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Run the application

1. **Start the Flask application:**

   ```bash
   python app.py
   ```

2. **Access the application:**
   Open your web browser and navigate to `http://127.0.0.1:5000`.

## Usage

- **Add Rule:** Enter a new rule to add it to the database.
- **Evaluate Rule:** Input a rule or select from the existing rules to evaluate against provided JSON data.
- **Combine Rules:** Enter multiple rules separated by new lines or select from existing rules to combine them.
- **Fetch Rules:** View existing rules stored in the database.

## Database

The application uses SQLite to store rules. The database file will be created automatically upon running the application for the first time.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask for web framework
- SQLAlchemy for database ORM
```

Feel free to customize any sections as needed!