import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from puzzle import is_solvable
from main import ALGORITHMS, GOAL, parse_state, random_state, replay, run_algorithm
 
CELL = 100          
BOARD = CELL * 3
 
# Colours
BG = "#f4f4f8"
TILE = "#4f8ef7"
TILE_OK = "#34b36b"    
BLANK = "#d9dbe3"
TEXT = "#ffffff"
 
 
class PuzzleApp:
    def __init__(self, root):
        self.root = root
        root.title("8-Puzzle Solver")
        root.configure(bg=BG)
        root.resizable(False, False)
 
        self.results = {}      
        self.boards = [list(GOAL)]
        self.path = []
        self.step = 0
        self.playing = False
        self.after_id = None
        self.queue = queue.Queue()
        self.start_state = [1, 2, 5, 3, 4, 0, 6, 7, 8]
 
        self._build_widgets()
        self.show_board(self.start_state)
 
    def _build_widgets(self):
        left = tk.Frame(self.root, bg=BG)
        left.grid(row=0, column=0, padx=12, pady=12, sticky="n")
        right = tk.Frame(self.root, bg=BG)
        right.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="n")
 
        
        inp = tk.Frame(left, bg=BG)
        inp.pack(fill="x")
        tk.Label(inp, text="State:", bg=BG).grid(row=0, column=0, sticky="w")
        self.state_var = tk.StringVar(value="1,2,5,3,4,0,6,7,8")
        entry = tk.Entry(inp, textvariable=self.state_var, width=24)
        entry.grid(row=0, column=1, padx=4)
        entry.bind("<Return>", lambda e: self.on_load())
        ttk.Button(inp, text="Load", width=7, command=self.on_load).grid(row=0, column=2)
        ttk.Button(inp, text="Random", width=7, command=self.on_random).grid(row=0, column=3, padx=(4, 0))
 
        self.canvas = tk.Canvas(left, width=BOARD, height=BOARD, bg=BG,
                                highlightthickness=0)
        self.canvas.pack(pady=10)
 
        self.info_var = tk.StringVar(value="Load a state and press Solve")
        tk.Label(left, textvariable=self.info_var, bg=BG,
                 font=("Segoe UI", 11, "bold")).pack()
 
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(pady=6)
        ttk.Button(ctrl, text="|<", width=4, command=self.go_first).grid(row=0, column=0)
        ttk.Button(ctrl, text="<", width=4, command=self.go_prev).grid(row=0, column=1)
        self.play_btn = ttk.Button(ctrl, text="Play", width=8, command=self.toggle_play)
        self.play_btn.grid(row=0, column=2, padx=4)
        ttk.Button(ctrl, text=">", width=4, command=self.go_next).grid(row=0, column=3)
        ttk.Button(ctrl, text=">|", width=4, command=self.go_last).grid(row=0, column=4)
 
        self.slider = ttk.Scale(left, from_=0, to=0, orient="horizontal",
                                length=BOARD, command=self.on_slider)
        self.slider.pack()
 
        speed = tk.Frame(left, bg=BG)
        speed.pack(pady=(6, 0))
        tk.Label(speed, text="Speed:", bg=BG).pack(side="left")
        self.speed = ttk.Scale(speed, from_=1, to=20, orient="horizontal", length=160)
        self.speed.set(4)
        self.speed.pack(side="left", padx=4)
 
       
        top = tk.Frame(right, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text="Algorithm:", bg=BG).pack(side="left")
        names = ["Run all"] + [a[0] for a in ALGORITHMS]
        self.algo_var = tk.StringVar(value="A* Manhattan")
        ttk.Combobox(top, textvariable=self.algo_var, values=names, state="readonly",
                     width=16).pack(side="left", padx=6)
        self.solve_btn = ttk.Button(top, text="Solve", command=self.on_solve)
        self.solve_btn.pack(side="left")
 
        cols = ("algo", "cost", "expanded", "depth", "time")
        self.table = ttk.Treeview(right, columns=cols, show="headings", height=7)
        for col, title, width in (("algo", "Algorithm", 110), ("cost", "Cost", 60),
                                  ("expanded", "Expanded", 80), ("depth", "Depth", 60),
                                  ("time", "Time (s)", 80)):
            self.table.heading(col, text=title)
            self.table.column(col, width=width, anchor="center")
        self.table.pack(pady=10)
        self.table.bind("<Double-1>", self.on_row_select)
 
        self.status_var = tk.StringVar(value="Double-click a row to replay its path.")
        tk.Label(right, textvariable=self.status_var, bg=BG, fg="#555",
                 wraplength=420, justify="left").pack(anchor="w")
 
        self.moves_text = tk.Text(right, width=52, height=8, wrap="word", state="disabled")
        self.moves_text.pack(pady=(8, 0))
 
    def show_board(self, board):
        self.canvas.delete("all")
        for i, tile in enumerate(board):
            r, c = divmod(i, 3)
            x0, y0 = c * CELL + 4, r * CELL + 4
            x1, y1 = x0 + CELL - 8, y0 + CELL - 8
            if tile == 0:
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=BLANK, outline="")
            else:
                color = TILE_OK if tile == i else TILE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
                self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(tile),
                                        fill=TEXT, font=("Segoe UI", 34, "bold"))
 
    def refresh(self):
        
        self.show_board(self.boards[self.step])
        total = len(self.path)
        if self.step == 0:
            self.info_var.set(f"Start  (0 / {total})")
        else:
            self.info_var.set(f"Step {self.step} / {total}:  {self.path[self.step - 1]}")
        
        self.slider.configure(command=None)
        self.slider.set(self.step)
        self.slider.configure(command=self.on_slider)
 

    def on_load(self):
        try:
            state = parse_state(self.state_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid state", str(e))
            return
        self.set_start(state)
 
    def on_random(self):
        state = random_state()
        self.state_var.set(",".join(map(str, state)))
        self.set_start(state)
 
    def set_start(self, state):
        self.stop_play()
        self.start_state = state
        self.results = {}
        self.table.delete(*self.table.get_children())
        self.load_path([], state)
        if is_solvable(state):
            self.status_var.set("Press Solve.")
        else:
            self.status_var.set("This state has no solution (odd number of inversions).")
 
    def on_solve(self):
        try:
            state = parse_state(self.state_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid state", str(e))
            return
        if not is_solvable(state):
            messagebox.showwarning("No solution", "This state has no solution.")
            return
 
        self.set_start(state)
        choice = self.algo_var.get()
        todo = [a for a in ALGORITHMS if choice == "Run all" or a[0] == choice]
 
        self.solve_btn.state(["disabled"])
        self.status_var.set("Running ... (BFS / DFS / IDS can take a few seconds)")
        threading.Thread(target=self.worker, args=(state, todo), daemon=True).start()
        self.root.after(100, self.poll_queue)
 
    def worker(self, state, todo):
        for name, func, extra in todo:
            self.queue.put(("result", run_algorithm(name, func, state, *extra)))
        self.queue.put(("done", None))
 
    def poll_queue(self):
        finished = False
        try:
            while True:
                kind, data = self.queue.get_nowait()
                if kind == "result":
                    self.add_result(data)
                else:
                    finished = True
        except queue.Empty:
            pass
 
        if finished:
            self.solve_btn.state(["!disabled"])
            self.status_var.set("Done. Double-click a row to replay its path.")
        else:
            self.root.after(100, self.poll_queue)
 
    def add_result(self, res):
        self.results[res["name"]] = res
        self.table.insert("", "end", iid=res["name"], values=(
            res["name"], res["cost"], res["expanded"], res["depth"],
            f"{res['time']:.4f}"))
        # show the first finished path automatically
        if len(self.results) == 1 and res["path"] is not None:
            self.table.selection_set(res["name"])
            self.load_path(res["path"], self.start_state, res["name"])
 
    def on_row_select(self, _event):
        sel = self.table.selection()
        if not sel:
            return
        res = self.results.get(sel[0])
        if res and res["path"] is not None:
            self.load_path(res["path"], self.start_state, res["name"])
 

    def load_path(self, path, state, name=None):
        self.stop_play()
        self.path = path
        self.boards = replay(state, path)
        self.step = 0
        self.slider.configure(to=max(len(path), 1))
        self.refresh()
 
        self.moves_text.configure(state="normal")
        self.moves_text.delete("1.0", "end")
        if name and path:
            shown = ", ".join(path[:300])
            if len(path) > 300:
                shown += f" ... ({len(path) - 300} more)"
            self.moves_text.insert("end", f"{name} - {len(path)} moves:\n{shown}")
        self.moves_text.configure(state="disabled")
 
    def go_first(self):
        self.stop_play()
        self.step = 0
        self.refresh()
 
    def go_last(self):
        self.stop_play()
        self.step = len(self.path)
        self.refresh()
 
    def go_prev(self):
        self.stop_play()
        if self.step > 0:
            self.step -= 1
            self.refresh()
 
    def go_next(self):
        self.stop_play()
        if self.step < len(self.path):
            self.step += 1
            self.refresh()
 
    def on_slider(self, value):
        self.step = min(int(float(value)), len(self.path))
        self.show_board(self.boards[self.step])
        total = len(self.path)
        self.info_var.set("Start" if self.step == 0 else
                          f"Step {self.step} / {total}:  {self.path[self.step - 1]}")
 
    def toggle_play(self):
        if self.playing:
            self.stop_play()
        elif self.path:
            if self.step >= len(self.path):
                self.step = 0
            self.playing = True
            self.play_btn.configure(text="Pause")
            self.tick()
 
    def tick(self):
        if not self.playing:
            return
        if self.step >= len(self.path):
            self.stop_play()
            return
        self.step += 1
        self.refresh()
        delay = int(1000 / self.speed.get())
        self.after_id = self.root.after(delay, self.tick)
 
    def stop_play(self):
        self.playing = False
        self.play_btn.configure(text="Play")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
 
 
def main():
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()