import customtkinter as ctk
from parser import parse_sql
from generator import generate_pandas_code

ctk.set_appearance_mode("dark")

def launch_gui():
    app = ctk.CTk()
    app.title("SQL ⮕ Pandas Translator")
    app.geometry("1100x850")

    frame = ctk.CTkFrame(app)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    title = ctk.CTkLabel(frame, text="SQL ⮕ PANDAS", font=("Consolas", 28, "bold"), text_color="#4cc9f0")
    title.pack(pady=10)

    sql_input = ctk.CTkTextbox(frame, height=250, font=("Consolas", 14))
    sql_input.pack(fill="x", padx=20)

    # Lógica de colores neón para SQL
    def highlight_sql(event=None):
        keywords = ["SELECT", "FROM", "WHERE", "JOIN", "ON", "GROUP BY", "ORDER BY", "DESC", "ASC", "TOP", "LIMIT", "AS", "AND", "OR", "COUNT", "SUM", "AVG", "MIN", "MAX"]
        for kw in keywords:
            start = "1.0"
            while True:
                start = sql_input.search(kw, start, stopindex="end", nocase=True)
                if not start: break
                end = f"{start}+{len(kw)}c"
                sql_input.tag_add(kw, start, end)
                sql_input.tag_config(kw, foreground="#50fa7b") # VERDE NEÓN
                start = end

    sql_input.bind("<KeyRelease>", highlight_sql)

    def translate():
        query = sql_input.get("1.0", "end").strip()
        output_box.configure(state="normal")
        output_box.delete("1.0", "end")
        try:
            parsed = parse_sql(query)
            code = generate_pandas_code(parsed)
            output_box.insert("end", code)
        except Exception as e:
            output_box.insert("end", f"Error: {str(e)}")
        output_box.configure(state="disabled")

    def clear():
        sql_input.delete("1.0", "end")
        output_box.configure(state="normal")
        output_box.delete("1.0", "end")
        output_box.configure(state="disabled")

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(pady=10)

    ctk.CTkButton(btn_frame, text="TRANSLATE", command=translate, fg_color="#7209b7", width=180).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="CLEAR", command=clear, fg_color="#f72585", width=90).pack(side="left", padx=10)

    output_box = ctk.CTkTextbox(frame, height=350, font=("Consolas", 14), text_color="#4cc9f0") # AZUL CIAN
    output_box.pack(fill="both", expand=True, padx=20, pady=10)
    output_box.configure(state="disabled")

    app.mainloop()

if __name__ == "__main__":
    launch_gui()