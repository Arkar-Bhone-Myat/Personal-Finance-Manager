import math
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
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
    _instance: "Application | None" = None
    transactions: list[dict] = []

    def __init__(self):
        """Initialize the main window, sidebar, and switchable views."""
        super().__init__()
        Application._instance = self
        self.title("Penny - Personal Finance Dashboard")
        self.geometry("1380x880")
        self.minsize(960, 680)
        self.configure(fg_color=self.PALETTE["BG_CANVAS"])

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
        nav_items = ["Overview", "Transactions"]

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

        for bottom_item in ["Help & support", "Settings"]:
            ctk.CTkButton(
                sidebar,
                text=f"   {bottom_item}",
                anchor="w",
                height=34,
                fg_color="transparent",
                hover_color="#F3F4F6",
                text_color=self.PALETTE["TEXT_MUTED"],
                font=("", 12),
            ).pack(side="bottom", fill="x", padx=14, pady=2)

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

        self.overview = Overview(self.main_wrapper)
        self.overview.grid_propagate(False)

        self.add_transition = AddTransaction(self.main_wrapper)
        self.add_transition.grid_propagate(False)

        self.transactions = Transactions(self.main_wrapper)
        self.transactions.grid_propagate(False)

        Application.views = {
            "overview": self.overview,
            "add_transaction": self.add_transition,
            "transactions": self.transactions,
        }

        self.main_wrapper.bind("<Configure>", self._enforce_max_width)

    def _sync_dimensions(self, width: int, height: int):
        """Apply width and height bounds to registered views."""
        target_w = max(min(width, self.MAX_MAIN_WIDTH), 1)
        target_h = max(height, 1)
        for view in self.views.values():
            view.configure(width=target_w, height=target_h)

    @classmethod
    def switch_view(cls, target_view: str):
        """Switch the main area to display the view with the given name and hide other views."""
        if target_view not in cls.views:
            return

        if target_view == "transactions":
            cls.views["transactions"].refresh_transactions()
        
        for view_name, frame in cls.views.items():
            if view_name != target_view:
                frame.grid_forget()
        target_frame = cls.views[target_view]
        target_frame.grid(row=0, column=0, sticky="nsew")

        if cls._instance is not None:
            wrapper = cls._instance.main_wrapper
            cls._instance._sync_dimensions(wrapper.winfo_width(), wrapper.winfo_height())
        

    @classmethod
    def _make_card(cls, parent, dark=False, **kwargs):
        """Create a styled card container matching the application palette."""
        return ctk.CTkFrame(
            parent,
            fg_color=cls.PALETTE["BG_DARK_CARD"] if dark else cls.PALETTE["BG_CARD"],
            corner_radius=14,
            border_width=0 if dark else 1,
            border_color=cls.PALETTE["BORDER_COLOR"],
            **kwargs,
        )

    @classmethod
    def load_transactions(cls):
        """Load transactions from storage into the memory cache."""
        cls.transactions = storage.get_transactions()

    def _enforce_max_width(self, event):
        """Constrain active view width to MAX_MAIN_WIDTH while matching height."""
        self._sync_dimensions(event.width, event.height)

class Overview(ctk.CTkFrame):
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
            text="Welcome back. Let's make your money work for you.",
            text_color=self.palette["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="se")

        ctk.CTkOptionMenu(
            right,
            values=["November 2026", "October 2026", "September 2026"],
            width=150,
            height=34,
            fg_color=self.palette["BG_CARD"],
            button_color=self.palette["BG_CARD"],
            button_hover_color="#F3F4F6",
            text_color=self.palette["TEXT_PRIMARY"],
        ).pack(side="left", padx=(0, 10))


    def _build_kpi_row(self):
        """Render the four summary metric cards across the top row."""
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))

        cards = [
            ("Total balance", "24,680 MMK", True),
            ("Income", "8,450 MMK", False),
            ("Expenses", "3,280 MMK", False),
            ("Net savings", "5,170 MMK", False),
        ]

        for col, (title, value, is_dark) in enumerate(cards):
            kpi_row.grid_columnconfigure(col, weight=1, uniform="kpi")
            card = Application._make_card(kpi_row, dark=is_dark, height=115)
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

        left_card = Application._make_card(mid)
        left_card.grid(row=0, column=0, sticky="nsew", padx=6)
        ctk.CTkLabel(
            left_card,
            text="Cash flow",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            left_card,
            text="[Bar Chart Area — 2/3 width]",
            text_color=self.palette["TEXT_MUTED"],
        ).pack(expand=True)

        right_card = Application._make_card(mid)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="Where it goes",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            right_card,
            text="[Donut Breakdown — 1/3 width]",
            text_color=self.palette["TEXT_MUTED"],
        ).pack(expand=True)

    def _build_bottom_row(self):
        """Render the recent transactions list and savings goals cards."""
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=3, column=0, sticky="nsew", padx=22, pady=(8, 22))
        bot.grid_rowconfigure(0, weight=1)
        bot.grid_columnconfigure(0, weight=2, uniform="split")
        bot.grid_columnconfigure(1, weight=1, uniform="split")

        left_card = Application._make_card(bot)
        left_card.grid(row=0, column=0, sticky="nsew", padx=6)
        ctk.CTkLabel(
            left_card,
            text="Recent transactions",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            left_card,
            text="[Transactions List — 2/3 width]",
            text_color=self.palette["TEXT_MUTED"],
        ).pack(expand=True)

        right_card = Application._make_card(bot)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="A little closer to your goals",
            text_color=self.palette["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            right_card,
            text="[Progress Bars — 1/3 width]",
            text_color=self.palette["TEXT_MUTED"],
        ).pack(expand=True)

class AddTransaction(ctk.CTkFrame):
    """UI form view for creating a new financial transaction."""

    def __init__(self, parent, palette=Application.PALETTE):
        """Initialize the transaction form frame."""
        super().__init__(parent, fg_color="transparent")
        self.palette = palette

        self.grid_columnconfigure(0, weight=1)
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

        self.expense_categories = [
            "Housing",
            "Food and Dining",
            "Transportation",
            "Shopping",
            "Bills and Utilities",
            "Health and Wellness",
            "Entertainment and Subscriptions",
            "Travel",
            "Savings and goals",
            "Other",
        ]
        self.income_categories = [
            "Salary",
            "Freelance / Side Income",
            "Investments",
            "Gift / Refunds",
            "Other income",
        ]

        self.category_menu = ctk.CTkOptionMenu(
            card,
            values=self.expense_categories,
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
            self.income_categories
            if selected_type == "Income"
            else self.expense_categories
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

class Transactions(ctk.CTkFrame):
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
        self.refresh_transactions()

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
            ("Money in", "8,450 MMK", "+8.2% vs. last month", False),
            ("Money out", "3,280 MMK", "-4.1% vs. last month", False),
            ("Net cash flow", "5,170 MMK", "61.2% of your income saved", True),
        ]

        for col, (title, value, sub, is_dark) in enumerate(cards):
            card = Application._make_card(row, dark=is_dark, height=120)
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
                "All categories",
                "Housing",
                "Food and Dining",
                "Transportation",
                "Shopping",
                "Bills and Utilities",
                "Health and Wellness",
                "Entertainment and Subscriptions",
                "Travel",
                "Savings and goals",
                "Salary",
                "Freelance / Side Income",
                "Investments",
                "Gift / Refunds",
                "Other",
            ],
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

        self.month_filter = ctk.CTkOptionMenu(
            bar,
            values=["November 2026", "October 2026", "September 2026"],
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
        EXPENSE_CATEGORIES = [
            "Housing",
            "Food and Dining",
            "Transportation",
            "Shopping",
            "Bills and Utilities",
            "Health and Wellness",
            "Entertainment and Subscriptions",
            "Travel",
            "Savings and goals",
            "Other",
        ]
        INCOME_CATEGORIES = [
            "Salary",
            "Freelance / Side Income",
            "Investments",
            "Gift / Refunds",
            "Other income",
        ]
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
        card = Application._make_card(self)
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

        headers = ["Transaction", "Category", "Type", "Date", "Amount",""]
        col_widths = [240, 150, 100, 120, 130, 36]
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 6))

        for idx, (text, w) in enumerate(zip(headers, col_widths)):
            anchor = "e" if idx == len(headers) - 1 else "w"
            ctk.CTkLabel(
                header_row,
                text=text,
                width=w,
                anchor=anchor,
                text_color=self.palette["TEXT_MUTED"],
                font=("", 11, "bold"),
            ).grid(row=0, column=idx, sticky="ew" if idx == 0 else "")

        ctk.CTkFrame(card, height=1, fg_color=self.palette["BORDER_COLOR"]).grid(
            row=1, column=0, sticky="sew", padx=16
        )

        self.rows_container = ctk.CTkScrollableFrame(
            card, fg_color="transparent", corner_radius=0
        )
        self.rows_container.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 12))
        self.rows_container.grid_columnconfigure(0, weight=1)

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

        filtered = []
        for tx in Application.transactions:
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
            self._render_row(row_idx, tx)

    def _render_row(self, idx: int, tx: dict):
        """Render a single transaction row inside the scrollable table body."""
        row = ctk.CTkFrame(self.rows_container, fg_color="transparent")
        row.grid(row=idx * 2, column=0, sticky="ew", padx=6, pady=4)

        merchant = str(tx.get("merchant", "Untitled"))
        category = str(tx.get("category", "Other"))
        tx_type = str(tx.get("type", "expense")).capitalize()
        date_str = str(tx.get("date", ""))
        raw_amount = tx.get("amount", 0)

        try:
            amount_val = float(raw_amount)
        except (TypeError, ValueError):
            amount_val = 0.0

        is_income = tx_type.lower() == "income"
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
            text=tx_type,
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
            command=lambda record=tx: self._confirm_delete(record),
        )
        delete_btn.grid(row=0, column=5, padx=(8, 0), sticky="e")

        ctk.CTkFrame(
            self.rows_container, height=1, fg_color=self.palette["BORDER_COLOR"]
        ).grid(row=idx * 2 + 1, column=0, sticky="ew", padx=6)

if __name__ == "__main__":
    Application().mainloop()