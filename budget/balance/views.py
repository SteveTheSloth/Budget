from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import CreateTransactionForm
from datetime import date
from .models import Transaction
from user.models import MyUser, UserGroup

month_str = str(date.today().month)
year_str = str(date.today().year)
month_year_int = int(month_str + year_str)


def find_queryset(user_id: int) -> QuerySet:
    """Determines if a user is acting as an individual or a group and returns queryset accordingly."""
    active_user = MyUser.objects.get(id=user_id)
    if active_user.as_group:
        queryset = Transaction.objects.filter(group=active_user.get_active_group())
    else:
        queryset = Transaction.objects.filter(user=active_user, group__isnull=True)
    return queryset


class BalanceView(LoginRequiredMixin, ListView):
    """Class based view for Balance."""
    
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
        """Update and return show year property representing currently displayed year."""
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
            self._prev_month_year = int(
                str(self._show_month - 1) + str(self._show_year)
            )
        else:
            self._prev_month_year = int(str(12) + str(self._show_year - 1))

        return self._prev_month_year

    @prev_month_year.setter
    def prev_month_year(self, value):
        """Set prev month year property to value argument."""
        self._prev_month_year = value

    @property
    def next_month_year(self):
        """Update and return next month year property representing the month and year following the currently displayed month."""
        if self._show_month != 12:
            self._next_month_year = int(
                str(self._show_month + 1) + str(self._show_year)
            )
        else:
            self._next_month_year = int(str(1) + str(self._show_year + 1))

        return self._next_month_year

    @next_month_year.setter
    def next_month_year(self, value):
        """Set next month year property to value argument."""
        self._next_month_year = value

    def group_members(self):
        """Return group names of which requesting user is a member."""
        if self.request.method == "GET":
            groups = UserGroup.objects.filter(members=self.request.user.id)
            group_names = [i.name for i in groups]
        return group_names

    def get_queryset(self):
        """Return queryset based on requesting user's id."""
        queryset = find_queryset(self.request.user.id)
        return queryset

    def month_amount(self):
        """Calculate and return total amount for user for active month."""
        month_amount = 0
        queryset = self.get_queryset()
        for i in queryset:
            month_amount += i.active_month(month=self.show_month, year=self.show_year)
        return month_amount

    def get_context_data(self, **kwargs):
        """Collect context data to be displayed in html."""
        context = super().get_context_data(**kwargs)
        context["month_amount"] = self.month_amount()
        context["show_month"] = date(month=self.show_month, year=1, day=1).strftime(
            "%B"
        )
        context["show_year"] = self.show_year
        context["prev_month_year"] = self.prev_month_year
        context["next_month_year"] = self.next_month_year
        context["groups"] = self.group_members()
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Class based view for Transaction Details."""
    
    def get_queryset(self):
        """Return queryset based on requesting user's id."""
        queryset = find_queryset(self.request.user.id)
        return queryset

    def get_context_data(self, **kwargs):
        """Collect context data to be displayed in html."""
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()
        context["items_dict"] = transaction.dict().items()
        return context


class ExpenseListView(LoginRequiredMixin, ListView):
    """Class based view for List of expenses."""
    
    def get_queryset(self):
        """Return queryset based on requesting user's id and type of transaction being Expense."""
        queryset = find_queryset(self.request.user.id)
        queryset = queryset.filter(transaction_type="Expense")
        return queryset


class IncomeListView(LoginRequiredMixin, ListView):
    """Class based view for List of Incomes."""
    
    def get_queryset(self):
        """Return queryset based on requesting user's id and type of transaction being Income."""
        queryset = find_queryset(self.request.user.id)
        queryset = queryset.filter(transaction_type="Income")
        return queryset


class LoanListView(LoginRequiredMixin, ListView):
    """Class based view for List of Loans."""
    
    def get_queryset(self):
        """Return queryset based on requesting user's id and type of transaction being Loan."""
        queryset = find_queryset(self.request.user.id)
        queryset = queryset.filter(transaction_type="Loan")
        return queryset


def create_transaction_view(request):
    """Functional view for creating a transaction. If request method is Post: Take user input in create transaction form and saves a new transaction if the input is valid. Else: display form."""
    if request.method == "POST":
        form = CreateTransactionForm(request.POST)

        if form.is_valid():
            newtrans = form.save(commit=False)
            newtrans.user = request.user
            if request.user.as_group:
                newtrans.group = UserGroup.objects.get(name=request.user.group)
            newtrans.save()
            form.save_m2m()
            return redirect("balance")
    else:
        form = CreateTransactionForm()
    return render(request, "balance/create.html", {"form": form})


def select_group_view(request):
    """Functional view for selecting a group. Gets groups of which user is a member and passes their names as context to be displayed in html. If user selects a group, activate selected group for user.
    if user selects switching to individual account, deactivate group for user."""
    groups = UserGroup.objects.filter(members=request.user.id)
    group_names = [i.name for i in groups]
    if request.method == "POST":
        if request.POST.get("groups") in group_names:
            request.user.set_active_group(request.POST.get("groups"))
            request.user.save()

            return redirect("balance")
        elif request.POST.get("switch") == "Switch to individual account":
            request.user.as_group = False
            request.user.group = None
            request.user.save()

            return redirect("welcome")
    else:
        groups = UserGroup.objects.filter(members=request.user.id)
        group_names = [i.name for i in groups]
        return render(request, "balance/group_select.html", {"groups": group_names})
