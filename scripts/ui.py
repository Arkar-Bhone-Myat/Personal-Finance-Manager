import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import *
from tkinter import ttk
import sys
import storage
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

    def __init__(self):
        """Initialize the main window, sidebar, and switchable views."""
        super().__init__()
        self.title("Penny - Personal Finance Dashboard")
        self.geometry("1380x880")
        self.minsize(960, 680)
        self.configure(fg_color=self.PALETTE["BG_CANVAS"])

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_area()

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

        profile_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        profile_box.pack(side="bottom", fill="x", padx=18, pady=(8, 18))

        ctk.CTkLabel(
            profile_box,
            text="Steve",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 13, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            profile_box,
            text="Personal workspace",
            text_color=self.PALETTE["TEXT_MUTED"],
            font=("", 11),
        ).pack(anchor="w")

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

        self._select_nav("Overview")

    def _select_nav(self, active_name):
        """Highlight active sidebar button and restore dashboard view."""
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

        if hasattr(self, "dashboard"):
            self._show_dashboard()

    def _build_main_area(self):
        """Build Main Area container and initialize switchable frames."""
        self.main_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.main_wrapper.grid(row=0, column=1, sticky="nsew")
        self.main_wrapper.grid_rowconfigure(0, weight=1)
        self.main_wrapper.grid_columnconfigure(0, weight=1)

        # Overview Dashboard Frame
        self.dashboard = ctk.CTkFrame(self.main_wrapper, fg_color="transparent")
        self.dashboard.grid_propagate(False)
        self.dashboard.grid_rowconfigure(0, weight=0)
        self.dashboard.grid_rowconfigure(1, weight=0)
        self.dashboard.grid_rowconfigure(2, weight=3)
        self.dashboard.grid_rowconfigure(3, weight=3)
        self.dashboard.grid_columnconfigure(0, weight=1)

        self._build_header_row()
        self._build_kpi_row()
        self._build_middle_row()
        self._build_bottom_row()

        # Add Transaction Form Frame
        self.add_tx_view = TransactionView(
            self.main_wrapper,
            palette=self.PALETTE,
            on_cancel=self._show_dashboard,
            on_submit=self._on_transaction_submitted,
        )
        self.add_tx_view.grid_propagate(False)

        self._show_dashboard()
        self.main_wrapper.bind("<Configure>", self._enforce_max_width)

    def _show_dashboard(self):
        """Display the main overview dashboard and hide the form view."""
        self.add_tx_view.grid_forget()
        self.dashboard.grid(row=0, column=0, sticky="ns")

    def _show_add_transaction(self):
        """Display the Add Transaction frame and hide the overview dashboard."""
        self.dashboard.grid_forget()
        self.add_tx_view.grid(row=0, column=0, sticky="ns")

    def _on_transaction_submitted(self, data):
        if has_non_empty_string_values(data):
            storage.add_transaction(data)
            self._show_dashboard()
        else:
            CTkMessagebox(
                title="Missing details",
                message="Please fill in all fields before saving.",
                icon="warning",
                fg_color=self.PALETTE["BG_CARD"],
                bg_color=self.PALETTE["BG_CANVAS"],
                border_width=1,
                border_color=self.PALETTE["BORDER_COLOR"],
                text_color=self.PALETTE["TEXT_PRIMARY"],
                button_color=self.PALETTE["ACCENT_ORANGE"],
                button_hover_color="#D9532B",
                button_text_color="#FFFFFF",
                title_color=self.PALETTE["TEXT_PRIMARY"],
            ).show()

    def _enforce_max_width(self, event):
        """Constrain active view width to MAX_MAIN_WIDTH while matching height."""
        target_w = max(min(event.width, self.MAX_MAIN_WIDTH), 1)
        target_h = max(event.height, 1)
        self.dashboard.configure(width=target_w, height=target_h)
        self.add_tx_view.configure(width=target_w, height=target_h)

    def _build_header_row(self):
        header = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="YOUR MONEY, AT A GLANCE",
            text_color=self.PALETTE["TEXT_MUTED"],
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="A little clarity. A lot of possibility.",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 22, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            left,
            text="Welcome back, Steve. Let's make your money work for you.",
            text_color=self.PALETTE["TEXT_MUTED"],
            font=("", 12),
        ).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="se")

        ctk.CTkOptionMenu(
            right,
            values=["November 2026", "October 2026", "September 2026"],
            width=150,
            height=34,
            fg_color=self.PALETTE["BG_CARD"],
            button_color=self.PALETTE["BG_CARD"],
            button_hover_color="#F3F4F6",
            text_color=self.PALETTE["TEXT_PRIMARY"],
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            right,
            text="+ Add transaction",
            height=34,
            corner_radius=8,
            fg_color=self.PALETTE["ACCENT_ORANGE"],
            hover_color="#D9532B",
            font=("", 12, "bold"),
            command=self._show_add_transaction,
        ).pack(side="left")

    def _build_kpi_row(self):
        kpi_row = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))

        cards = [
            ("Total balance", "24,680.00 MMK", True),
            ("Income", "8,450.00 MMK", False),
            ("Expenses", "3,280.00 MMK", False),
            ("Net savings", "5,170.00 MMK", False),
        ]

        for col, (title, value, is_dark) in enumerate(cards):
            kpi_row.grid_columnconfigure(col, weight=1, uniform="kpi")
            card = self._make_card(kpi_row, dark=is_dark, height=115)
            card.grid(row=0, column=col, sticky="nsew", padx=6)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                text_color="#D1FAE5" if is_dark else self.PALETTE["TEXT_MUTED"],
                font=("", 12),
            ).pack(anchor="w", padx=18, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=value,
                text_color="#FFFFFF" if is_dark else self.PALETTE["TEXT_PRIMARY"],
                font=("", 22, "bold"),
            ).pack(anchor="w", padx=18)

    def _build_middle_row(self):
        mid = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        mid.grid(row=2, column=0, sticky="nsew", padx=22, pady=8)
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=2, uniform="split")
        mid.grid_columnconfigure(1, weight=1, uniform="split")

        left_card = self._make_card(mid)
        left_card.grid(row=0, column=0, sticky="nsew", padx=6)
        ctk.CTkLabel(
            left_card,
            text="Cash flow",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            left_card,
            text="[Bar Chart Area — 2/3 width]",
            text_color=self.PALETTE["TEXT_MUTED"],
        ).pack(expand=True)

        right_card = self._make_card(mid)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="Where it goes",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            right_card,
            text="[Donut Breakdown — 1/3 width]",
            text_color=self.PALETTE["TEXT_MUTED"],
        ).pack(expand=True)

    def _build_bottom_row(self):
        bot = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        bot.grid(row=3, column=0, sticky="nsew", padx=22, pady=(8, 22))
        bot.grid_rowconfigure(0, weight=1)
        bot.grid_columnconfigure(0, weight=2, uniform="split")
        bot.grid_columnconfigure(1, weight=1, uniform="split")

        left_card = self._make_card(bot)
        left_card.grid(row=0, column=0, sticky="nsew", padx=6)
        ctk.CTkLabel(
            left_card,
            text="Recent transactions",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            left_card,
            text="[Transactions List — 2/3 width]",
            text_color=self.PALETTE["TEXT_MUTED"],
        ).pack(expand=True)

        right_card = self._make_card(bot)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="A little closer to your goals",
            text_color=self.PALETTE["TEXT_PRIMARY"],
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            right_card,
            text="[Progress Bars — 1/3 width]",
            text_color=self.PALETTE["TEXT_MUTED"],
        ).pack(expand=True)

    def _make_card(self, parent, dark=False, **kwargs):
        return ctk.CTkFrame(
            parent,
            fg_color=self.PALETTE["BG_DARK_CARD"] if dark else self.PALETTE["BG_CARD"],
            corner_radius=14,
            border_width=0 if dark else 1,
            border_color=self.PALETTE["BORDER_COLOR"],
            **kwargs,
        )

class TransactionView(ctk.CTkFrame):
    """UI form view for creating a new financial transaction."""

    def __init__(self, parent, palette, on_cancel, on_submit):
        """Initialize the transaction form frame.

        Args:
            parent: The parent container widget.
            palette: Dictionary containing the application's color tokens.
            on_cancel: Callback function triggered when cancelling or going back.
            on_submit: Callback function triggered when saving the transaction.
        """
        super().__init__(parent, fg_color="transparent")
        self.palette = palette
        self.on_cancel = on_cancel
        self.on_submit = on_submit

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
            command=self.on_cancel,
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

        # Transaction Type Segmented Control
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

        # Merchant Input
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

        # Amount Input
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

        # Category Dropdown
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
            "Other income"
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

        # Action Buttons
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
            command=self.on_cancel,
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

    def _handle_save(self):
        """Collect UI inputs into the target dictionary structure and trigger submit."""
        payload = {
            "id": get_next_tx_id(storage.get_transactions()),
            "merchant": self.merchant_entry.get().strip(),
            "category": self.category_menu.get(),
            "date": get_current_date_yy_mm_dd(),
            "amount": self.amount_entry.get().strip(),
            "type": self.type_var.get().lower(),
        }
        self.on_submit(payload)

    def _validate_numeric_keystroke(self, proposed_text: str) -> bool:
        """Allow empty string, digits, and at most one decimal point."""
        if proposed_text == "":
            return True
        if proposed_text.count(".") > 1:
            return False
        cleaned = proposed_text.replace(".", "", 1)
        return cleaned.isdigit()

    def _attach_numeric_guard(self,entry:ctk.CTkEntry):
        """Block non-numeric keystrokes while allowing decimal input and deletion."""
        vcmd = (self.register(self._validate_numeric_keystroke), "%P")
        entry.configure(validate="key", validatecommand=vcmd)

if __name__ == "__main__":
    Application().mainloop()