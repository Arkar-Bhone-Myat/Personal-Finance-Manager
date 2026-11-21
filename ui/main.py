import customtkinter as ctk

ctk.set_appearance_mode("system")


class Application(ctk.CTk):
    SIDEBAR_WIDTH = 230
    MAX_MAIN_WIDTH = 1200

    # Palette
    BG_SIDEBAR = "#FFFFFF"
    BG_CANVAS = "#F8F9FA"
    BG_CARD = "#FFFFFF"
    BG_DARK_CARD = "#24372B"
    ACCENT_ORANGE = "#F0643B"
    ACCENT_ORANGE_LIGHT = "#FDECE6"
    BORDER_COLOR = "#E5E7EB"
    TEXT_PRIMARY = "#111827"
    TEXT_MUTED = "#6B7280"

    def __init__(self):
        super().__init__()
        self.title("Penny - Personal Finance Dashboard")
        self.geometry("1380x880")
        self.minsize(960, 680)
        self.configure(fg_color=self.BG_CANVAS)

        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) #fixed sidebar
        self.grid_columnconfigure(1, weight=1) #expandable main area

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        """Build Sidebar with brand, nav, and bottom profile/settings section."""
        sidebar = ctk.CTkFrame(
            self,
            width=self.SIDEBAR_WIDTH,
            fg_color=self.BG_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=self.BORDER_COLOR,
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Top Brand Header
        brand_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_row.pack(fill="x", padx=20, pady=(22, 20))

        logo = ctk.CTkLabel(
            brand_row,
            text="P",
            width=30,
            height=30,
            corner_radius=8,
            fg_color=self.ACCENT_ORANGE,
            text_color="white",
            font=("", 16, "bold"),
        )
        logo.pack(side="left")

        ctk.CTkLabel(
            brand_row,
            text="enny",
            text_color=self.TEXT_PRIMARY,
            font=("", 18, "bold"),
        ).pack(side="left", padx=0)

        ctk.CTkLabel(
            sidebar,
            text="WORKSPACE",
            text_color=self.TEXT_MUTED,
            font=("", 10, "bold"),
        ).pack(anchor="w", padx=22, pady=(4, 8))


        self.nav_buttons = {}
        nav_items = [
            "Overview",
            "Transitions"
        ]

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
            text_color=self.TEXT_PRIMARY,
            font=("", 13, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            profile_box,
            text="Personal workspace",
            text_color=self.TEXT_MUTED,
            font=("", 11),
        ).pack(anchor="w")

        ctk.CTkFrame(sidebar, height=1, fg_color=self.BORDER_COLOR).pack(
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
                text_color=self.TEXT_MUTED,
                font=("", 12),
            ).pack(side="bottom", fill="x", padx=14, pady=2)

        self._select_nav("Overview")

    def _select_nav(self, active_name):
        for name, btn in self.nav_buttons.items():
            if name == active_name:
                btn.configure(
                    fg_color=self.ACCENT_ORANGE_LIGHT,
                    hover_color=self.ACCENT_ORANGE_LIGHT,
                    text_color=self.ACCENT_ORANGE,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color="#F3F4F6",
                    text_color=self.TEXT_MUTED,
                )

    def _build_main_area(self):
        """Build Main Area with header, KPI row, middle charts, and bottom cards."""
        self.main_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.main_wrapper.grid(row=0, column=1, sticky="nsew")
        self.main_wrapper.grid_rowconfigure(0, weight=1)
        self.main_wrapper.grid_columnconfigure(0, weight=1)

        self.dashboard = ctk.CTkFrame(self.main_wrapper, fg_color="transparent")
        self.dashboard.grid(row=0, column=0, sticky="ns")
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

        self.main_wrapper.bind("<Configure>", self._enforce_max_width)

    def _enforce_max_width(self, event):
        target_w = min(event.width, self.MAX_MAIN_WIDTH)
        self.dashboard.configure(width=max(target_w, 1), height=max(event.height, 1))

    def _build_header_row(self):
        header = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left,
            text="YOUR MONEY, AT A GLANCE",
            text_color=self.TEXT_MUTED,
            font=("", 10, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="A little clarity. A lot of possibility.",
            text_color=self.TEXT_PRIMARY,
            font=("", 22, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            left,
            text="Welcome back, Steve. Let's make your money work for you.",
            text_color=self.TEXT_MUTED,
            font=("", 12),
        ).pack(anchor="w")

        # Right controls
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="se")

        ctk.CTkOptionMenu(
            right,
            values=["November 2026", "October 2026", "September 2026"],
            width=150,
            height=34,
            fg_color=self.BG_CARD,
            button_color=self.BG_CARD,
            button_hover_color="#F3F4F6",
            text_color=self.TEXT_PRIMARY,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            right,
            text="+ Add transaction",
            height=34,
            corner_radius=8,
            fg_color=self.ACCENT_ORANGE,
            hover_color="#D9532B",
            font=("", 12, "bold"),
        ).pack(side="left")

    def _build_kpi_row(self):
        kpi_row = ctk.CTkFrame(self.dashboard, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))

        cards = [
            ("Total balance", "$24,680.00", True),
            ("Income", "$8,450.00", False),
            ("Expenses", "$3,280.00", False),
            ("Net savings", "$5,170.00", False),
        ]

        for col, (title, value, is_dark) in enumerate(cards):
            kpi_row.grid_columnconfigure(col, weight=1, uniform="kpi")
            card = self._make_card(kpi_row, dark=is_dark, height=115)
            card.grid(row=0, column=col, sticky="nsew", padx=6)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                text_color="#D1FAE5" if is_dark else self.TEXT_MUTED,
                font=("", 12),
            ).pack(anchor="w", padx=18, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=value,
                text_color="#FFFFFF" if is_dark else self.TEXT_PRIMARY,
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
            text_color=self.TEXT_PRIMARY,
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            left_card,
            text="[Bar Chart Area — 2/3 width]",
            text_color=self.TEXT_MUTED,
        ).pack(expand=True)

        right_card = self._make_card(mid)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="Where it goes",
            text_color=self.TEXT_PRIMARY,
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            right_card,
            text="[Donut Breakdown — 1/3 width]",
            text_color=self.TEXT_MUTED,
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
            text_color=self.TEXT_PRIMARY,
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            left_card,
            text="[Transactions List — 2/3 width]",
            text_color=self.TEXT_MUTED,
        ).pack(expand=True)

        right_card = self._make_card(bot)
        right_card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(
            right_card,
            text="A little closer to your goals",
            text_color=self.TEXT_PRIMARY,
            font=("", 15, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(
            right_card,
            text="[Progress Bars — 1/3 width]",
            text_color=self.TEXT_MUTED,
        ).pack(expand=True)

    def _make_card(self, parent, dark=False, **kwargs):
        return ctk.CTkFrame(
            parent,
            fg_color=self.BG_DARK_CARD if dark else self.BG_CARD,
            corner_radius=14,
            border_width=0 if dark else 1,
            border_color=self.BORDER_COLOR,
            **kwargs,
        )


if __name__ == "__main__":
    Application().mainloop()