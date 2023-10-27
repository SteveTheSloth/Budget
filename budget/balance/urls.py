from django.urls import path, reverse_lazy
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .views import (
    BalanceView,
    TransactionDetailView,
    ExpenseListView,
    IncomeListView,
    LoanListView,
    create_transaction_view,
    select_group_view,
)


urlpatterns = [
    path(
        "<int:monthyear>",
        BalanceView.as_view(template_name="balance/balance.html"),
        name="balance",
    ),
    path("", BalanceView.as_view(
        template_name="balance/balance.html"), name="balance"),
    path(
        "expenses",
        ExpenseListView.as_view(template_name="balance/expenses.html"),
        name="expenses",
    ),
    path(
        "incomes",
        IncomeListView.as_view(template_name="balance/incomes.html"),
        name="incomes",
    ),
    path(
        "loans", LoanListView.as_view(template_name="balance/loans.html"), name="loans"
    ),
    path(
        "details/<int:pk>/",
        TransactionDetailView.as_view(template_name="balance/details.html"),
        name="details",
    ),
    path("create", login_required(create_transaction_view), name="create"),
    path("group_select", login_required(select_group_view), name="group_select"),
    path(
        "<int:pk>/update",
        login_required(
            UpdateView.as_view(
                model=Transaction,
                template_name="balance/update.html",
                fields=[
                    "name",
                    "purpose",
                    "transaction_type",
                    "amount",
                    "due_date",
                    "repeat_pattern",
                    "website",
                    "email",
                    "telephone",
                    "end_date",
                ],
                success_url=reverse_lazy("balance"),
            )
        ),
        name="update",
    ),
    path(
        "<int:pk>/delete",
        login_required(
            DeleteView.as_view(
                model=Transaction,
                template_name="balance/delete.html",
                success_url=reverse_lazy("balance"),
            )
        ),
        name="delete",
    ),
]
