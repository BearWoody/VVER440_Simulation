import tkinter as tk
from tkinter import ttk
import random
import math


class NuclearVelin:
    def __init__(self, root):
        self.root = root
        self.root.title("Watt's Next - Jaderný Blok (Dukovany VVER-440 Mod - FINAL SBO EDITION)")
        self.root.geometry("1450x950")
        self.root.configure(bg="#121212")

        self.core_temp = 20.0
        self.MAX_CORE_TEMP = 400.0
        self.scrammed = False

        self.rod_position = 0.0
        self.core_power_mwt = 0.1
        self.reactivity = 0.0
        self.fuel_state = 100.0

        self.prim_pressure = 12.25
        self.MAX_PRIM_PRESSURE = 16.0
        self.MIN_PRIM_PRESSURE = 9.0

        self.sg_temp = 20.0
        self.sg_water_lvl = 100.0
        self.steam_pressure = 0.0
        self.MAX_PRESSURE = 10.0

        self.condenser_pressure = 0.01
        self.MAX_COND_PRESSURE = 0.15

        self.turbine1_rpm = 0.0
        self.turbine2_rpm = 0.0
        self.TARGET_RPM = 3000.0
        self.MAX_RPM = 4500.0
        self.turbine1_mw = 0.0
        self.turbine2_mw = 0.0
        self.total_energy = 0.0

        self.tg1_connected = False
        self.tg2_connected = False
        self.tg1_voltage = 0.0
        self.tg2_voltage = 0.0
        self.tg1_phase = 0.0
        self.tg2_phase = 0.0

        self.GRID_VOLTAGE = 400.0
        self.GRID_HZ = 50.0
        self.national_demand = 8500.0
        self.other_power = 8500.0

        self.blackout_active = False
        self.dg_running = False
        self.dg_rpm = 0.0

        self.sync_window = None
        self.ic_window = None
        self.suz_window = None
        self.active_sync_tg = 0

        self.destroyed = False

        self.vytvor_ui()
        self.aktualizuj_fyziku()

    def vytvor_posuvnik(self, parent, text, length=180, command=None):
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill="x", pady=(5, 0))

        if text: tk.Label(frame, text=text, font=("Consolas", 9), bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w")

        ctrl_frame = tk.Frame(frame, bg="#1e1e1e")
        ctrl_frame.pack(anchor="w")

        btn_m = tk.Button(ctrl_frame, text="-", bg="#333333", fg="white", font=("Consolas", 10, "bold"), width=2)
        btn_m.pack(side="left")

        scale = tk.Scale(ctrl_frame, from_=0, to=100, orient="horizontal", bg="#1e1e1e", fg="white",
                         highlightthickness=0, length=length)
        if command: scale.config(command=command)
        scale.pack(side="left", padx=5)

        btn_p = tk.Button(ctrl_frame, text="+", bg="#333333", fg="white", font=("Consolas", 10, "bold"), width=2)
        btn_p.pack(side="left")

        def dec():
            if scale.cget("state") != "disabled": scale.set(max(0, scale.get() - 1))

        def inc():
            if scale.cget("state") != "disabled": scale.set(min(100, scale.get() + 1))

        btn_m.config(command=dec)
        btn_p.config(command=inc)

        return scale

    def vytvor_ui(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Red.Horizontal.TProgressbar", background='#cc0000')
        style.configure("Green.Horizontal.TProgressbar", background='#00cc44')

        tk.Label(self.root, text="VELÍN JADERNÉHO BLOKU (DUKOVANY VVER-440)", font=("Consolas", 20, "bold"),
                 bg="#121212", fg="#ffcc00").pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=1350, height=180, bg="#1a1a1a", highlightthickness=1,
                                highlightbackground="#333333")
        self.canvas.pack(pady=(0, 10))

        self.canvas.create_line(250, 90, 450, 90, fill="#cc0000", width=4)
        self.canvas.create_line(450, 130, 250, 130, fill="#0066cc", width=4)
        self.canvas.create_line(600, 90, 800, 90, fill="#ffffff", width=4)
        self.canvas.create_line(850, 120, 850, 140, fill="#aaaaaa", width=4)
        self.canvas.create_line(800, 150, 525, 150, 525, 140, fill="#0066cc", width=4)
        self.canvas.create_line(900, 150, 1100, 150, fill="#00ccff", width=4)

        self.gfx_reaktor = self.canvas.create_rectangle(150, 50, 250, 150, fill="#cc0000", outline="white", width=2)
        self.text_reaktor = self.canvas.create_text(200, 100, text="REAKTOR", fill="white",
                                                    font=("Consolas", 10, "bold"))
        self.gfx_ko = self.canvas.create_oval(300, 20, 360, 70, fill="#cc0000", outline="white", width=2)
        self.text_ko = self.canvas.create_text(330, 45, text="KO", fill="white", font=("Consolas", 9, "bold"))
        self.gfx_pg = self.canvas.create_rectangle(450, 50, 600, 140, fill="#cc0000", outline="white", width=2)
        self.text_pg = self.canvas.create_text(525, 95, text="PAROGENERÁTOR", fill="white",
                                               font=("Consolas", 10, "bold"))
        self.gfx_turb = self.canvas.create_polygon(800, 70, 950, 50, 950, 120, 800, 100, fill="#cc0000",
                                                   outline="white", width=2)
        self.text_turb = self.canvas.create_text(875, 85, text="TURBÍNY", fill="white", font=("Consolas", 10, "bold"))
        self.gfx_cond = self.canvas.create_rectangle(800, 140, 900, 165, fill="#cc0000", outline="white", width=2)
        self.text_cond = self.canvas.create_text(850, 152, text="KONDENZÁTOR", fill="white",
                                                 font=("Consolas", 9, "bold"))
        self.gfx_vez = self.canvas.create_polygon(1100, 50, 1160, 50, 1180, 160, 1080, 160, fill="#cc0000",
                                                  outline="white", width=2)
        self.text_vez = self.canvas.create_text(1130, 105, text="VĚŽE", fill="white", font=("Consolas", 10, "bold"))

        main_frame = tk.Frame(self.root, bg="#121212")
        main_frame.pack(fill="both", expand=True, padx=20)

        frame_reactor = tk.Frame(main_frame, bg="#1e1e1e", bd=2, relief="sunken", padx=10, pady=10)
        frame_reactor.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(frame_reactor, text="[ PRIMÁRNÍ OKRUH ]", font=("Consolas", 14), bg="#1e1e1e", fg="#aaaaaa").pack()

        self.lbl_core_temp = tk.Label(frame_reactor, text="Teplota jádra: 20 °C", font=("Consolas", 12), bg="#1e1e1e",
                                      fg="#00cc44")
        self.lbl_core_temp.pack(anchor="w", pady=(5, 0))
        self.bar_core_temp = ttk.Progressbar(frame_reactor, orient="horizontal", length=250, mode="determinate",
                                             style="Red.Horizontal.TProgressbar")
        self.bar_core_temp.pack(pady=2)

        self.lbl_core_power = tk.Label(frame_reactor, text="Tepelný výkon: 0.1 MWt", font=("Consolas", 11),
                                       bg="#1e1e1e", fg="#00ccff")
        self.lbl_core_power.pack(anchor="w", pady=(2, 0))

        self.lbl_fuel = tk.Label(frame_reactor, text="Stav paliva: 100.0 %", font=("Consolas", 11), bg="#1e1e1e",
                                 fg="#ffcc00")
        self.lbl_fuel.pack(anchor="w", pady=(0, 10))

        self.btn_suz_panel = tk.Button(frame_reactor, text="ŘÍDICÍ PULT SUZ (REAKTOR)", bg="#aa0000", fg="white",
                                       font=("Consolas", 11, "bold"), command=self.open_suz_panel)
        self.btn_suz_panel.pack(fill="x", pady=(0, 15), ipady=5)

        self.slider_prim_pump = self.vytvor_posuvnik(frame_reactor, "Výkon hl. cirkulačních čerpadel")

        tk.Label(frame_reactor, text="[ KOMPENZÁTOR OBJEMU ]", font=("Consolas", 12), bg="#1e1e1e", fg="#aaaaaa").pack(
            pady=(15, 0))

        self.lbl_prim_pressure = tk.Label(frame_reactor, text="Tlak primáru: 12.25 MPa", font=("Consolas", 11, "bold"),
                                          bg="#cc0000", fg="white", padx=5)
        self.lbl_prim_pressure.pack(anchor="w")
        self.bar_prim_pressure = ttk.Progressbar(frame_reactor, orient="horizontal", length=250, mode="determinate",
                                                 style="Red.Horizontal.TProgressbar")
        self.bar_prim_pressure.pack(pady=2)

        self.slider_ko_heaters = self.vytvor_posuvnik(frame_reactor, "Ohříváky (Zvyšují tlak)", length=100)
        self.slider_ko_sprays = self.vytvor_posuvnik(frame_reactor, "Sprchy (Snižují tlak)", length=100)

        frame_sg = tk.Frame(main_frame, bg="#1e1e1e", bd=2, relief="sunken", padx=10, pady=10)
        frame_sg.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(frame_sg, text="[ PAROGENERÁTOR ]", font=("Consolas", 14), bg="#1e1e1e", fg="#aaaaaa").pack()

        self.lbl_sg_temp = tk.Label(frame_sg, text="Teplota PG: 20 °C", font=("Consolas", 12), bg="#1e1e1e",
                                    fg="#00cc44")
        self.lbl_sg_temp.pack(anchor="w", pady=(10, 0))

        self.lbl_sg_water = tk.Label(frame_sg, text="Hladina vody: 100 %", font=("Consolas", 12), bg="#1e1e1e",
                                     fg="#ff4444")
        self.lbl_sg_water.pack(anchor="w", pady=(10, 0))
        self.bar_sg_water = ttk.Progressbar(frame_sg, orient="horizontal", length=250, mode="determinate",
                                            style="Red.Horizontal.TProgressbar")
        self.bar_sg_water.pack(pady=2)

        self.lbl_pressure = tk.Label(frame_sg, text="Tlak páry: 0.00 MPa", font=("Consolas", 12), bg="#1e1e1e",
                                     fg="#00cc44")
        self.lbl_pressure.pack(anchor="w", pady=(10, 0))
        self.bar_pressure = ttk.Progressbar(frame_sg, orient="horizontal", length=250, mode="determinate",
                                            style="Red.Horizontal.TProgressbar")
        self.bar_pressure.pack(pady=2)

        self.slider_feed_pump = self.vytvor_posuvnik(frame_sg, "Napájecí čerpadlo (Doplňování vody)")

        frame_turb = tk.Frame(main_frame, bg="#1e1e1e", bd=2, relief="sunken", padx=10, pady=10)
        frame_turb.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(frame_turb, text="[ STROJOVNA ]", font=("Consolas", 14), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(0, 5))

        self.link_turbines = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_turb, text="Spřáhnout ventily (TG1 = TG2)", variable=self.link_turbines, bg="#1e1e1e",
                       fg="white", selectcolor="#333333", activebackground="#1e1e1e").pack(anchor="w")

        self.lbl_rpm1 = tk.Label(frame_turb, text="Otáčky TG1: 0 RPM", font=("Consolas", 11), bg="#1e1e1e",
                                 fg="#00cc44")
        self.lbl_rpm1.pack(anchor="w", pady=(5, 0))
        self.bar_rpm1 = ttk.Progressbar(frame_turb, orient="horizontal", length=250, mode="determinate",
                                        style="Red.Horizontal.TProgressbar")
        self.bar_rpm1.pack(pady=2)

        self.btn_grid_tg1 = tk.Button(frame_turb, text="TG1: PŘIPRAVIT FÁZOVÁNÍ", bg="#0066cc", fg="white",
                                      font=("Consolas", 10, "bold"), command=lambda: self.open_sync_panel(1))
        self.btn_grid_tg1.pack(anchor="w", pady=(2, 5))

        self.slider_turb1_valve = self.vytvor_posuvnik(frame_turb, "Parní ventil TG1", command=self.on_tg1_move)

        self.lbl_rpm2 = tk.Label(frame_turb, text="Otáčky TG2: 0 RPM", font=("Consolas", 11), bg="#1e1e1e",
                                 fg="#00cc44")
        self.lbl_rpm2.pack(anchor="w", pady=(5, 0))
        self.bar_rpm2 = ttk.Progressbar(frame_turb, orient="horizontal", length=250, mode="determinate",
                                        style="Red.Horizontal.TProgressbar")
        self.bar_rpm2.pack(pady=2)

        self.btn_grid_tg2 = tk.Button(frame_turb, text="TG2: PŘIPRAVIT FÁZOVÁNÍ", bg="#0066cc", fg="white",
                                      font=("Consolas", 10, "bold"), command=lambda: self.open_sync_panel(2))
        self.btn_grid_tg2.pack(anchor="w", pady=(2, 5))

        self.slider_turb2_valve = self.vytvor_posuvnik(frame_turb, "Parní ventil TG2")

        self.lbl_mw = tk.Label(frame_turb, text="Výkon: 0.0 MW", font=("Consolas", 14, "bold"), bg="#1e1e1e",
                               fg="#00cc44")
        self.lbl_mw.pack(anchor="w", pady=(10, 0))

        self.lbl_grid_hz = tk.Label(frame_turb, text="Síť: 50.000 Hz", font=("Consolas", 12, "bold"), bg="#1e1e1e",
                                    fg="#00ccff")
        self.lbl_grid_hz.pack(anchor="w", pady=(2, 0))

        self.lbl_total = tk.Label(frame_turb, text="Celkem dodáno: 0.00 MWh", font=("Consolas", 10), bg="#1e1e1e",
                                  fg="#aaaaaa")
        self.lbl_total.pack(anchor="w")

        frame_cooling = tk.Frame(main_frame, bg="#1e1e1e", bd=2, relief="sunken", padx=10, pady=10)
        frame_cooling.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(frame_cooling, text="[ TERCIÁRNÍ OKRUH ]", font=("Consolas", 14), bg="#1e1e1e", fg="#aaaaaa").pack()
        tk.Label(frame_cooling, text="(Chladicí věže & Kondenzátor)", font=("Consolas", 9), bg="#1e1e1e",
                 fg="#777777").pack(pady=(0, 15))

        self.lbl_cond_pressure = tk.Label(frame_cooling, text="Tlak (Vakuum): 0.01 MPa", font=("Consolas", 12, "bold"),
                                          bg="#1e1e1e", fg="#00cc44")
        self.lbl_cond_pressure.pack(anchor="w")
        self.bar_cond_pressure = ttk.Progressbar(frame_cooling, orient="horizontal", length=250, mode="determinate",
                                                 style="Red.Horizontal.TProgressbar")
        self.bar_cond_pressure.pack(pady=2)

        self.slider_cooling_pump = self.vytvor_posuvnik(frame_cooling, "Čerpadla chladicí vody (Věže)")
        self.slider_steam_dump = self.vytvor_posuvnik(frame_cooling, "Odfuk páry do atmosféry (BRU-A)")

        tk.Label(frame_cooling, text="[ NOUZOVÉ NAPÁJENÍ ]", font=("Consolas", 12), bg="#1e1e1e", fg="#aaaaaa").pack(
            pady=(25, 0))
        self.lbl_dg = tk.Label(frame_cooling, text="Dieselagregáty (6kV): VYP", font=("Consolas", 11, "bold"),
                               bg="#1e1e1e", fg="gray")
        self.lbl_dg.pack(anchor="w", pady=(5, 0))
        self.bar_dg = ttk.Progressbar(frame_cooling, orient="horizontal", length=250, mode="determinate",
                                      style="Green.Horizontal.TProgressbar")
        self.bar_dg.pack(pady=2)

        frame_bottom = tk.Frame(self.root, bg="#121212")
        frame_bottom.pack(fill="x", padx=20, pady=15)

        self.btn_scram = tk.Button(frame_bottom, text="AZ (HAVARIJNÍ OCHRANA)", font=("Consolas", 14, "bold"),
                                   bg="#550000", fg="white", command=self.trigger_scram)
        self.btn_scram.pack(side="left", ipadx=10, ipady=5, padx=(0, 20))

        self.btn_restart = tk.Button(frame_bottom, text="RESTART SIMULACE", font=("Consolas", 12, "bold"), bg="#0066cc",
                                     fg="white", command=self.apply_ic_cold)
        self.btn_restart.pack(side="left", padx=5)

        self.btn_ic_menu = tk.Button(frame_bottom, text="TRÉNINKOVÉ SCÉNÁŘE", font=("Consolas", 12, "bold"),
                                     bg="#9900cc", fg="white", command=self.open_ic_window)
        self.btn_ic_menu.pack(side="left", padx=20)

        self.btn_blackout = tk.Button(frame_bottom, text="VÝPADEK SÍTĚ", font=("Consolas", 12, "bold"), bg="#cc9900",
                                      fg="black", command=self.trigger_blackout)
        self.btn_blackout.pack(side="right", padx=5, ipady=3)

        self.btn_dg = tk.Button(frame_bottom, text="START DIESEL", font=("Consolas", 12, "bold"), bg="#555555",
                                fg="white", command=self.toggle_dg)
        self.btn_dg.pack(side="right", padx=10, ipady=3)

        self.lbl_status = tk.Label(frame_bottom, text="[ STATUS ] - Běžný provoz.", font=("Consolas", 12), bg="#121212",
                                   fg="white")
        self.lbl_status.pack(side="left", padx=30)

    def open_suz_panel(self):
        if self.destroyed: return
        if self.suz_window is not None and self.suz_window.winfo_exists():
            self.suz_window.focus()
            return
        self.suz_window = tk.Toplevel(self.root)
        self.suz_window.title("Pult řízení SUZ (VVER-440)")
        self.suz_window.geometry("640x540")
        self.suz_window.configure(bg="#1a1a1a")
        self.suz_window.resizable(False, False)
        self.suz_window.transient(self.root)

        tk.Label(self.suz_window, text="SYSTÉM ŘÍZENÍ A OCHRANY", font=("Consolas", 16, "bold"), bg="#1a1a1a",
                 fg="white").pack(pady=10)

        content_frame = tk.Frame(self.suz_window, bg="#1a1a1a")
        content_frame.pack(fill="both", expand=True)
        left_frame = tk.Frame(content_frame, bg="#1a1a1a")
        left_frame.pack(side="left", fill="both", expand=True)
        right_frame = tk.Frame(content_frame, bg="#1a1a1a")
        right_frame.pack(side="right", fill="y", padx=20)

        self.suz_canvas = tk.Canvas(left_frame, width=220, height=130, bg="#222222", highlightthickness=2,
                                    highlightbackground="#555555")
        self.suz_canvas.pack(pady=10)
        self.suz_canvas.create_arc(20, 20, 200, 200, start=0, extent=180, outline="#888888", width=3, style="arc")
        for i in range(-5, 6):
            angle = math.radians(90 - i * 14)
            r_inner = 80
            r_outer = 90 if i % 5 == 0 else 85
            x1 = 110 + r_inner * math.cos(angle)
            y1 = 110 - r_inner * math.sin(angle)
            x2 = 110 + r_outer * math.cos(angle)
            y2 = 110 - r_outer * math.sin(angle)
            self.suz_canvas.create_line(x1, y1, x2, y2, fill="#aaaaaa", width=2 if i % 5 == 0 else 1)

        self.suz_canvas.create_text(110, 45, text="0", fill="white", font=("Consolas", 9))
        self.suz_canvas.create_text(40, 100, text="- \u03C1", fill="#00cc44", font=("Consolas", 12, "bold"))
        self.suz_canvas.create_text(180, 100, text="+ \u03C1", fill="#ff4444", font=("Consolas", 12, "bold"))

        self.suz_needle = self.suz_canvas.create_line(110, 110, 110, 25, fill="white", width=3, arrow=tk.LAST)
        self.suz_canvas.create_oval(105, 105, 115, 115, fill="#aaaaaa")

        info_frame = tk.Frame(left_frame, bg="#1a1a1a")
        info_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(info_frame, text="Tepelný výkon:", font=("Consolas", 11), bg="#1a1a1a", fg="#aaaaaa").grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w")
        self.lbl_suz_power = tk.Label(info_frame, text="0.0 MWt", font=("Consolas", 12, "bold"), bg="#1a1a1a",
                                      fg="#00ccff")
        self.lbl_suz_power.grid(row=0, column=1, sticky="e", padx=20)

        tk.Label(info_frame, text="Teplota jádra:", font=("Consolas", 11), bg="#1a1a1a", fg="#aaaaaa").grid(row=1,
                                                                                                            column=0,
                                                                                                            sticky="w")
        self.lbl_suz_temp = tk.Label(info_frame, text="0.0 °C", font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="white")
        self.lbl_suz_temp.grid(row=1, column=1, sticky="e", padx=20)

        tk.Label(info_frame, text="Poloha tyčí HRK:", font=("Consolas", 11), bg="#1a1a1a", fg="#aaaaaa").grid(row=2,
                                                                                                              column=0,
                                                                                                              sticky="w",
                                                                                                              pady=(10,
                                                                                                                    0))
        self.lbl_suz_rods = tk.Label(info_frame, text="0.0 %", font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="yellow")
        self.lbl_suz_rods.grid(row=2, column=1, sticky="e", padx=20, pady=(10, 0))

        ctrl_frame = tk.Frame(left_frame, bg="#1a1a1a")
        ctrl_frame.pack(pady=20)

        btn_fast_in = tk.Button(ctrl_frame, text="ZASUNOUT (-1%)", bg="#00cc44", fg="black",
                                font=("Consolas", 10, "bold"), width=18, command=lambda: self.move_rods(-1.0))
        btn_fast_in.grid(row=0, column=0, padx=5, pady=5)
        btn_step_in = tk.Button(ctrl_frame, text="KROK DOLŮ (-0.1%)", bg="#333333", fg="white", font=("Consolas", 10),
                                width=18, command=lambda: self.move_rods(-0.1))
        btn_step_in.grid(row=0, column=1, padx=5, pady=5)
        btn_step_out = tk.Button(ctrl_frame, text="KROK NAHORU (+0.1%)", bg="#333333", fg="white",
                                 font=("Consolas", 10), width=18, command=lambda: self.move_rods(0.1))
        btn_step_out.grid(row=1, column=0, padx=5, pady=5)
        btn_fast_out = tk.Button(ctrl_frame, text="VYTÁHNOUT (+1%)", bg="#ff4444", fg="black",
                                 font=("Consolas", 10, "bold"), width=18, command=lambda: self.move_rods(1.0))
        btn_fast_out.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(right_frame, text="SKUPINA TYČÍ HRK", font=("Consolas", 10, "bold"), bg="#1a1a1a", fg="#aaaaaa").pack(
            pady=(0, 5))
        self.rod_canvas = tk.Canvas(right_frame, width=180, height=400, bg="#111111", highlightthickness=2,
                                    highlightbackground="#444444")
        self.rod_canvas.pack()

        for i in range(0, 101, 10):
            y = 360 - (i / 100.0) * 180
            self.rod_canvas.create_line(30, y, 40, y, fill="#888888")
            if i % 25 == 0 or i == 100:
                self.rod_canvas.create_text(15, y, text=f"{i}%", fill="#aaaaaa", font=("Consolas", 8))

        self.rod_canvas.create_rectangle(45, 20, 165, 180, fill="#222222", outline="#555555", width=2)
        self.rod_canvas.create_rectangle(45, 180, 165, 360, fill="#1a0000", outline="#cc0000", width=2)
        self.rod_canvas.create_text(105, 270, text="AKTIVNÍ\nZÓNA", fill="#ff4444", font=("Consolas", 14, "bold"),
                                    justify="center")

        self.rod_gfx_list = []
        start_x = 55
        spacing = 18
        rod_width = 10
        for i in range(6):
            x1 = start_x + (i * spacing)
            x2 = x1 + rod_width
            rod = self.rod_canvas.create_rectangle(x1, 180, x2, 360, fill="#cccccc", outline="#ffffff", width=1)
            self.rod_gfx_list.append(rod)

        self.update_suz_panel()

    def move_rods(self, delta):
        if not self.scrammed:
            self.rod_position = max(0.0, min(100.0, self.rod_position + delta))

    def update_suz_panel(self):
        if not self.suz_window or not self.suz_window.winfo_exists() or self.destroyed: return

        self.lbl_suz_power.config(text=f"{self.core_power_mwt:.1f} MWt")
        self.lbl_suz_temp.config(text=f"{self.core_temp:.1f} °C")
        self.lbl_suz_rods.config(text=f"{self.rod_position:.1f} %")

        angle = max(-70, min(70, self.reactivity * 15000))
        angle_rad = math.radians(angle - 90)
        x = 110 + 85 * math.cos(angle_rad)
        y = 110 + 85 * math.sin(angle_rad)
        self.suz_canvas.coords(self.suz_needle, 110, 110, x, y)
        self.suz_canvas.itemconfig(self.suz_needle, fill="#ff4444" if self.reactivity > 0.0001 else (
            "#00cc44" if self.reactivity < -0.0001 else "white"))

        offset = (self.rod_position / 100.0) * 180
        for rod in self.rod_gfx_list:
            coords = self.rod_canvas.coords(rod)
            if len(coords) == 4:
                x1, _, x2, _ = coords
                self.rod_canvas.coords(rod, x1, 180 - offset, x2, 360 - offset)

        self.suz_window.after(100, self.update_suz_panel)

    def open_ic_window(self):
        if self.destroyed: return
        if self.ic_window is not None and self.ic_window.winfo_exists():
            self.ic_window.focus()
            return
        self.ic_window = tk.Toplevel(self.root)
        self.ic_window.title("Počáteční stavy a Kampaň")
        self.ic_window.geometry("450x450")
        self.ic_window.configure(bg="#1a1a1a")
        self.ic_window.resizable(False, False)
        self.ic_window.transient(self.root)
        tk.Label(self.ic_window, text="PALIVOVÁ KAMPAŇ A SCÉNÁŘE", font=("Consolas", 14, "bold"), bg="#1a1a1a",
                 fg="white").pack(pady=(15, 5))
        tk.Label(self.ic_window, text="- START A FÁZOVÁNÍ -", font=("Consolas", 10), bg="#1a1a1a", fg="#aaaaaa").pack(
            pady=(5, 2))
        btn_cold = tk.Button(self.ic_window, text="1) COLD START (100% palivo)", bg="#333333", fg="white",
                             font=("Consolas", 11), command=self.apply_ic_cold)
        btn_cold.pack(fill="x", padx=40, pady=2)
        btn_sync = tk.Button(self.ic_window, text="2) PŘED FÁZOVÁNÍM (Zahřáto, 100% palivo)", bg="#0066cc", fg="white",
                             font=("Consolas", 11), command=self.apply_ic_sync)
        btn_sync.pack(fill="x", padx=40, pady=2)
        tk.Label(self.ic_window, text="- NOMINÁLNÍ PROVOZ (Vyhořívání) -", font=("Consolas", 10), bg="#1a1a1a",
                 fg="#aaaaaa").pack(pady=(15, 2))
        btn_nom_100 = tk.Button(self.ic_window, text="3) BĚH: Palivo 100% (Tyče ~11%)", bg="#00cc44", fg="black",
                                font=("Consolas", 11, "bold"), command=self.apply_ic_nominal_100)
        btn_nom_100.pack(fill="x", padx=40, pady=2)
        btn_nom_75 = tk.Button(self.ic_window, text="4) BĚH: Palivo 75% (Tyče ~33%)", bg="#009933", fg="white",
                               font=("Consolas", 11, "bold"), command=self.apply_ic_nominal_75)
        btn_nom_75.pack(fill="x", padx=40, pady=2)
        btn_nom_50 = tk.Button(self.ic_window, text="5) BĚH: Palivo 50% (Tyče ~54%)", bg="#cca300", fg="black",
                               font=("Consolas", 11, "bold"), command=self.apply_ic_nominal_50)
        btn_nom_50.pack(fill="x", padx=40, pady=2)
        btn_nom_25 = tk.Button(self.ic_window, text="6) BĚH: Palivo 25% (Tyče ~76%)", bg="#cc6600", fg="white",
                               font=("Consolas", 11, "bold"), command=self.apply_ic_nominal_25)
        btn_nom_25.pack(fill="x", padx=40, pady=2)
        btn_nom_10 = tk.Button(self.ic_window, text="7) BĚH: Palivo 10% (Konec kampaně ~89%)", bg="#cc0000", fg="white",
                               font=("Consolas", 11, "bold"), command=self.apply_ic_nominal_10)
        btn_nom_10.pack(fill="x", padx=40, pady=2)

    def reset_status_for_ic(self):
        self.scrammed = False
        self.destroyed = False
        self.blackout_active = False
        self.dg_running = False
        self.dg_rpm = 0.0
        self.btn_scram.config(bg="#550000", state="normal")
        for slider in [self.slider_prim_pump, self.slider_ko_heaters, self.slider_ko_sprays, self.slider_feed_pump,
                       self.slider_turb1_valve, self.slider_turb2_valve, self.slider_cooling_pump,
                       self.slider_steam_dump]:
            slider.config(state="normal")
        self.btn_grid_tg1.config(state="normal")
        self.btn_grid_tg2.config(state="normal")
        self.btn_dg.config(bg="#555555", text="START DIESEL")
        if self.ic_window: self.ic_window.destroy()

    def apply_ic_cold(self):
        self.reset_status_for_ic()
        self.core_temp = 20.0
        self.core_power_mwt = 0.1
        self.rod_position = 0.0
        self.fuel_state = 100.0
        self.prim_pressure = 12.25
        self.sg_temp = 20.0
        self.steam_pressure = 0.0
        self.sg_water_lvl = 100.0
        self.condenser_pressure = 0.01
        self.turbine1_rpm = 0.0
        self.turbine2_rpm = 0.0
        self.tg1_connected = False
        self.tg2_connected = False
        self.btn_grid_tg1.config(bg="#0066cc", text="TG1: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
        self.btn_grid_tg2.config(bg="#0066cc", text="TG2: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
        self.GRID_HZ = 50.0
        self.national_demand = 8500.0
        self.other_power = 8500.0
        self.slider_prim_pump.set(0)
        self.slider_ko_heaters.set(0)
        self.slider_ko_sprays.set(0)
        self.slider_feed_pump.set(0)
        self.slider_cooling_pump.set(100)
        self.slider_steam_dump.set(0)
        self.slider_turb1_valve.set(0)
        self.slider_turb2_valve.set(0)
        self.lbl_status.config(text="[ SCÉNÁŘ ] - Blok je zcela vychladlý a odstavený.", fg="#aaaaaa")

    def apply_ic_sync(self):
        self.reset_status_for_ic()
        self.core_temp = 272.6
        self.core_power_mwt = 516.0
        self.fuel_state = 100.0
        self.rod_position = 10.1
        self.prim_pressure = 12.25
        self.sg_temp = 258.0
        self.steam_pressure = 4.6
        self.sg_water_lvl = 60.0
        self.condenser_pressure = 0.015
        self.turbine1_rpm = 2950.0
        self.turbine2_rpm = 2950.0
        self.tg1_connected = False
        self.tg2_connected = False
        self.btn_grid_tg1.config(bg="#0066cc", text="TG1: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
        self.btn_grid_tg2.config(bg="#0066cc", text="TG2: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
        self.GRID_HZ = 50.0
        self.national_demand = 8500.0
        self.other_power = 8500.0
        self.slider_prim_pump.set(100)
        self.slider_ko_heaters.set(4)
        self.slider_ko_sprays.set(0)
        self.slider_feed_pump.set(4)
        self.slider_cooling_pump.set(100)
        self.slider_steam_dump.set(17)
        self.slider_turb1_valve.set(3)
        self.slider_turb2_valve.set(3)
        self.lbl_status.config(text="[ SCÉNÁŘ ] - Dukovany termodynamicky vyváženy. Čeká se na fázování.", fg="#00ccff")

    def apply_ic_nominal_base(self, fuel_perc, rod_pos):
        self.reset_status_for_ic()
        self.core_temp = 297.1
        self.core_power_mwt = 1378.2
        self.fuel_state = fuel_perc
        self.rod_position = rod_pos
        self.prim_pressure = 12.25
        self.sg_temp = 258.0
        self.steam_pressure = 4.6
        self.sg_water_lvl = 60.0
        self.condenser_pressure = 0.005
        self.turbine1_rpm = 3000.0
        self.turbine2_rpm = 3000.0
        self.tg1_connected = True
        self.tg2_connected = True
        self.btn_grid_tg1.config(bg="#cc0000", text="TG1: SÍŤ (PŘIPOJENO)", fg="white")
        self.btn_grid_tg2.config(bg="#cc0000", text="TG2: SÍŤ (PŘIPOJENO)", fg="white")
        self.GRID_HZ = 50.0
        self.national_demand = 8500.0
        self.other_power = 8500.0 - 500.4
        self.slider_prim_pump.set(100)
        self.slider_ko_heaters.set(0)
        self.slider_ko_sprays.set(0)
        self.slider_feed_pump.set(11)
        self.slider_cooling_pump.set(100)
        self.slider_steam_dump.set(0)
        self.slider_turb1_valve.set(100)
        self.slider_turb2_valve.set(100)
        self.lbl_status.config(text=f"[ SCÉNÁŘ ] - Nominální běh bloku. Palivo {fuel_perc}%.", fg="#00cc44")

    def apply_ic_nominal_100(self):
        self.apply_ic_nominal_base(100.0, 11.1)

    def apply_ic_nominal_75(self):
        self.apply_ic_nominal_base(75.0, 32.7)

    def apply_ic_nominal_50(self):
        self.apply_ic_nominal_base(50.0, 54.4)

    def apply_ic_nominal_25(self):
        self.apply_ic_nominal_base(25.0, 76.0)

    def apply_ic_nominal_10(self):
        self.apply_ic_nominal_base(10.0, 89.0)

    def trigger_blackout(self):
        if self.destroyed or self.scrammed: return
        self.blackout_active = True
        self.tg1_connected = False
        self.tg2_connected = False
        self.btn_grid_tg1.config(bg="#333333", text="TG1: SÍŤ NEDOSTUPNÁ", fg="gray")
        self.btn_grid_tg2.config(bg="#333333", text="TG2: SÍŤ NEDOSTUPNÁ", fg="gray")
        self.lbl_status.config(
            text="[ BLACKOUT ] Vnější síť padla! Udržte generátory na 3000 RPM pro vlastní čerpadla!", fg="yellow",
            bg="#aa0000")
        if self.sync_window and self.sync_window.winfo_exists():
            self.sync_window.destroy()

    def toggle_dg(self):
        if not self.destroyed:
            self.dg_running = not self.dg_running
            if self.dg_running:
                self.btn_dg.config(bg="#00cc44", text="STOP DIESEL")
                self.lbl_status.config(text="[ ZÁLOHA ] Startuji obří Dieselagregáty!", fg="white", bg="#121212")
            else:
                self.btn_dg.config(bg="#555555", text="START DIESEL")

    def open_sync_panel(self, tg_id):
        if self.destroyed or self.blackout_active: return

        if (tg_id == 1 and self.tg1_connected) or (tg_id == 2 and self.tg2_connected):
            if tg_id == 1 and self.tg1_connected:
                self.tg1_connected = False
                self.btn_grid_tg1.config(bg="#0066cc", text="TG1: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
                self.lbl_status.config(text="[ SÍŤ ] - TG1 ručně odpojena ze sítě.", fg="white")
            elif tg_id == 2 and self.tg2_connected:
                self.tg2_connected = False
                self.btn_grid_tg2.config(bg="#0066cc", text="TG2: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
                self.lbl_status.config(text="[ SÍŤ ] - TG2 ručně odpojena ze sítě.", fg="white")
            return

        if self.sync_window is not None and self.sync_window.winfo_exists():
            self.sync_window.focus()
            return

        self.active_sync_tg = tg_id
        self.sync_window = tk.Toplevel(self.root)
        self.sync_window.title(f"Fázovací panel - TG{tg_id}")
        self.sync_window.geometry("450x570")
        self.sync_window.configure(bg="#1a1a1a")
        self.sync_window.resizable(False, False)
        self.sync_window.transient(self.root)

        tk.Label(self.sync_window, text=f"SYNCHRONIZACE TG{tg_id} DO SÍTĚ", font=("Consolas", 14, "bold"), bg="#1a1a1a",
                 fg="white").pack(pady=10)
        info_frame = tk.Frame(self.sync_window, bg="#1a1a1a")
        info_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(info_frame, text="FREKVENCE SÍTĚ:", font=("Consolas", 10), bg="#1a1a1a", fg="#aaaaaa").grid(row=0,
                                                                                                             column=0,
                                                                                                             sticky="w")
        self.lbl_sync_net_hz = tk.Label(info_frame, text="50.00 Hz", font=("Consolas", 12, "bold"), bg="#1a1a1a",
                                        fg="#00ccff")
        self.lbl_sync_net_hz.grid(row=0, column=1, sticky="e", padx=20)
        tk.Label(info_frame, text="FREKVENCE TG:", font=("Consolas", 10), bg="#1a1a1a", fg="#aaaaaa").grid(row=1,
                                                                                                           column=0,
                                                                                                           sticky="w")
        self.lbl_sync_tg_hz = tk.Label(info_frame, text="0.00 Hz", font=("Consolas", 12, "bold"), bg="#1a1a1a",
                                       fg="yellow")
        self.lbl_sync_tg_hz.grid(row=1, column=1, sticky="e", padx=20)
        tk.Label(info_frame, text="NAPĚTÍ SÍTĚ:", font=("Consolas", 10), bg="#1a1a1a", fg="#aaaaaa").grid(row=2,
                                                                                                          column=0,
                                                                                                          sticky="w",
                                                                                                          pady=(10, 0))
        tk.Label(info_frame, text="400.0 kV", font=("Consolas", 12, "bold"), bg="#1a1a1a", fg="#00ccff").grid(row=2,
                                                                                                              column=1,
                                                                                                              sticky="e",
                                                                                                              padx=20,
                                                                                                              pady=(10,
                                                                                                                    0))
        tk.Label(info_frame, text="NAPĚTÍ TG:", font=("Consolas", 10), bg="#1a1a1a", fg="#aaaaaa").grid(row=3, column=0,
                                                                                                        sticky="w")
        self.lbl_sync_tg_kv = tk.Label(info_frame, text="0.0 kV", font=("Consolas", 12, "bold"), bg="#1a1a1a",
                                       fg="yellow")
        self.lbl_sync_tg_kv.grid(row=3, column=1, sticky="e", padx=20)

        self.sync_canvas = tk.Canvas(self.sync_window, width=200, height=200, bg="#222222", highlightthickness=2,
                                     highlightbackground="#555555")
        self.sync_canvas.pack(pady=20)
        self.sync_canvas.create_oval(10, 10, 190, 190, outline="#888888", width=2)
        self.sync_canvas.create_line(100, 10, 100, 30, fill="red", width=4)
        self.sync_canvas.create_text(100, 45, text="0°", fill="white", font=("Consolas", 10))
        self.sync_canvas.create_text(40, 100, text="POMALU\n(-)", fill="#ff4444", font=("Consolas", 8),
                                     justify="center")
        self.sync_canvas.create_text(160, 100, text="RYCHLE\n(+)", fill="#00cc44", font=("Consolas", 8),
                                     justify="center")
        self.sync_needle = self.sync_canvas.create_line(100, 100, 100, 30, fill="white", width=3, arrow=tk.LAST)

        exc_frame = tk.Frame(self.sync_window, bg="#1a1a1a")
        exc_frame.pack(fill="x", padx=20)
        self.slider_excitation = self.vytvor_posuvnik(exc_frame, "Buzení generátoru (Úprava napětí kV)", length=300)
        curr_exc = (self.tg1_voltage if tg_id == 1 else self.tg2_voltage) / 450.0 * 100
        self.slider_excitation.set(curr_exc)
        self.btn_sync_connect = tk.Button(self.sync_window, text="SEPNOUT VYPÍNAČ (FÁZOVAT)",
                                          font=("Consolas", 14, "bold"), bg="#cc0000", fg="white",
                                          command=self.attempt_synchronization)
        self.btn_sync_connect.pack(pady=20, fill="x", padx=20)
        self.update_sync_panel()

    def update_sync_panel(self):
        if not self.sync_window or not self.sync_window.winfo_exists() or self.destroyed: return
        tg_id = self.active_sync_tg
        rpm = self.turbine1_rpm if tg_id == 1 else self.turbine2_rpm
        hz = rpm / 60.0
        exc_val = self.slider_excitation.get() / 100.0
        kv = exc_val * 450.0 * min(1.0, rpm / 3000.0)
        if tg_id == 1:
            self.tg1_voltage = kv
        else:
            self.tg2_voltage = kv
        phase = self.tg1_phase if tg_id == 1 else self.tg2_phase
        self.lbl_sync_net_hz.config(text=f"{self.GRID_HZ:.2f} Hz", fg="#00ccff")
        self.lbl_sync_tg_hz.config(text=f"{hz:.2f} Hz",
                                   fg="#00cc44" if (self.GRID_HZ - 0.1) <= hz <= (self.GRID_HZ + 0.1) else "yellow")
        self.lbl_sync_tg_kv.config(text=f"{kv:.1f} kV", fg="#00cc44" if 390 <= kv <= 410 else "yellow")
        angle_rad = math.radians(phase - 90)
        x = 100 + 70 * math.cos(angle_rad)
        y = 100 + 70 * math.sin(angle_rad)
        self.sync_canvas.coords(self.sync_needle, 100, 100, x, y)
        if phase < 15 or phase > 345:
            self.sync_canvas.itemconfig(self.sync_needle, fill="#00cc44")
        else:
            self.sync_canvas.itemconfig(self.sync_needle, fill="white")
        self.sync_window.after(100, self.update_sync_panel)

    def attempt_synchronization(self):
        tg_id = self.active_sync_tg
        hz = (self.turbine1_rpm if tg_id == 1 else self.turbine2_rpm) / 60.0
        kv = self.tg1_voltage if tg_id == 1 else self.tg2_voltage
        phase = self.tg1_phase if tg_id == 1 else self.tg2_phase
        hz_ok = (self.GRID_HZ - 0.2) <= hz <= (self.GRID_HZ + 0.2)
        kv_ok = 380.0 <= kv <= 420.0
        phase_ok = phase < 15 or phase > 345

        if hz_ok and kv_ok and phase_ok:
            if tg_id == 1:
                self.tg1_connected = True
                self.btn_grid_tg1.config(bg="#cc0000", text="TG1: SÍŤ (PŘIPOJENO)", fg="white")
            else:
                self.tg2_connected = True
                self.btn_grid_tg2.config(bg="#cc0000", text="TG2: SÍŤ (PŘIPOJENO)", fg="white")
            self.lbl_status.config(text=f"[ SÍŤ ] - TG{tg_id} byla čistě přifázována. Zvyšujte výkon.", fg="#00cc44")
            self.sync_window.destroy()
        else:
            duvod = []
            if not hz_ok: duvod.append("ROZDÍL FREKVENCE")
            if not kv_ok: duvod.append("ROZDÍL NAPĚTÍ")
            if not phase_ok: duvod.append("MIMO FÁZI")
            self.sync_window.destroy()
            self.havarie(f"ASYNCHRONNÍ PŘIPNUTÍ TG{tg_id} ({', '.join(duvod)})! DESTRUKCE HŘÍDELE!")

    def on_tg1_move(self, val):
        if self.link_turbines.get(): self.slider_turb2_valve.set(val)

    def trigger_scram(self):
        if not self.destroyed and not self.scrammed:
            self.scrammed = True
            self.rod_position = 0.0
            self.lbl_status.config(text="[ STATUS: AZ AKTIVOVÁNA! ] - Zbytkové teplo! Chlaďte reaktor!", fg="yellow",
                                   bg="#550000")
            self.btn_scram.config(bg="gray", state="disabled")

    def havarie(self, zprava):
        self.destroyed = True
        self.lbl_status.config(text=f"[ FATÁLNÍ SELHÁNÍ: {zprava} ]", fg="white", bg="red",
                               font=("Consolas", 14, "bold"))
        for slider in [self.slider_prim_pump, self.slider_ko_heaters, self.slider_ko_sprays, self.slider_feed_pump,
                       self.slider_turb1_valve, self.slider_turb2_valve, self.slider_cooling_pump,
                       self.slider_steam_dump]:
            slider.config(state="disabled")
        self.btn_grid_tg1.config(state="disabled")
        self.btn_grid_tg2.config(state="disabled")
        self.btn_dg.config(state="disabled")

    def aktualizuj_fyziku(self):
        if self.destroyed: return

        val_prim_pump = self.slider_prim_pump.get() / 100.0
        val_feed_pump = self.slider_feed_pump.get() / 100.0
        val_turb1_valve = self.slider_turb1_valve.get() / 100.0
        val_turb2_valve = self.slider_turb2_valve.get() / 100.0
        val_ko_heaters = self.slider_ko_heaters.get() / 100.0
        val_ko_sprays = self.slider_ko_sprays.get() / 100.0
        val_cooling_pump = self.slider_cooling_pump.get() / 100.0
        val_steam_dump = self.slider_steam_dump.get() / 100.0

        if self.dg_running:
            self.dg_rpm += (1500.0 - self.dg_rpm) * 0.05
        else:
            self.dg_rpm -= self.dg_rpm * 0.05
            if self.dg_rpm < 10: self.dg_rpm = 0.0

        has_grid = not self.blackout_active
        has_island = (self.turbine1_rpm >= 2700) or (self.turbine2_rpm >= 2700)
        has_dg = self.dg_rpm > 1400.0
        has_power = has_grid or has_island or has_dg

        if not has_grid and not has_island and not self.dg_running:
            self.toggle_dg()
            self.lbl_status.config(text="[ ZTRÁTA NAPÁJENÍ ] - Ostrov padl! Nouzový start Dieselagregátů!", fg="yellow",
                                   bg="#aa0000")

        if not has_power:
            val_prim_pump = 0.0
            val_feed_pump = 0.0
            val_cooling_pump = 0.0

        house_load_mw = (val_prim_pump * 16.0) + (val_feed_pump * 6.0) + (val_cooling_pump * 8.0)

        redukce1, redukce2 = 0.0, 0.0
        if self.turbine1_rpm > 3100:
            redukce1 = min(1.0, (self.turbine1_rpm - 3100) / 100.0)
            val_turb1_valve *= (1.0 - redukce1)
        if self.turbine2_rpm > 3100:
            redukce2 = min(1.0, (self.turbine2_rpm - 3100) / 100.0)
            val_turb2_valve *= (1.0 - redukce2)

        stara_teplota = self.core_temp

        if self.scrammed:
            self.rod_position = max(0.0, self.rod_position - 5.0)

        if self.core_power_mwt > 10.0 and not self.scrammed:
            self.fuel_state -= (self.core_power_mwt / 1378.0) * 0.00005
            self.fuel_state = max(10.0, self.fuel_state)

        req_rod = max(1.0, 89.0 - (self.fuel_state - 10.0) * 0.866)
        ratio = self.rod_position / req_rod
        target_temp = 20.0 + ratio * 277.0

        self.reactivity = (target_temp - self.core_temp) * 0.00005

        if self.core_power_mwt < 0.1: self.core_power_mwt = 0.1
        if self.scrammed:
            self.core_power_mwt *= 0.85
        else:
            self.core_power_mwt += self.core_power_mwt * self.reactivity

        self.core_power_mwt = min(2000.0, max(0.0, self.core_power_mwt))
        vygenerovane_teplo = self.core_power_mwt * 0.012

        rozdil_teplot = max(0, self.core_temp - self.sg_temp)
        predane_teplo = val_prim_pump * rozdil_teplot * 0.423

        self.core_temp += (vygenerovane_teplo - predane_teplo)
        self.core_temp -= (self.core_temp - 20.0) * 0.001

        delta_temp = self.core_temp - stara_teplota
        self.prim_pressure += delta_temp * 0.08
        self.prim_pressure += val_ko_heaters * 0.03
        self.prim_pressure -= val_ko_sprays * 0.06
        self.prim_pressure -= (self.prim_pressure - 12.25) * 0.0005
        self.prim_pressure = max(0.1, self.prim_pressure)

        if self.prim_pressure > 13.5 and has_power:
            self.prim_pressure -= 0.15
            if not self.blackout_active:
                self.lbl_status.config(text="[ VAROVÁNÍ ] - Pojišťovací ventily KO odpouští přetlak primáru!",
                                       fg="yellow", bg="#121212")

        self.sg_temp -= (self.sg_temp - 20.0) * 0.0005

        if self.core_temp < self.sg_temp:
            chladnuti_pg = (self.sg_temp - self.core_temp) * 0.01 * (val_prim_pump + 0.05)
            self.sg_temp -= chladnuti_pg
            self.steam_pressure = max(0.0, self.steam_pressure - chladnuti_pg * 0.05)

        self.sg_temp += predane_teplo * 0.05

        if self.sg_temp > 258.0 and self.sg_water_lvl > 0:
            prebytek_teploty = self.sg_temp - 258.0
            teplo_pro_var = prebytek_teploty / 0.05
            self.sg_temp = 258.0
            self.steam_pressure += teplo_pro_var * 0.0178
            self.sg_water_lvl -= teplo_pro_var * 0.01

        self.sg_temp = max(20.0, self.sg_temp)
        self.sg_water_lvl += val_feed_pump * 1.5
        self.sg_water_lvl = min(100.0, max(0.0, self.sg_water_lvl))

        if val_steam_dump > 0.0 and self.steam_pressure > 0.2:
            self.steam_pressure -= val_steam_dump * 0.60
            self.sg_water_lvl -= val_steam_dump * 0.25

        if self.steam_pressure > 8.0:
            self.steam_pressure -= 0.20
            self.sg_water_lvl -= 0.15

        prutok_pary_1 = 0.0
        prutok_pary_2 = 0.0
        if self.steam_pressure > 0.5:
            prutok_pary_1 = val_turb1_valve * self.steam_pressure * 0.40
            prutok_pary_2 = val_turb2_valve * self.steam_pressure * 0.40
            self.steam_pressure -= (prutok_pary_1 + prutok_pary_2) * 0.08

        self.steam_pressure = max(0.1, self.steam_pressure)
        self.condenser_pressure += (prutok_pary_1 + prutok_pary_2) * 0.00010
        self.condenser_pressure -= val_cooling_pump * 0.025
        self.condenser_pressure += 0.0001
        self.condenser_pressure = max(0.005, self.condenser_pressure)
        protitlak = max(0.0, self.condenser_pressure - 0.03)

        hz1 = self.turbine1_rpm / 60.0
        hz2 = self.turbine2_rpm / 60.0

        if not self.tg1_connected:
            self.tg1_phase = (self.tg1_phase + (hz1 - self.GRID_HZ) * 36.0) % 360.0
        else:
            self.tg1_phase = 0.0
        if not self.tg2_connected:
            self.tg2_phase = (self.tg2_phase + (hz2 - self.GRID_HZ) * 36.0) % 360.0
        else:
            self.tg2_phase = 0.0

        grid_connected_1 = self.tg1_connected
        grid_connected_2 = self.tg2_connected

        moment_pary_1 = (prutok_pary_1 * 500.0) - (protitlak * 8000.0)
        moment_pary_2 = (prutok_pary_2 * 500.0) - (protitlak * 8000.0)

        drag_1 = (self.turbine1_rpm / 1000.0) ** 3 * 1.5
        drag_2 = (self.turbine2_rpm / 1000.0) ** 3 * 1.5

        active_t = (1 if self.turbine1_rpm > 1000 else 0) + (1 if self.turbine2_rpm > 1000 else 0)
        req_torque = (house_load_mw / active_t) * 5.0 if (active_t > 0 and not has_dg) else 0.0

        if grid_connected_1:
            if moment_pary_1 > 2.0:
                odpor_gen_1 = moment_pary_1 + (self.turbine1_rpm - 3000) * 0.05
            else:
                self.tg1_connected = False
                self.btn_grid_tg1.config(bg="#0066cc", text="TG1: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
                odpor_gen_1 = drag_1
        else:
            if self.blackout_active and self.turbine1_rpm > 1000:
                odpor_gen_1 = drag_1 + req_torque
            else:
                odpor_gen_1 = drag_1

        if grid_connected_2:
            if moment_pary_2 > 2.0:
                odpor_gen_2 = moment_pary_2 + (self.turbine2_rpm - 3000) * 0.05
            else:
                self.tg2_connected = False
                self.btn_grid_tg2.config(bg="#0066cc", text="TG2: PŘIPRAVIT FÁZOVÁNÍ", fg="white")
                odpor_gen_2 = drag_2
        else:
            if self.blackout_active and self.turbine2_rpm > 1000:
                odpor_gen_2 = drag_2 + req_torque
            else:
                odpor_gen_2 = drag_2

        self.turbine1_rpm += (moment_pary_1 - odpor_gen_1) * 0.15
        self.turbine1_rpm = max(0.0, self.turbine1_rpm)
        self.turbine2_rpm += (moment_pary_2 - odpor_gen_2) * 0.15
        self.turbine2_rpm = max(0.0, self.turbine2_rpm)

        ucinnost = max(0.0, 1.0 - (protitlak * 10.0))

        if grid_connected_1:
            self.turbine1_mw = (prutok_pary_1 * 136.0 * ucinnost)
        elif self.blackout_active and self.turbine1_rpm > 1000 and not has_dg:
            self.turbine1_mw = house_load_mw / active_t
        else:
            self.turbine1_mw = 0.0

        if grid_connected_2:
            self.turbine2_mw = (prutok_pary_2 * 136.0 * ucinnost)
        elif self.blackout_active and self.turbine2_rpm > 1000 and not has_dg:
            self.turbine2_mw = house_load_mw / active_t
        else:
            self.turbine2_mw = 0.0

        celkovy_vykon_mw = self.turbine1_mw + self.turbine2_mw
        self.total_energy += celkovy_vykon_mw * (0.1 / 3600)

        if not self.blackout_active:
            self.national_demand += random.uniform(-1.5, 1.5)
            self.national_demand = max(7000.0, min(10000.0, self.national_demand))
            odchylka_frekvence = self.GRID_HZ - 50.0
            primarni_regulace = -odchylka_frekvence * 800.0
            self.other_power -= odchylka_frekvence * 1.5
            self.other_power = max(0.0, self.other_power)

            vykon_do_site = 0.0
            if grid_connected_1: vykon_do_site += self.turbine1_mw
            if grid_connected_2: vykon_do_site += self.turbine2_mw

            bilance_site = (self.other_power + primarni_regulace + vykon_do_site) - self.national_demand
            self.GRID_HZ += bilance_site * 0.00002

        if self.core_temp < 100 and not self.scrammed:
            c_reak = "#00cc44"
        elif self.core_temp < 315:
            c_reak = "#cc0000"
        elif self.core_temp < 330:
            c_reak = "yellow"
        else:
            c_reak = "#ffffff"

        self.canvas.itemconfig(self.gfx_reaktor, fill=c_reak)
        self.canvas.itemconfig(self.text_reaktor, fill="black" if self.core_temp >= 330 else "white")

        c_ko = "#00ff00" if self.prim_pressure > 14.5 or self.prim_pressure < 9.5 else (
            "yellow" if self.prim_pressure > 13.5 or self.prim_pressure < 10.0 else "#cc0000")
        if self.core_temp < 100 and self.prim_pressure < 10.0: c_ko = "#00cc44"
        self.canvas.itemconfig(self.gfx_ko, fill=c_ko)
        self.canvas.itemconfig(self.text_ko, fill="black" if (
                                                                         self.prim_pressure > 13.5 or self.prim_pressure < 10.0) and self.core_temp > 100 else "white")

        c_pg = "#00ff00" if self.steam_pressure > 8.0 or self.sg_water_lvl < 15 else (
            "yellow" if self.steam_pressure > 7.0 or self.sg_water_lvl < 30 else "#cc0000")
        if self.core_temp < 100 and self.steam_pressure < 1.0: c_pg = "#00cc44"
        self.canvas.itemconfig(self.gfx_pg, fill=c_pg)
        self.canvas.itemconfig(self.text_pg, fill="black" if (
                                                                         self.steam_pressure > 7.0 or self.sg_water_lvl < 30) and self.core_temp > 100 else "white")

        c_turb = "#cc0000" if grid_connected_1 or grid_connected_2 else "#00cc44"
        self.canvas.itemconfig(self.gfx_turb, fill=c_turb)
        self.canvas.itemconfig(self.text_turb, fill="white" if grid_connected_1 or grid_connected_2 else "black")

        c_cond = "#00ff00" if self.condenser_pressure > 0.10 else (
            "yellow" if self.condenser_pressure > 0.05 else "#cc0000")
        self.canvas.itemconfig(self.gfx_cond, fill=c_cond)
        self.canvas.itemconfig(self.text_cond, fill="black" if self.condenser_pressure > 0.05 else "white")

        c_vez = "#00ff00" if val_cooling_pump < 0.5 and self.condenser_pressure > 0.03 else "#cc0000"
        if val_cooling_pump < 0.2 and self.core_temp < 100: c_vez = "#00cc44"
        self.canvas.itemconfig(self.gfx_vez, fill=c_vez)
        self.canvas.itemconfig(self.text_vez,
                               fill="black" if val_cooling_pump < 0.5 and self.condenser_pressure > 0.03 else "white")

        self.lbl_core_temp.config(text=f"Teplota jádra: {self.core_temp:.1f} °C")
        self.bar_core_temp["value"] = min(100, (self.core_temp / self.MAX_CORE_TEMP) * 100)

        if self.core_temp < 100:
            self.lbl_core_temp.config(fg="#00cc44", bg="#1e1e1e")
        elif self.core_temp < 315:
            self.lbl_core_temp.config(fg="#ff4444", bg="#1e1e1e")
        elif self.core_temp < 330:
            self.lbl_core_temp.config(fg="yellow", bg="#1e1e1e")
        else:
            self.lbl_core_temp.config(fg="white", bg="red")

        self.lbl_core_power.config(text=f"Tepelný výkon: {self.core_power_mwt:.1f} MWt")
        self.lbl_fuel.config(text=f"Stav paliva: {self.fuel_state:.1f} %",
                             fg="#ffcc00" if self.fuel_state > 20 else "#ff4444")

        self.lbl_prim_pressure.config(text=f"Tlak primáru: {self.prim_pressure:.2f} MPa")
        self.bar_prim_pressure["value"] = min(100, (self.prim_pressure / self.MAX_PRIM_PRESSURE) * 100)
        if self.prim_pressure < self.MIN_PRIM_PRESSURE:
            self.lbl_prim_pressure.config(bg="yellow", fg="black")
        elif self.prim_pressure < 13.5:
            self.lbl_prim_pressure.config(bg="#cc0000", fg="white")
        else:
            self.lbl_prim_pressure.config(bg="red", fg="white")

        self.lbl_sg_temp.config(text=f"Teplota PG: {self.sg_temp:.1f} °C")
        self.lbl_sg_water.config(text=f"Hladina vody: {self.sg_water_lvl:.1f} %")
        self.bar_sg_water["value"] = self.sg_water_lvl

        self.lbl_pressure.config(text=f"Tlak páry: {self.steam_pressure:.2f} MPa")
        self.bar_pressure["value"] = min(100, (self.steam_pressure / self.MAX_PRESSURE) * 100)
        if self.steam_pressure < 1.0:
            self.lbl_pressure.config(fg="#00cc44")
        elif self.steam_pressure < 7.0:
            self.lbl_pressure.config(fg="#ff4444")
        else:
            self.lbl_pressure.config(fg="yellow")

        self.lbl_cond_pressure.config(text=f"Tlak (Vakuum): {self.condenser_pressure:.3f} MPa")
        self.bar_cond_pressure["value"] = min(100, (self.condenser_pressure / self.MAX_COND_PRESSURE) * 100)
        if self.condenser_pressure <= 0.02:
            self.lbl_cond_pressure.config(fg="#00cc44")
        elif self.condenser_pressure <= 0.05:
            self.lbl_cond_pressure.config(fg="yellow")
        else:
            self.lbl_cond_pressure.config(fg="red")

        if redukce1 > 0.05:
            self.lbl_rpm1.config(text=f"Otáčky TG1: {self.turbine1_rpm:.0f} RPM (REGULÁTOR!)", fg="#ffcc00")
        else:
            self.lbl_rpm1.config(text=f"Otáčky TG1: {self.turbine1_rpm:.0f} RPM",
                                 fg="#00cc44" if self.turbine1_rpm < 100 else (
                                     "#ff4444" if 2900 < self.turbine1_rpm < 3100 else "yellow"))
        self.bar_rpm1["value"] = min(100, (self.turbine1_rpm / self.MAX_RPM) * 100)

        if redukce2 > 0.05:
            self.lbl_rpm2.config(text=f"Otáčky TG2: {self.turbine2_rpm:.0f} RPM (REGULÁTOR!)", fg="#ffcc00")
        else:
            self.lbl_rpm2.config(text=f"Otáčky TG2: {self.turbine2_rpm:.0f} RPM",
                                 fg="#00cc44" if self.turbine2_rpm < 100 else (
                                     "#ff4444" if 2900 < self.turbine2_rpm < 3100 else "yellow"))
        self.bar_rpm2["value"] = min(100, (self.turbine2_rpm / self.MAX_RPM) * 100)

        self.bar_dg["value"] = min(100, (self.dg_rpm / 1500.0) * 100)
        if self.dg_running:
            if has_dg:
                self.lbl_dg.config(text=f"Dieselagregáty (6kV): {self.dg_rpm:.0f} RPM (BĚŽÍ)", fg="#00cc44")
            else:
                self.lbl_dg.config(text=f"Dieselagregáty (6kV): {self.dg_rpm:.0f} RPM (STARTUJE)", fg="yellow")
        else:
            self.lbl_dg.config(text=f"Dieselagregáty (6kV): {self.dg_rpm:.0f} RPM (VYP)", fg="gray")

        if self.blackout_active:
            self.lbl_grid_hz.config(text="Síť: OFFLINE (BLACKOUT)", fg="red")
            if not has_power:
                self.lbl_mw.config(text="Vlastní spotřeba: VÝPADEK NAPÁJENÍ!", fg="red")
            elif has_dg:
                self.lbl_mw.config(text="Vlastní spotřeba: Napájeno z DG", fg="#00cc44")
            else:
                self.lbl_mw.config(text=f"Vlastní spotřeba: {celkovy_vykon_mw:.1f} MW (Ostrov)", fg="yellow")
        else:
            barva_hz = "#00cc44" if 49.95 <= self.GRID_HZ <= 50.05 else (
                "yellow" if 49.8 <= self.GRID_HZ <= 50.2 else "#ff4444")
            self.lbl_grid_hz.config(text=f"Síť: {self.GRID_HZ:.3f} Hz", fg=barva_hz)
            self.lbl_mw.config(text=f"Výkon: {celkovy_vykon_mw:.1f} MW",
                               fg="#ff4444" if celkovy_vykon_mw > 0 else "#00cc44")

        self.lbl_total.config(text=f"Celkem dodáno: {self.total_energy:.2f} MWh")

        limit_kavitace = 200.0 + self.prim_pressure * 10.5

        if self.blackout_active and self.turbine1_rpm < 2700 and self.turbine2_rpm < 2700 and not has_dg:
            self.havarie("BLACKOUT SELHAL (Ztráta napájení čerpadel)!")
        elif self.core_temp > limit_kavitace:
            self.havarie("VAR V PRIMÁRU (KAVITACE ČERPADEL / ZTRÁTA CHLAZENÍ)!")
        elif self.core_temp >= 1200.0:
            self.havarie("TAVENÍ JÁDRA (MELTDOWN)!")
        elif self.prim_pressure >= self.MAX_PRIM_PRESSURE:
            self.havarie("PRASKL PRIMÁRNÍ OKRUH (LOCA)!")
        elif self.steam_pressure >= self.MAX_PRESSURE:
            self.havarie("EXPLOZE PAROVODU!")
        elif self.condenser_pressure >= self.MAX_COND_PRESSURE:
            self.havarie("ZTRÁTA VAKUA - DESTRUKCE LOPATEK!")
        elif self.turbine1_rpm >= self.MAX_RPM or self.turbine2_rpm >= self.MAX_RPM:
            self.havarie("PŘETOČENÍ A DESTRUKCE TURBÍNY!")

        if not self.destroyed:
            self.root.after(100, self.aktualizuj_fyziku)


if __name__ == "__main__":
    hlavni_okno = tk.Tk()
    app = NuclearVelin(hlavni_okno)
    hlavni_okno.mainloop()
