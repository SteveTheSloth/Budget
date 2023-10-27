from django.db import models
from datetime import timedelta, date
from user.models import MyUser, UserGroup
from typing import Union, Dict


class Transaction(models.Model):
    """Model representing individual transactions that can be added to the budget. Includes calculating methods."""
    types = (("Income", "Income"), ("Expense", "Expense"), ("Loan", "Loan"))

    repeat_patterns = (
        ("one off", "one off"),
        ("monthly", "monthly"),
        ("weekly", "weekly"),
        ("every two weeks", "every two weeks"),
        ("every three weeks", "every three weeks"),
        ("every four weeks", "every four weeks"),
    )
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=25, choices=types, default="Expense")
    name = models.CharField(max_length=200)
    purpose = models.CharField(max_length=200)
    amount = models.FloatField(max_length=6)
    due_date = models.DateField(default=date.today())
    repeat_pattern = models.CharField(
        max_length=25, choices=repeat_patterns, default="one off"
    )
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True, editable=False)
    group = models.ForeignKey(
        UserGroup, blank=True, null=True, default=None, on_delete=models.CASCADE
    )

    def monthamount(self, month: int, year: int) -> Union[int, float]:
        """Takes month and year as arguments and calculates and returns the total amount of a transaction for that month/year."""
        amount_dict = self.active_month(month, year)
        amount = 0
        for value in amount_dict.values():
            amount += value
        return amount

    def __str__(self):
        return f"{self.name}"

    def dict(self) -> Dict:
        """Returns a dictionary of useful information for display purposes."""
        attributes = {
            "Name": self.name,
            "Purpose": self.purpose,
            "Type": self.transaction_type,
            "Amount": self.amount,
            "Due On": self.due_date,
            "Repeat Pattern": self.repeat_pattern,
            "Website": self.website,
            "E-Mail": self.email,
            "Telephone Number": self.telephone,
            "End Date": self.end_date,
            "Added On": self.date_added,
        }
        return attributes

    def day_balance(self, month: int, year: int) -> Union[int, float]:
        """Takes month and year as arguments and returns a dictionary of format {day: amount} for that month/year depending on the repeat pattern of the transaction. Ignores loans."""
        
        if (
            self.transaction_type == "Loan"
            or self.due_date.month > month
            and self.due_date.year >= year
            or self.due_date.year > year
        ):
            return dict()
        if self.end_date != None:
            if self.end_date.month < month and self.end_date.year <= year:
                return dict()

        if self.repeat_pattern == "one off":
            return self.one_off_day()

        elif self.repeat_pattern == "monthly":
            return self.one_off_day()

        elif self.repeat_pattern == "weekly":
            return self.weekly_day(month, timedelta(weeks=1))

        elif self.repeat_pattern == "every two weeks":
            return self.weekly_day(month, timedelta(weeks=2))

        elif self.repeat_pattern == "every three weeks":
            return self.weekly_day(month, timedelta(weeks=3))

        else:
            return self.weekly_day(month, timedelta(weeks=4))

    def one_off_day(self) -> Dict[int, Union[int, float]]:
        """Returns a dictionary of format {day: amount} for a one_off or monthly recurring transaction."""
        dayly_transaction_dict = dict()

        if self.transaction_type == "Expense":
            dayly_transaction_dict[self.due_date.day] = -self.amount
        else:
            dayly_transaction_dict[self.due_date.day] = self.amount

        return dayly_transaction_dict

    def weekly_day(self, month: int, delta: int) -> Dict[int, Union[int, float]]:
        """Takes month and delta (number of weeks in between repeats) as arguments and returns a dictionary of format {day: amount} for a 1/2/3/4-weekly recurring transaction."""
        due_date = self.due_date
        dayly_transaction_dict = dict()

        while due_date.month != month:
            due_date += delta

        while due_date.month == month:
            if self.transaction_type == "Expense":
                dayly_transaction_dict[due_date.day] = -self.amount
            else:
                dayly_transaction_dict[due_date.day] = self.amount

            due_date += delta

        return dayly_transaction_dict

    def active_month(self, month: int = date.today().month, year: int = date.today().year) -> Union[int, float]:
        """Takes month and year as arguments and returns the total amount for a transaction for that month/year"""
        if (
            self.due_date.month > month
            and self.due_date.year >= year
            or self.transaction_type == "Loan"
        ):
            return 0
        elif self.end_date != None:
            if self.end_date.month < month and self.end_date.year <= year:
                return 0
            else:
                pass

        else:
            if self.repeat_pattern == "one off":
                if self.due_date.month == month:
                    if self.transaction_type == "Expense":
                        return -self.amount
                    else:
                        return self.amount
                else:
                    return 0

            elif self.repeat_pattern == "monthly":
                if self.transaction_type == "Expense":
                    return -self.amount
                else:
                    return self.amount

            elif self.repeat_pattern == "weekly":
                return self.weekly_month(month, timedelta(weeks=1))

            elif self.repeat_pattern == "every two weeks":
                return self.weekly_month(month, timedelta(weeks=2))

            elif self.repeat_pattern == "every three weeks":
                return self.weekly_month(month, timedelta(weeks=3))

            else:
                return self.weekly_month(month, timedelta(weeks=4))

    def weekly_month(self, month: int, delta: int) -> Union[int, float]:
        """Takes month and delta (number of weeks in between repeats) as arguments and returns total amoount for transaction in a month if it has a 1/2/3/4-weekly repeat pattern"""
        due_date = self.due_date
        amount = 0

        while due_date.month != month:
            due_date += delta

        while due_date.month == month:
            amount += self.amount
            due_date += delta

        if self.transaction_type == "Expense":
            return -amount
        else:
            return amount
