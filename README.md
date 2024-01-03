# Functional Testing with Unittest Python

This project includes functional test cases implemented using the `unittest` framework in Python. The tests are designed to validate user management scenarios, such as login with valid and invalid credentials, and user lock functionality.

## Project Structure

### Files and Directories

- **Files:**
  - `README.md`: This file, providing an overview of the project and its structure.
  - `requirements.txt`: Requirements file listing necessary Python dependencies.
  - `test_login.py`: Test script for login scenarios.
  - `test_usermanagement.py`: Test script for user management scenarios.
  - `test_generateToken.py`: Test script for generating tokens (dependency for login tests).
  - `utils`: Directory containing utility modules.
  
- **Directories:**
  - `__pycache__`: Python cache directory.
  - `utils`: Subdirectory within `utils` containing utility modules.
    - `__init__.py`: Initialization file for the `utils` package.
    - `__pycache__`: Python cache directory for `utils`.
    - `configloader.py`: Module for loading configuration.
    - `mssqlutil.py`: Module for MSSQL database utilities.

## Usage

1. **Install Dependencies:**
   - Install the required Python dependencies using `pip install -r requirements.txt`.

2. **Test Execution:**
   - Run the tests using the command: `python -m unittest test_login.py test_usermanagement.py`.

## Test Scenarios

1. **Login with Invalid Credentials (`test_LoginWithInvalidCredentials`):**
   - Tests the login functionality with invalid credentials.
   - Covers scenarios such as incorrect passwords.

2. **Login with Valid Credentials (`test_LoginWithValidCredentials`):**
   - Tests the login functionality with valid credentials.
   - Includes user creation, password setting, password reset, and successful login.

3. **Lock User by Logging in Multiple Times (`test_LockUser`):**
   - Tests the scenario where a user gets locked by attempting to log in multiple times with incorrect credentials.
   - Validates that the user is locked after a certain number of unsuccessful login attempts.

## Configuration

- The project relies on a configuration file to set up environment-specific parameters. Ensure that the configuration is correctly set before running the tests.

## References

- [unittest Documentation](https://docs.python.org/3/library/unittest.html)

## Change History

- [Refer to the change history in the source code for detailed updates.](test_login.py)

