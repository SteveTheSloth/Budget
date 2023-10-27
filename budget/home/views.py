from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password, check_password
from balance.models import Transaction
from user.models import MyUser, UserGroup
from user.forms import RegistrationForm, GroupRegistrationForm
from datetime import date
import calendar


month_str = str(date.today().month)
year_str = str(date.today().year)
month_year_int = int(month_str + year_str)


class WelcomeView(LoginRequiredMixin, ListView):
    """Class based view for Welcome page."""
    
    @property
    def show_month(self):
        """Update and return show month property representing currently displayed month."""
        try:
            month_year = self.kwargs["monthyear"]

            if len(str(month_year)) == 6:
                show_month = int(str(month_year)[:2])
            else:
                show_month = int(str(month_year)[:1])

        except KeyError:
            show_month = int(month_str)

        self._show_month = show_month
        return self._show_month

    @show_month.setter
    def show_month(self, value):
        """Set show month property to value argument."""
        self._show_month = value

    @property
    def show_year(self):
        """Update and return show year property representing currently displayed month."""
        try:
            month_year = self.kwargs["monthyear"]
            self._show_year = int(str(month_year)[-4:])
        except KeyError:
            self._show_year = int(year_str)

        return self._show_year

    @show_year.setter
    def show_year(self, value):
        """Set show year property to value argument."""
        self._show_year = value

    @property
    def prev_month_year(self):
        """Update and return prev month year property representing the month and year priror to the currently displayed month."""
        if self._show_month != 1:
            self._prev_month_year = (self._show_month - 1, self._show_year)
        else:
            self._prev_month_year = (12, self._show_year - 1)

        return self._prev_month_year

    @prev_month_year.setter
    def prev_month_year(self, value):
        """Set prev month year property to value argument."""
        self._prev_month_year = value

    @property
    def next_month_year(self):
        """Update and return next month year property representing the month and year following the currently displayed month."""
        if self._show_month != 12:
            self._next_month_year = (self._show_month + 1, self._show_year)
        else:
            self._next_month_year = (1, self._show_year + 1)

        return self._next_month_year

    @next_month_year.setter
    def next_month_year(self, value):
        """Set next month year property to value argument."""
        self._next_month_year = value

    def get_queryset(self):
        """Return queryset based on requesting user's id and if that user is currently treated as a group member or individual."""
        active_user = MyUser.objects.get(id=self.request.user.id)
        if active_user.as_group:
            queryset = Transaction.objects.filter(group=active_user.get_active_group())
        else:
            queryset = Transaction.objects.filter(user=active_user, group__isnull=True)
        return queryset

    def dayly_transactions(self):
        """Return a list of days for the calendar view, where every day is represented as a tuple (day, None/list of transactions)."""

        dayly_transactions_dict = dict()
        for transaction in self.get_queryset():
            for key, value in transaction.day_balance(
                self.show_month, self.show_year
            ).items():
                if key not in dayly_transactions_dict:
                    dayly_transactions_dict[key] = [value]
                else:
                    dayly_transactions_dict[key].append(value)

        transaction_tuples = [
            (i, None)
            if i not in dayly_transactions_dict
            else (i, dayly_transactions_dict.get(i))
            for i in range(
                1, calendar.monthrange(self.show_year, self.show_month)[1] + 1
            )
        ]
        return transaction_tuples

    def weeks(self):
        """Return the list of tuples from dayly_transactions method split into weeks according to the active month.
        Also return a list of first and last days of next/previous month to eventually style differently."""

        transaction_tuples = self.dayly_transactions()
        prev_month_num_days = calendar.monthrange(
            self.prev_month_year[1], self.prev_month_year[0]
        )[1]
        curr_month_weekday, curr_month_num_days = calendar.monthrange(
            self.show_year, self.show_month
        )
        last_days = [
            prev_month_num_days - i for i in range(curr_month_weekday - 1, -1, -1)
        ]

        first_week = [transaction_tuples[i] for i in range(7 - len(last_days))]

        second_week = [
            transaction_tuples[i] for i in range(first_week[-1][0], 14 - len(last_days))
        ]

        third_week = [
            transaction_tuples[i]
            for i in range(second_week[-1][0], 21 - len(last_days))
        ]

        fourth_week = [
            transaction_tuples[i] for i in range(third_week[-1][0], 28 - len(last_days))
        ]

        weeks = [first_week, second_week, third_week, fourth_week]

        if fourth_week[-1][0] == curr_month_num_days:
            fifth_week = None
            sixth_week = None

        else:
            fifth_week = [
                transaction_tuples[i]
                for i in range(fourth_week[-1][0], len(transaction_tuples))
            ]
            weeks.append(fifth_week)

        if len(fifth_week) <= 7:
            first_days = [i for i in range(1, 7) if len(fifth_week) + i <= 7]
            if len(first_days) == 0:
                first_days = None
            sixth_week = None
        else:
            sixth_week = [
                transaction_tuples[i]
                for i in range(fifth_week[-1][0], 35 - len(last_days))
            ]
            weeks.append(sixth_week)
            first_days = [i for i in range(1, 7) if len(sixth_week) + i <= 7]

        last_week = weeks[-1]
        weeks = weeks[:-1]
        return (last_days, weeks, first_days, last_week)

    def get_context_data(self, **kwargs):
        """Collect context data to be displayed in html."""
        context = super().get_context_data(**kwargs)
        last_days, weeks, first_days, last_week = self.weeks()
        context["last_days"] = last_days
        context["weeks"] = weeks
        context["last_week"] = last_week
        context["first_days"] = first_days

        show_date = date(year=self.show_year, month=self.show_month, day=1)
        context["month"] = show_date.strftime("%B")
        context["year"] = show_date.year

        prev_month = int(str(self.prev_month_year[0]) + str(self.prev_month_year[1]))
        next_month = int(str(self.next_month_year[0]) + str(self.next_month_year[1]))
        context["prev_month"] = prev_month
        context["next_month"] = next_month
        return context


def registration(request):
    """Functional view for user registration. Create a new user if method is Post and form is valid. Else display user registration form."""
    if request.method == "GET":
        form = RegistrationForm()
        return render(request, "registration/register.html", {"form": form})

    elif request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("welcome")

        else:
            return render(request, "registration/register.html", {"form": form})


def registration_group(request):
    """Functional view for group registration. Create a new group with user automatically added as member if method is Post and form is valid. Else display group registration form."""
    if request.method == "GET":
        form = GroupRegistrationForm()
        return render(request, "registration/register_group.html", {"form": form})

    elif request.method == "POST":
        form = GroupRegistrationForm(request.POST)

        if form.is_valid():
            password = make_password(request.POST["password"])
            name = request.POST["name"]
            group = UserGroup(name=name, password=password)
            group.save()
            group.members.add(MyUser.objects.get(id=request.user.id))
            return redirect("welcome")

        else:
            return render(request, "registration/register_group.html", {"form": form})


def success_group(request, name):
    """Functional view for succesful group registration. Displays group name and success message."""
    return render(request, "registration/success_group.html", {"name": name})


def login_group(request):
    """Functional view for joining an existing group. Check for group name and password and add user to group if both are correct."""
    if request.method == "GET":
        return render(request, "registration/login_group.html")

    elif request.method == "POST":
        # Check if Group with provided name exists.
        try:
            group = UserGroup.objects.get(name=request.POST.get("Group Name"))
        except:
            return render(
                request,
                "registration/login_group.html",
                {"group_exists": True, "name": request.POST.get("Group Name")},
            )

        if check_password(request.POST.get("Password"), group.password):
            # If Group exists and provided password is correct, check if user is already a member of the group.
            try:
                group.members.get(id=request.user.id)
                return render(
                    request,
                    "registration/login_group.html",
                    {"member": True, "name": request.POST.get("Group Name")},
                )
            except:
                group.members.add(MyUser.objects.get(id=request.user.id))
                group.nr_of_members += 1
                group.save()
                return redirect("success_group", group.name)

        else:
            return render(
                request, "registration/login_group.html", {"wrong_password": True}
            )
