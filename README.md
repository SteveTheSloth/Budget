# Multi-Page Budget Balancing Web Application with Django

This Application is intended to help groups and individuals to balance and organise budgets.

It includes user authentication, group-creation and functionality to join existing groups (for shared budgets), transaction-creation (epenses, incomes, loans), and different screens to view transactions/balances (overview over all transactions of any one type, detailed view of any single transaction, total monthly balance, calendar view with transactions being shown on their due date(s)).

It is built using Django, as well as pure HTML and CSS.

## Installation

To test functionality, clone repository and create a file named **secrets.py** containing a variable called **skey** which stores your secret key in the budget/budget directory.

Create a virtual environment using pipenv and install dependencies.

Run **python budget/manage.py migrate** to apply migrations & create database.

Run **python budget/manage.py runserver** to start app on local server.

```bash
pipenv shell
pipenv install -r requirements.txt
python budget/manage.py migrate
python budget/manage.py runserver
```

## Usage

Open the application that should now be running on your local server at http://127.0.0.1:8000 (or on port specified by **python budget/manage.py runserver** command). You can now create a new user and test the application's features! Please disregard the rather poor styling of the application. This should be updated in the future, as I now have a much better understanding of front-end technologies & styling.

## License

[MIT](https://choosealicense.com/licenses/mit/)
