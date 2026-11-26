import math
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from CTkXYFrame import CTkXYFrame
from tkinter import *
from tkinter import ttk
import storage
import logic
from general import *

ctk.set_appearance_mode("system")

class Application(ctk.CTk):
    """Main desktop application window for Penny Personal Finance."""

    SIDEBAR_WIDTH = 230
    MAX_MAIN_WIDTH = 1200

    PALETTE = {
        "BG_SIDEBAR": "#FFFFFF",
        "BG_CANVAS": "#F8F9FA",
        "BG_CARD": "#FFFFFF",
        "BG_DARK_CARD": "#24372B",
        "ACCENT_ORANGE": "#F0643B",
        "ACCENT_ORANGE_LIGHT": "#FDECE6",
        "BORDER_COLOR": "#E5E7EB",
        "TEXT_PRIMARY": "#111827",
        "TEXT_MUTED": "#6B7280",
    }

    views: dict[str, ctk.CTkFrame] = {}
    transactions: list[dict] = []
    current_view:View | None = None

    def __init__(self):
        """Initialize the main window, sidebar, and switchable views."""
        super().__init__()
        Application._instance = self
        self.title("Penny - Personal Finance Dashboard")
        self.geometry("1380x880")
        self.minsize(960, 680)
        self.configure(fg_color=self.PALETTE["BG_CANVAS"])

        self.current_frame:View | None = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.load_transactions()
        self._build_sidebar()
        self._build_main_area()
        self._select_nav("Overview")

    def _build_sidebar(self):
        """Build Sidebar with brand, nav, and bottom profile/settings section."""
        sidebar = ctk.CTkFrame(
            self,
            width=self.SIDEBAR_WIDTH,
            fg_color=self.PALETTE["BG_SIDEBAR"],
            corner_radius=0,
            border_width=1,
            border_color=self.PALETTE["BORDER_COLOR"],
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        brand_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_row.pack(fill="x", padx=20, pady=(22, 20))

        logo = ctk.CTkLabel(
            brand_row,
            text="P",
            width=30,
            height=30,
            corner_radius=8,
            fg_color=self.PALETTE["ACCENT_ORANGE"],
            text_color="white",
            font=("", 16, "bold"),
        )
        logo.pack(side="left")

        ctk.CTkLabel(
            brand_row,
            text="enny",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 18, "bold"),
        ).pack(side="left", padx=0)

        ctk.CTkLabel(
            sidebar,
            text="WORKSPACE",
            text_color=self.PALETTE["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w", padx=22, pady=(4, 8))

        self.nav_buttons = {}
        nav_items = ["Overview", "Transactions","Budgets"]

        for name in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"   {name}",
                anchor="w",
                height=38,
                corner_radius=8,
                font=("", 13, "bold"),
                command=lambda n=name: self._select_nav(n),
            )
            btn.pack(fill="x", padx=14, pady=2)
            self.nav_buttons[name] = btn

        ctk.CTkFrame(sidebar, height=1, fg_color=self.PALETTE["BORDER_COLOR"]).pack(
            side="bottom", fill="x", padx=16, pady=8
        )

    def _select_nav(self, active_name: str):
        """Highlight active sidebar button and change dashboard view."""
        for name, btn in self.nav_buttons.items():
            if name == active_name:
                btn.configure(
                    fg_color=self.PALETTE["ACCENT_ORANGE_LIGHT"],
                    hover_color=self.PALETTE["ACCENT_ORANGE_LIGHT"],
                    text_color=self.PALETTE["ACCENT_ORANGE"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color="#F3F4F6",
                    text_color=self.PALETTE["TEXT_MUTED"],
                )
        self.switch_view(active_name.lower().replace(" ", "_"))

    def _build_main_area(self):
        """Build Main Area container and initialize switchable frames."""
        self.main_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.main_wrapper.grid(row=0, column=1, sticky="nsew")
        self.main_wrapper.grid_rowconfigure(0, weight=1)
        self.main_wrapper.grid_columnconfigure(0, weight=1)

        Application.views = {
            "overview": Overview,
            "add_transaction": AddTransaction,
            "transactions": Transactions,
            "budgets": Budgets,
            "edit_budgets": EditBudgets,
        }

    @classmethod
    def switch_view(cls, target_view: str):
        """Switch the main area to display the view with the given name and hide other views."""
        if target_view not in cls.views:
            return
        


        if Application.current_view:
            if isinstance(Application.current_view,Application.views[target_view]):
                 return
            del Application.current_view
        target_frame:View = cls.views[target_view](cls._instance.main_wrapper)
        Application.current_view = target_frame
        target_frame.grid_propagate(False)
        target_frame.grid(row=0, column=0, sticky="nsew")

    @classmethod
    def load_transactions(cls):
        """Load transactions from storage into the memory cache."""
        cls.transactions = storage.get_transactions()

class View(ctk.CTkFrame):

    def _validate_numeric_keystroke(self, proposed_text: str) -> bool:
        """Allow empty string, digits, and at most one decimal point."""
        if proposed_text == "":
            return True
        if proposed_text.count(".") > 1:
            return False
        cleaned = proposed_text.replace(".", "", 1)
        return cleaned.isdigit()

    def _attach_numeric_guard(self, entry: ctk.CTkEntry):
        """Block non-numeric keystrokes while allowing decimal input and deletion."""
        vcmd = (self.register(self._validate_numeric_keystroke), "%P")
        entry.configure(validate="key", validatecommand=vcmd)


    def _make_card(self, parent, dark=False, **kwargs):
        """Create a styled card container matching the application palette."""
        return ctk.CTkFrame(
            parent,
            fg_color=self.palette["BG_DARK_CARD"] if dark else self.palette["BG_CARD"],
            corner_radius=14,
            border_width=0 if dark else 1,
            border_color=self.palette["BORDER_COLOR"],
            **kwargs,
        )

    def _render_transaction_row(self,parent, idx: int, transactions: dict):
        """Render a single transaction row inside the scrollable table body."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=idx * 2, column=0, sticky="ew", padx=6, pady=4)

        merchant = str(transactions.get("merchant", "Untitled"))
        category = str(transactions.get("category", "Other"))
        transaction_type = str(transactions.get("type", "expense")).capitalize()
        date_str = str(transactions.get("date", ""))
        raw_amount = transactions.get("amount", 0)

        try:
            amount_val = float(raw_amount)
        except (TypeError, ValueError):
            amount_val = 0.0

        is_income = transaction_type.lower() == "income"
        sign = "+" if is_income else "-"
        amount_text = f"{sign}{amount_val:,.2f} MMK"

        ctk.CTkLabel(
            row,
            text=merchant,
            width=240,
            anchor="w",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            row,
            text=category,
            width=150,
            anchor="w",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            row,
            text=transaction_type,
            width=100,
            anchor="w",
            text_color="#15803D" if is_income else self.palette["TEXT_MUTED"],
            font=("", 12, "bold" if is_income else "normal"),
        ).grid(row=0, column=2, sticky="w")

        ctk.CTkLabel(
            row,
            text=date_str,
            width=120,
            anchor="w",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).grid(row=0, column=3, sticky="w")

        ctk.CTkLabel(
            row,
            text=amount_text,
            width=130,
            anchor="e",
            text_color="#15803D" if is_income else self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=0, column=4, sticky="e")

        delete_btn = ctk.CTkButton(
            row,
            text="🗑",
            width=30,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#FEE2E2",
            text_color="#DC2626",
            font=("", 20),
            command=lambda record=transactions: self._confirm_delete(record),
        )
        delete_btn.grid(row=0, column=5, padx=(8, 0), sticky="e")

        ctk.CTkFrame(
            parent, height=1, fg_color=self.palette["BORDER_COLOR"]
        ).grid(row=idx * 2 + 1, column=0, sticky="ew", padx=6)

class Overview(View):
    """Main overview dashboard frame displaying KPIs, charts, and summaries."""

    def __init__(self, parent, palette=Application.PALETTE):
        """Initialize the overview dashboard frame."""
        super().__init__(parent, fg_color="transparent")
        self.palette = palette

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure(3, weight=3)
        self.grid_columnconfigure(0, weight=1)

        self._build_header_row()
        self._build_kpi_row()
        self._build_middle_row()
        self._build_bottom_row()

    def refresh(self):
        self._build_header_row()
        self._build_kpi_row()
        self._build_middle_row()
        self._build_bottom_row()

    def _build_header_row(self):
        """Render the greeting header, month selector, and add transaction CTA."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="YOUR MONEY, AT A GLANCE",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="A little clarity. A lot of possibility.",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 22, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            left,
            text="Let's make your money work for you.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

    def _build_kpi_row(self):
        """Render the four summary metric cards across the top row."""
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))

        cards = [
            ("Total balance", f"{logic.calculate_current_balance(400000,Application.transactions)} MMK", True),  
            ("Income", f"{logic.calculate_total_income(Application.transactions)} MMK", False),
            ("Expenses", f"{logic.calculate_total_expenses(Application.transactions)} MMK", False),
            ("Net savings", f"{logic.calculate_net_cash_flow(Application.transactions)} MMK", False),
        ] #TODO: Chnage the budget

        for col, (title, value, is_dark) in enumerate(cards):
            kpi_row.grid_columnconfigure(col, weight=1, uniform="kpi")
            card = self._make_card(kpi_row, dark=is_dark, height=115)
            card.grid(row=0, column=col, sticky="nsew", padx=6)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                text_color="#D1FAE5" if is_dark else self.palette["TEXT_MUTED"],
                font=("", 12),
            ).pack(anchor="w", padx=18, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=value,
                text_color="#FFFFFF" if is_dark else self.palette["TEXT_PRIMARY"],
                font=("", 22, "bold"),
            ).pack(anchor="w", padx=18)

    def _build_middle_row(self):
        """Render the cash flow and category breakdown chart cards."""
        mid = ctk.CTkFrame(self, fg_color="transparent")
        mid.grid(row=2, column=0, sticky="nsew", padx=22, pady=8)
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=2, uniform="split")
        mid.grid_columnconfigure(1, weight=1, uniform="split")

        left_card = self._make_card(mid)
        left_card.grid(row=0, column=0, sticky="nsew", padx=6)
        ctk.CTkLabel(
            left_card,
            text="Cash flow",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))


        right_card = self._make_card(mid)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="Where it goes",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))

    def _build_bottom_row(self):
        """Render the recent transactions list and savings goals cards."""
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=3, column=0, sticky="nsew", padx=22, pady=(8, 22))
        bot.grid_rowconfigure(0, weight=1)
        bot.grid_columnconfigure(0, weight=2, uniform="split")
        bot.grid_columnconfigure(1, weight=1, uniform="split")

        left_card = self._make_card(bot)
        left_card.grid(row=0, column=0, sticky="nsew", padx=6)
        left_card.grid_rowconfigure(0, weight=0)
        left_card.grid_rowconfigure(1, weight=1)
        left_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            left_card,
            text="Recent transactions",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))
        transactions_table = CTkXYFrame(left_card, fg_color="transparent")
        transactions_table.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        transactions_table.grid_columnconfigure(0, weight=1)

        for idx,transaction in enumerate(Application.transactions):
            self._render_transaction_row(transactions_table,idx,transaction)

        right_card = self._make_card(bot)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="A little closer to your goals",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))

class AddTransaction(View):
    """UI form view for creating a new financial transaction."""

    def __init__(self, parent, palette=Application.PALETTE):
        """Initialize the transaction form frame."""
        super().__init__(parent, fg_color="transparent")
        self.palette = palette

        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_form_card()

    def refresh(self):
        self._build_header()
        self._build_form_card()

    def _build_header(self):
        """Render the top navigation back button and page title."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))

        ctk.CTkButton(
            header,
            text="← Back to Overview",
            width=140,
            height=30,
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color=self.palette["TEXT_MUTED"],
            anchor="w",
            font=("", 12, "bold"),
            command=lambda: Application.switch_view("overview"),
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="NEW ENTRY",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Add a transaction",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 22, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            header,
            text="Record a new income or expense entry to your workspace.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

    def _build_form_card(self):
        """Render the centered card containing the transaction input fields."""
        card = ctk.CTkFrame(
            self,
            fg_color=self.palette["BG_CARD"],
            corner_radius=14,
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
        )
        card.grid(row=1, column=0, sticky="ew", padx=28, pady=(4, 24))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card,
            text="Transaction Type",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=24, pady=(22, 6))

        self.type_var = ctk.StringVar(value="Expense")
        self.type_selector = ctk.CTkSegmentedButton(
            card,
            values=["Expense", "Income"],
            variable=self.type_var,
            height=36,
            selected_color=self.palette["ACCENT_ORANGE"],
            selected_hover_color="#D9532B",
            unselected_color="#F3F4F6",
            unselected_hover_color="#E5E7EB",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
            command=self._on_type_change,
        )
        self.type_selector.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 16)
        )

        ctk.CTkLabel(
            card,
            text="Merchant / Description",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=2, column=0, sticky="w", padx=(24, 12), pady=(0, 6))

        self.merchant_entry = ctk.CTkEntry(
            card,
            placeholder_text="e.g., Acme Studio, Coffee Shop",
            height=38,
            corner_radius=8,
            border_color=self.palette["BORDER_COLOR"],
            fg_color=self.palette["BG_CANVAS"],
            text_color=self.palette["TEXT_PRIMARY"],
        )
        self.merchant_entry.grid(
            row=3, column=0, sticky="ew", padx=(24, 12), pady=(0, 16)
        )

        ctk.CTkLabel(
            card,
            text="Amount (MMK)",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=2, column=1, sticky="w", padx=(12, 24), pady=(0, 6))

        self.amount_entry = ctk.CTkEntry(
            card,
            placeholder_text="0.00",
            height=38,
            corner_radius=8,
            border_color=self.palette["BORDER_COLOR"],
            fg_color=self.palette["BG_CANVAS"],
            text_color=self.palette["TEXT_PRIMARY"],
        )
        self.amount_entry.grid(
            row=3, column=1, sticky="ew", padx=(12, 24), pady=(0, 16)
        )
        self._attach_numeric_guard(self.amount_entry)

        ctk.CTkLabel(
            card,
            text="Category",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=24, pady=(0, 6))

        self.category_menu = ctk.CTkOptionMenu(
            card,
            values=EXPENSE_CATEGORIES,
            height=38,
            corner_radius=8,
            fg_color=self.palette["BG_CANVAS"],
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            text_color=self.palette["TEXT_PRIMARY"],
        )
        self.category_menu.grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 24)
        )

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=6, column=0, columnspan=2, sticky="e", padx=24, pady=(0, 22))

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
            command=lambda: Application.switch_view("transactions"),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text="Save Transaction",
            width=140,
            height=36,
            corner_radius=8,
            fg_color=self.palette["ACCENT_ORANGE"],
            hover_color="#D9532B",
            font=("", 12, "bold"),
            command=self._handle_save,
        ).pack(side="left")

    def _on_type_change(self, selected_type):
        """Update available categories based on whether Expense or Income is chosen."""
        categories = (
            INCOME_CATEGORIES
            if selected_type == "Income"
            else EXPENSE_CATEGORIES
        )
        self.category_menu.configure(values=categories)
        self.category_menu.set(categories[0])

    def _parse_amount(self) -> float | None:
        """Return a positive numeric amount or None if blank or invalid."""
        raw = self.amount_entry.get().strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        if not math.isfinite(value) or value <= 0:
            return None
        return int(value) if value.is_integer() else value

    def _show_warning(self, message: str):
        """Display a themed warning dialog."""
        CTkMessagebox(
            title="Missing details",
            message=message,
            icon="warning",
            fg_color=self.palette["BG_CARD"],
            bg_color=self.palette["BG_CANVAS"],
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            text_color=self.palette["TEXT_PRIMARY"],
            button_color=self.palette["ACCENT_ORANGE"],
            button_hover_color="#D9532B",
            button_text_color="#FFFFFF",
            title_color=self.palette["TEXT_PRIMARY"],
        )

    def _clear_form(self):
        """Reset form inputs after saving a transaction."""
        self.merchant_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.type_var.set("Expense")
        self._on_type_change("Expense")

    def _on_submit(self, data):
        """Persist valid transaction records or show a validation dialog."""
        text_fields = {k: v for k, v in data.items() if isinstance(v, str)}
        if has_non_empty_string_values(text_fields) and data["amount"] is not None:
            storage.add_transaction(data)
            Application.load_transactions()
            self._clear_form()
            Application.switch_view("transactions")
        else:
            self._show_warning("Please enter a valid merchant and amount greater than 0.")

    def _handle_save(self):
        """Collect UI inputs into the target dictionary structure and trigger submit."""
        payload = {
            "id": get_next_tx_id(Application.transactions),
            "merchant": self.merchant_entry.get().strip(),
            "category": self.category_menu.get(),
            "date": get_current_date_yy_mm_dd(),
            "amount": self._parse_amount(),
            "type": self.type_var.get().lower(),
        }
        self._on_submit(payload)


class Transactions(View):
    """Transactions list view with summary cards, filters, and table."""

    def __init__(self, parent, palette=Application.PALETTE):
        """Initialize the transactions view."""
        super().__init__(parent, fg_color="transparent")
        self.palette = palette

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_summary_cards()
        self._build_filter_bar()
        self._build_transactions_table_card()
        self.refresh_transactions() #TODO: Need to figure how to build the view

    def refresh(self):
        self._build_header()
        self._build_summary_cards()
        self._build_filter_bar()
        self._build_transactions_table_card()

    def _build_header(self):
        """Render the workspace label, title, subtitle, and add transaction CTA."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="PERSONAL WORKSPACE",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Transactions",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 24, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            left,
            text="Every money move, in one place.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

        ctk.CTkButton(
            header,
            text="Add transaction",
            height=36,
            corner_radius=8,
            fg_color=self.palette["ACCENT_ORANGE"],
            hover_color="#D9532B",
            font=("", 12, "bold"),
            command=lambda: Application.switch_view("add_transaction"),
        ).grid(row=0, column=1, sticky="e")

    def _build_summary_cards(self):
        """Render Money in, Money out, and Net cash flow summary cards."""
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 12))
        row.grid_columnconfigure((0, 1, 2), weight=1, uniform="tx_kpi")

        cards = [
            ("Money in", f"{logic.calculate_total_income(Application.transactions)} MMK", "", False),
            ("Money out", f"{logic.calculate_total_expenses(Application.transactions)} MMK", "", False),
            ("Net cash flow", f"{logic.calculate_net_cash_flow(Application.transactions)} MMK", "", True),
        ]

        for col, (title, value, sub, is_dark) in enumerate(cards):
            card = self._make_card(row, dark=is_dark, height=120)
            card.grid(row=0, column=col, sticky="nsew", padx=6)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                text_color="#D1FAE5" if is_dark else self.palette["TEXT_MUTED"],
                font=("", 12),
            ).pack(anchor="w", padx=18, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=value,
                text_color="#FFFFFF" if is_dark else self.palette["TEXT_PRIMARY"],
                font=("", 22, "bold"),
            ).pack(anchor="w", padx=18)

            ctk.CTkLabel(
                card,
                text=sub,
                text_color="#A7F3D0" if is_dark else "#15803D",
                font=("", 11),
            ).pack(anchor="w", padx=18, pady=(6, 0))

    def _build_filter_bar(self):
        """Render search and dropdown filters."""
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", padx=28, pady=(4, 12))
        bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            bar,
            placeholder_text="Search by name, category, or note",
            height=36,
            corner_radius=8,
            fg_color=self.palette["BG_CARD"],
            border_color=self.palette["BORDER_COLOR"],
            text_color=self.palette["TEXT_PRIMARY"],
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda _e: self.refresh_transactions())

        self.type_filter = ctk.CTkOptionMenu(
            bar,
            values=["All types", "Income", "Expense"],
            width=130,
            height=36,
            corner_radius=8,
            fg_color=self.palette["BG_CARD"],
            button_color=self.palette["BG_CARD"],
            button_hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
            command=lambda _v: self._on_type_filter_change(_v),
        )
        self.type_filter.grid(row=0, column=1, padx=(0, 10))

        self.category_filter = ctk.CTkOptionMenu(
            bar,
            values=[
                "All categories"]+INCOME_CATEGORIES+EXPENSE_CATEGORIES,
            width=165,
            height=36,
            corner_radius=8,
            fg_color=self.palette["BG_CARD"],
            button_color=self.palette["BG_CARD"],
            button_hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
            command=lambda _v: self._on_category_filter_change(_v),
        )
        self.category_filter.grid(row=0, column=2, padx=(0, 10))

        months = get_month_year(Application.transactions)

        self.month_filter = ctk.CTkOptionMenu(
            bar,
            values=months + ["October 2026"] if months else [get_current_month_year()],
            width=155,
            height=36,
            corner_radius=8,
            fg_color=self.palette["BG_CARD"],
            button_color=self.palette["BG_CARD"],
            button_hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
            command=lambda _v: self.refresh_transactions(),
        )
        self.month_filter.grid(row=0, column=3)

    def _get_categories_for_type(self, selected_type: str) -> list[str]:
        """Return category filter values matching the chosen transaction type."""
        normalized = selected_type.strip().lower()
        if normalized == "income":
            return ["All categories", *INCOME_CATEGORIES]
        if normalized == "expense":
            return ["All categories", *EXPENSE_CATEGORIES]

        # When "All types" is selected, merge both lists without duplicates
        combined = list(dict.fromkeys([*EXPENSE_CATEGORIES, *INCOME_CATEGORIES]))
        return ["All categories", *combined]

    def _on_type_filter_change(self, selected_type: str):
        """Update category dropdown choices dynamically and refresh rows."""
        previous_category = self.category_filter.get()
        updated_values = self._get_categories_for_type(selected_type)

        self.category_filter.configure(values=updated_values)
        if previous_category in updated_values:
            self.category_filter.set(previous_category)
        else:
            self.category_filter.set("All categories")

        self.refresh_transactions()

    def _on_category_filter_change(self, _selected_category: str):
        """Refresh filtered rows when a category option is chosen."""
        self.refresh_transactions()

    def _build_transactions_table_card(self):
        """Render the All transactions card with column headers and rows."""
        card = self._make_card(self)
        card.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 24))
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        top.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="All transactions",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w")

        self.count_label = ctk.CTkLabel(
            left,
            text="0 transactions this month",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 11),
        )
        self.count_label.pack(anchor="w")

        self.sort_order = "newest"
        self.sort_btn = ctk.CTkButton(
            top,
            text="Newest first ↓",
            width=110,
            height=28,
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 11),
            command=self._toggle_sort,
        )
        self.sort_btn.grid(row=0, column=1, sticky="e")

        self.rows_container = CTkXYFrame(
            card, fg_color="transparent", corner_radius=0
        )
        self.rows_container.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 12))
        self.rows_container.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(card, height=1, fg_color=self.palette["BORDER_COLOR"]).grid(
            row=1, column=0, sticky="sew", padx=16
        )

    def _confirm_delete(self, tx: dict):
        """Ask for confirmation before deleting a transaction."""
        merchant = str(tx.get("merchant", "this transaction"))
        amount_text = f"{float(tx.get('amount', 0)):,.2f} MMK"

        msg = CTkMessagebox(
            title="Delete transaction",
            message=f"Are you sure you want to delete '{merchant}' ({amount_text})?",
            icon="question",
            option_1="No",
            option_2="Yes",
            fg_color=self.palette["BG_CARD"],
            bg_color=self.palette["BG_CANVAS"],
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            text_color=self.palette["TEXT_PRIMARY"],
            button_color=self.palette["ACCENT_ORANGE"],
            button_hover_color="#D9532B",
            button_text_color="#FFFFFF",
            title_color=self.palette["TEXT_PRIMARY"],
        )

        if msg.get() == "Yes":
            tx_id = tx.get("id")
            if tx_id is not None:
                storage.delete_transaction(tx_id)
                if hasattr(Application, "load_transactions"):
                    Application.load_transactions()
                self.refresh_transactions()

    def _toggle_sort(self):
        """Switch between newest-first and oldest-first sorting."""
        self.sort_order = "oldest" if self.sort_order == "newest" else "newest"
        self.sort_btn.configure(
            text="Oldest first ↑" if self.sort_order == "oldest" else "Newest first ↓"
        )
        self.refresh_transactions()

    def refresh_transactions(self):
        """Filter cached transactions in memory and render matching rows."""
        for widget in self.rows_container.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip().lower()
        selected_type = self.type_filter.get().lower()
        selected_category = self.category_filter.get()
        selected_month = self.month_filter.get()

        filtered = []
        for tx in logic.filter_transactions_by_month(Application.transactions,str_to_int_year_month(selected_month)):
            merchant = str(tx.get("merchant", ""))
            category = str(tx.get("category", ""))
            tx_type = str(tx.get("type", "expense")).lower()

            if selected_type != "all types" and tx_type != selected_type:
                continue
            if selected_category != "All categories" and category != selected_category:
                continue
            if query and query not in merchant.lower() and query not in category.lower():
                continue
            filtered.append(tx)

        if self.sort_order == "newest":
            filtered = list(reversed(filtered))

        self.count_label.configure(text=f"{len(filtered)} transactions")

        for row_idx, tx in enumerate(filtered):
            self._render_transaction_row(self.rows_container,row_idx, tx)

class Budgets(View):
    """Budgets view displaying monthly budget usage, remaining balance, and category cards."""

    def __init__(self, parent, palette=Application.PALETTE):
        """Initialize the budgets view."""
        super().__init__(parent, fg_color="transparent")
        self.palette = palette

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.refresh()



    def _build_header(self):
        """Render the workspace label, title, subtitle, and edit budget CTA."""
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="PERSONAL WORKSPACE",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Budgets",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 24, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            left,
            text="A plan for today. More room for tomorrow.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

        ctk.CTkButton(
            header,
            text="Edit monthly budget",
            height=36,
            corner_radius=8,
            fg_color=self.palette["ACCENT_ORANGE"],
            hover_color="#D9532B",
            font=("", 12, "bold"),
            command=lambda: Application.switch_view("edit_budgets"),
        ).grid(row=0, column=1, sticky="e")

    def _build_top_summary_row(self, total_spent, monthly_budget, left_to_spend, used_pct):
        """Render the dark monthly budget card and right-side remaining card."""
        row = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))
        row.grid_columnconfigure(0, weight=2, uniform="budget_top")
        row.grid_columnconfigure(1, weight=1, uniform="budget_top")

        dark_card = self._make_card(row, dark=True, height=175)
        dark_card.grid(row=0, column=0, sticky="nsew", padx=6)
        dark_card.grid_propagate(False)
        dark_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            dark_card,
            text=get_current_upper_month_and_date(),
            text_color="#A7F3D0",
            font=("", 10, "bold"),
        ).pack(anchor="w", padx=22, pady=(18, 6))

        amount_line = ctk.CTkFrame(dark_card, fg_color="transparent")
        amount_line.pack(fill="x", padx=22)

        ctk.CTkLabel(
            amount_line,
            text=total_spent,
            text_color="#FFFFFF",
            font=("", 24, "bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            amount_line,
            text=f"  spent of {monthly_budget} budget",
            text_color="#D1FAE5",
            font=("", 12),
        ).pack(side="left", pady=(6, 0))

        ctk.CTkLabel(
            amount_line,
            text=f"{round(used_pct)}% used",
            text_color="#D1FAE5",
            font=("", 11, "bold"),
        ).pack(side="right", pady=(6, 0))

        progress = ctk.CTkProgressBar(
            dark_card,
            height=8,
            corner_radius=4,
            fg_color="#3A5243",
            progress_color="#D9F99D",
        )
        progress.set(min(max(used_pct / 100, 0.0), 1.0))
        progress.pack(fill="x", padx=22, pady=(14, 14))

        footer_line = ctk.CTkFrame(dark_card, fg_color="transparent")
        footer_line.pack(fill="x", padx=22)

        ctk.CTkLabel(
            footer_line,
            text="A little intention goes a long way.",
            text_color="#D1FAE5",
            font=("", 11),
        ).pack(side="left")

        ctk.CTkLabel(
            footer_line,
            text="5 days left this month",
            text_color="#D1FAE5",
            font=("", 11),
        ).pack(side="right")

        right_card = self._make_card(row, dark=False, height=175)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        right_card.grid_propagate(False)

        ctk.CTkLabel(
            right_card,
            text="Left to spend",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            right_card,
            text=left_to_spend,
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 24, "bold"),
        ).pack(anchor="w", padx=20)

        daily_pace = left_to_spend / 5 if left_to_spend > 0 else 0
        ctk.CTkLabel(
            right_card,
            text=f"That's {daily_pace} a day for the rest of November.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 11),
        ).pack(anchor="w", padx=20, pady=(4, 0))

        on_track = left_to_spend >= 0
        badge = ctk.CTkLabel(
            right_card,
            text="On track" if on_track else "Over budget",
            corner_radius=6,
            fg_color="#DCFCE7" if on_track else "#FEE2E2",
            text_color="#15803D" if on_track else "#DC2626",
            font=("", 11, "bold"),
            padx=10,
            pady=3,
        )
        badge.pack(anchor="w", padx=20)

    def _build_category_budgets_section(self, spent_by_cat, cat_limits):
        """Render the category budget cards grid and flexibility helper card."""
        section_header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        section_header.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 10))
        section_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            section_header,
            text="Your category budgets",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            section_header,
            text=f"{len(BUDGET_CATEGORIES)} categories",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 11),
        ).grid(row=0, column=1, sticky="e")

        grid_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid_frame.grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 14))
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="budget_grid")

        next_idx = 0
        for idx, (category, subtitle) in enumerate(BUDGET_CATEGORIES.items()):
            r, c = divmod(idx, 3)
            spent = spent_by_cat.get(category, 0)
            limit = cat_limits.get(category, 0)
            card = self._create_category_card(grid_frame, category, spent, limit, subtitle)
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            next_idx = idx+1

        flex_r,flex_c = divmod(next_idx,3)
        flex_card = self._create_flexibility_card(grid_frame)
        flex_card.grid(row=flex_r, column=flex_c, sticky="nsew", padx=6, pady=6)

    def _create_category_card(self, parent, category, spent, limit, subtitle):
        
        """Build a single category budget card with progress bar and variance."""
        card = self._make_card(parent, dark=False, height=185)
        card.grid_propagate(False)
        card.grid_columnconfigure(0,weight=1)

        pct = (spent / limit * 100) if limit > 0 else 0
        is_over = spent > limit
        pct_rounded = round(pct)
        bar_color = self.palette["ACCENT_ORANGE"] if is_over else "#2D5A3C"
        status_color = "#DC2626" if is_over else "#15803D"
        status_text = (
            f"{spent - limit:,} MMK over budget"
            if is_over
            else f"{limit - spent:,} MMK left"
        )

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            top_row,
            text=category,
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 13, "bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            top_row,
            text="•••",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12, "bold"),
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=f"{spent:,} MMK",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 20, "bold"),
        ).pack(anchor="w", padx=18)

        meta_row = ctk.CTkFrame(card, fg_color="transparent")
        meta_row.pack(fill="x", padx=18, pady=(0, 8))

        ctk.CTkLabel(
            meta_row,
            text=f"of {limit:,} MMK",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 11),
        ).pack(side="left")

        ctk.CTkLabel(
            meta_row,
            text=f"{pct_rounded}%",
            text_color=status_color if is_over else self.palette["TEXT_MUTED"],
            font=("", 11, "bold"),
        ).pack(side="right")

        bar = ctk.CTkProgressBar(
            card,
            height=6,
            corner_radius=3,
            fg_color="#E5E7EB",
            progress_color=bar_color,
        )
        bar.set(min(max(pct / 100, 0.0), 1.0))
        bar.pack(fill="x", padx=18, pady=(0, 8))

        ctk.CTkLabel(
            card,
            text=status_text,
            text_color=status_color,
            font=("", 11, "bold"),
        ).pack(anchor="w", padx=18)

        ctk.CTkLabel(
            card,
            text=subtitle,
            text_color=self.palette["TEXT_MUTED"],
            font=("", 10),
        ).pack(anchor="w", padx=18, pady=(2, 0))

        return card

    def _create_flexibility_card(self, parent) -> ctk.CTkFrame:
        """Build the helper card suggesting category limit adjustments."""
        card = ctk.CTkFrame(
            parent,
            fg_color="#EEF2EA",
            corner_radius=14,
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            height=165,
        )
        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text="A little flexibility helps.",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 14, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            card,
            text="Shopping is slightly over budget, while other categories still have room.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 11),
            wraplength=240,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        ctk.CTkButton(
            card,
            text="Adjust category limits →",
            height=32,
            corner_radius=8,
            fg_color=self.palette["BG_CARD"],
            hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            font=("", 11, "bold"),
            command=lambda: Application.switch_view("edit_budgets"),
        ).pack(anchor="w", padx=18)

        return card

    def _build_rhythm_banner(self):
        """Render the bottom summary card with monthly pacing notes."""
        banner = self._make_card(self.scroll_container, dark=False)
        banner.grid(row=4, column=0, sticky="ew", padx=28, pady=(0, 24))

        ctk.CTkLabel(
            banner,
            text="Your budget, your rhythm.",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 14, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            banner,
            text="Keep making room for the things that matter.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w", padx=20)

        ctk.CTkLabel(
            banner,
            text="Monthly budget resets on December 1",
            text_color="#15803D",
            font=("", 11, "bold"),
        ).pack(anchor="w", padx=20, pady=(8, 16))

    def _load_budget_data(self) -> tuple[float, dict[str, float]]:
        """Fetch monthly budget and category limits from storage, defaulting to 0."""
        getter = getattr(storage, "get_budget", None) or getattr(storage, "get_budgets", None)
        if not callable(getter):
            return 0, {cat: 0 for cat in BUDGET_CATEGORIES}

        data = getter() or {}
        if not isinstance(data, dict):
            return 0, {cat: 0 for cat in BUDGET_CATEGORIES}

        monthly_limit = data.get("monthly_budget", 0) or 0
        raw_cats = data.get("categories", {})
        cat_dict = raw_cats if isinstance(raw_cats, dict) else {}

        limits = {
            cat: cat_dict.get(cat, 0) or 0
            for cat in BUDGET_CATEGORIES
        }
        return monthly_limit, limits

    def refresh(self):
        """Rebuild all budget cards from storage and cached transactions."""
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        monthly_budget, cat_limits = self._load_budget_data()
        txs = getattr(Application, "transactions", []) or []

        spent_by_cat = {cat: 0 for cat in BUDGET_CATEGORIES}
        total_spent = 0

        for tx in txs:
            if str(tx.get("type", "")).lower() == "expense":
                amt = tx.get("amount", 0) or 0
                total_spent += amt
                cat = str(tx.get("category", "Other"))
                if cat in spent_by_cat:
                    spent_by_cat[cat] += amt

        left_to_spend = monthly_budget - total_spent
        used_pct = (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0

        self._build_header()
        self._build_top_summary_row(total_spent, monthly_budget, left_to_spend, used_pct)
        self._build_category_budgets_section(spent_by_cat, cat_limits)
        self._build_rhythm_banner()

class EditBudgets(View):
    """View for editing the overall monthly budget and per-category limits."""

    DEFAULT_CATEGORIES = [
        "Housing",
        "Food & dining",
        "Shopping",
        "Transport",
        "Other",
    ]

    def __init__(self, parent, palette=Application.PALETTE):
        """Initialize the edit budget view."""
        super().__init__(parent, fg_color="transparent")
        self.palette = palette
        self.category_entries: dict[str, ctk.CTkEntry] = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)
        self.refresh()


    def refresh(self):
        self._build_header()
        self._build_form_card()
        self.load_values()

    def _build_header(self):
        """Render the back button, title, and subtitle."""
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))

        ctk.CTkButton(
            header,
            text="← Back to Budgets",
            width=145,
            height=30,
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color=self.palette["TEXT_MUTED"],
            anchor="w",
            font=("", 12, "bold"),
            command=lambda: Application.switch_view("budgets"),
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="BUDGETS SETTINGS",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Edit budget limits",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 24, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            header,
            text="Set your overall monthly budget and category spending caps in MMK.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

    def _build_form_card(self):
        """Render inputs for monthly budget, optional initial balance, and categories."""
        card = self._make_card(self.scroll_container, dark=False)
        card.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 24))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card,
            text="Overall Monthly Budget (MMK)",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(24, 12), pady=(22, 6))

        ctk.CTkLabel(
            card,
            text="Starting Balance (MMK)",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=(12, 24), pady=(22, 6))

        self.monthly_budget_entry = ctk.CTkEntry(
            card,
            placeholder_text="4000",
            height=38,
            corner_radius=8,
            border_color=self.palette["BORDER_COLOR"],
            fg_color=self.palette["BG_CANVAS"],
            text_color=self.palette["TEXT_PRIMARY"],
        )
        self.monthly_budget_entry.grid(
            row=1, column=0, sticky="ew", padx=(24, 12), pady=(0, 20)
        )
        self._attach_numeric_guard(self.monthly_budget_entry)

        self.initial_balance_entry = ctk.CTkEntry(
            card,
            placeholder_text="0",
            height=38,
            corner_radius=8,
            border_color=self.palette["BORDER_COLOR"],
            fg_color=self.palette["BG_CANVAS"],
            text_color=self.palette["TEXT_PRIMARY"],
        )
        self.initial_balance_entry.grid(
            row=1, column=1, sticky="ew", padx=(12, 24), pady=(0, 20)
        )
        self._attach_numeric_guard(self.initial_balance_entry)

        ctk.CTkFrame(card, height=1, fg_color=self.palette["BORDER_COLOR"]).grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=24, pady=(0, 16)
        )

        ctk.CTkLabel(
            card,
            text="Category Limits (MMK)",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 13, "bold"),
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=24, pady=(0, 10))

        for idx, category in enumerate(self.DEFAULT_CATEGORIES):
            row_idx = 4 + idx
            ctk.CTkLabel(
                card,
                text=category,
                text_color=self.palette["TEXT_PRIMARY"],
                font=("", 12, "bold"),
            ).grid(row=row_idx, column=0, sticky="w", padx=(24, 12), pady=6)

            entry = ctk.CTkEntry(
                card,
                placeholder_text="0",
                height=36,
                corner_radius=8,
                border_color=self.palette["BORDER_COLOR"],
                fg_color=self.palette["BG_CANVAS"],
                text_color=self.palette["TEXT_PRIMARY"],
            )
            entry.grid(row=row_idx, column=1, sticky="ew", padx=(12, 24), pady=6)
            self._attach_numeric_guard(entry)
            self.category_entries[category] = entry

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(
            row=4 + len(self.DEFAULT_CATEGORIES),
            column=0,
            columnspan=2,
            sticky="e",
            padx=24,
            pady=(18, 22),
        )

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 12, "bold"),
            command=lambda: Application.switch_view("budgets"),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text="Save Budgets",
            width=135,
            height=36,
            corner_radius=8,
            fg_color=self.palette["ACCENT_ORANGE"],
            hover_color="#D9532B",
            font=("", 12, "bold"),
            command=self._handle_save,
        ).pack(side="left")

    def _format_num(self, val: float) -> str:
        """Format numbers cleanly without trailing .0 when whole."""
        return str(int(val)) if float(val).is_integer() else str(round(float(val), 2))

    def load_values(self):
        """Populate form fields from storage if available."""
        if not hasattr(storage, "get_budgets"):
            return
        data = storage.get_budgets() or {}

        monthly = data.get("monthly_budget", 0)
        self.monthly_budget_entry.delete(0, "end")
        self.monthly_budget_entry.insert(0, self._format_num(monthly))

        balance = data.get("initial_balance", 0)
        self.initial_balance_entry.delete(0, "end")
        self.initial_balance_entry.insert(0, self._format_num(balance))

        cats = data.get("categories", {}) if isinstance(data.get("categories"), dict) else {}
        for name, entry in self.category_entries.items():
            entry.delete(0, "end")
            entry.insert(0, self._format_num(cats.get(name, 0)))

    def _parse_non_negative(self, entry: ctk.CTkEntry) -> float | None:
        """Return a finite number >= 0, or None if invalid/empty."""
        raw = entry.get().strip()
        if not raw:
            return None
        try:
            val = float(raw)
        except ValueError:
            return None
        if val < 0:
            return None
        return int(val) if val.is_integer() else round(val, 2)

    def _show_warning(self, message: str):
        """Display a themed warning dialog."""
        CTkMessagebox(
            title="Invalid budget value",
            message=message,
            icon="warning",
            fg_color=self.palette["BG_CARD"],
            bg_color=self.palette["BG_CANVAS"],
            border_width=1,
            border_color=self.palette["BORDER_COLOR"],
            text_color=self.palette["TEXT_PRIMARY"],
            button_color=self.palette["ACCENT_ORANGE"],
            button_hover_color="#D9532B",
            button_text_color="#FFFFFF",
            title_color=self.palette["TEXT_PRIMARY"],
        )

    def _handle_save(self):
        """Validate inputs, persist budgets to storage, and return to Budgets."""
        monthly_budget = self._parse_non_negative(self.monthly_budget_entry)
        initial_balance = self._parse_non_negative(self.initial_balance_entry)

        if monthly_budget is None or initial_balance is None:
            self._show_warning("Please enter valid numbers (0 or greater) for budget and balance.")
            return

        categories_payload = {}
        for name, entry in self.category_entries.items():
            parsed = self._parse_non_negative(entry)
            if parsed is None:
                self._show_warning(f"Please enter a valid limit for '{name}'.")
                return
            categories_payload[name] = parsed

        payload = {
            "monthly_budget": monthly_budget,
            "initial_balance": initial_balance,
            "categories": categories_payload,
        }

        if hasattr(storage, "save_budgets"):
            storage.save_budgets(payload)

        Application.switch_view("budgets")


if __name__ == "__main__":
    Application().mainloop()