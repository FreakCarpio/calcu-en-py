import tkinter as tk
from tkinter import messagebox
from sympy import symbols, Eq, dsolve, Function, lambdify, simplify
from sympy.parsing.sympy_parser import parse_expr
import numpy as np
import random
import time

class CalculadoraEcuaciones:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Ecuaciones Diferenciales")
        self.root.geometry("600x700")
        self.root.configure(bg="black")

        # Estilo de fuente y color 
        font_style = ("Courier New", 12, "bold")
        title_style = ("Courier New", 20, "bold")
        matrix_green = "#00FF00"

        # Título
        title_label = tk.Label(self.root, text="Ecuaciones Diferenciales",
                               font=title_style, fg=matrix_green, bg="black")
        title_label.pack(pady=10)

        # Campo de entrada de ecuación
        equation_label = tk.Label(self.root, text="Ingresa tu Ecuación Diferencial (Ej. dy/dx = ...):",
                                  font=font_style, fg=matrix_green, bg="black")
        equation_label.pack(pady=5)

        self.input_equation_field = tk.Entry(self.root, font=font_style, fg=matrix_green, bg="black", insertbackground=matrix_green)
        self.input_equation_field.pack(pady=5, ipadx=50)

        # Campo de valor inicial
        initial_label = tk.Label(self.root, text="Condición Inicial (Ej. y(0)=1):",
                                 font=font_style, fg=matrix_green, bg="black")
        initial_label.pack(pady=5)

        self.initial_value_field = tk.Entry(self.root, font=font_style, fg=matrix_green, bg="black", insertbackground=matrix_green)
        self.initial_value_field.pack(pady=5, ipadx=50)

        # Botón para resolver
        solve_button = tk.Button(self.root, text="Resolver y Graficar", font=font_style, fg="black", bg=matrix_green,
                                 command=self.solve_and_plot, activebackground="#004400", activeforeground="white")
        solve_button.pack(pady=20)
        solve_button.bind("<Enter>", lambda e: solve_button.config(bg="#004400"))
        solve_button.bind("<Leave>", lambda e: solve_button.config(bg=matrix_green))

        # Botón de instrucciones con animación
        instructions_button = tk.Button(self.root, text="Instrucciones", font=font_style, fg="black", bg=matrix_green,
                                        command=self.show_instructions, activebackground="#004400", activeforeground="white")
        instructions_button.pack(pady=10)
        instructions_button.bind("<Enter>", lambda e: instructions_button.config(bg="#004400"))
        instructions_button.bind("<Leave>", lambda e: instructions_button.config(bg=matrix_green))

        # Botón para limpiar los campos
        clear_button = tk.Button(self.root, text="Limpiar", font=font_style, fg="black", bg=matrix_green,
                                 command=self.clear_fields, activebackground="#004400", activeforeground="white")
        clear_button.pack(pady=10)
        clear_button.bind("<Enter>", lambda e: clear_button.config(bg="#004400"))
        clear_button.bind("<Leave>", lambda e: clear_button.config(bg=matrix_green))

        # Área para mostrar resultados
        self.result_area = tk.Text(self.root, font=font_style, height=6, width=60, wrap="word", fg=matrix_green, bg="black", insertbackground=matrix_green)
        self.result_area.pack(pady=5)

        # Gráfica y animación Matrix
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="black")
        self.canvas.pack(pady=10)

        self.is_matrix_running = False

    def show_instructions(self):
        """Muestra un cuadro con las instrucciones de uso."""
        instrucciones = (
            "Instrucciones de Uso:\n"
            "1. Para ingresar una EDO, usa la notación estándar.\n"
            "   Ejemplo: dy/dx = x*y + x^2\n"
            "   - Utiliza 'dy/dx' para la derivada.\n"
            "   - Usa '^' para potencias (Ej. x^2 para x al cuadrado).\n"
            "2. Para ingresar condiciones iniciales, usa el formato:\n"
            "   y(x0) = y0\n"
            "   Ejemplo: y(0) = 1\n"
            "3. Si no proporcionas una condición inicial,\n"
            "   se resolverá la solución general.\n"
            "4. Presiona 'Resolver y Graficar' para obtener la solución.\n"
            "5. La solución general y particular (si aplica) se mostrarán,\n"
            "   y la gráfica de la solución se generará automáticamente."
        )
        messagebox.showinfo("Instrucciones", instrucciones)

    def solve_and_plot(self):
        x = symbols('x')
        y = Function('y')(x)

        equation_text = self.input_equation_field.get().replace('^', '**')
        initial_value_text = self.initial_value_field.get()

        try:
            equation = Eq(y.diff(x), parse_expr(equation_text))
            solution = dsolve(equation, y)

            if initial_value_text:
                initial_point = initial_value_text.replace("y(", "").replace(")", "").split("=")
                x0 = float(initial_point[0])
                y0 = float(initial_point[1])
                solution_with_init = dsolve(equation, y, ics={y.subs(x, x0): y0})
            else:
                solution_with_init = solution

            solution_str = f"Solución general: {self.format_expression(solution)}\n"
            if initial_value_text:
                solution_str += f"Solución con condición inicial: {self.format_expression(solution_with_init)}"

            self.result_area.delete(1.0, tk.END)
            self.display_with_buffering(solution_str)

            self.run_matrix_animation()
            self.root.after(2000, lambda: self.stop_matrix_and_plot(solution_with_init, x))

        except Exception as ex:
            messagebox.showerror("Error", f"Error al resolver la ecuación: {str(ex)}")

    def format_expression(self, solution):
        expr_str = str(solution.rhs).replace("**2", "²").replace("**3", "³")
        return f"y(x) = {expr_str}"

    def display_with_buffering(self, text, delay=50):
        for char in text:
            self.result_area.insert(tk.END, char)
            self.result_area.update()
            time.sleep(delay / 1000.0)

    def run_matrix_animation(self):
        self.is_matrix_running = True
        self.matrix_drops = [0 for _ in range(60)]
        self.update_matrix()

    def update_matrix(self):
        if not self.is_matrix_running:
            return

        self.canvas.delete("all")
        for i in range(len(self.matrix_drops)):
            text = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.canvas.create_text(i*10, self.matrix_drops[i]*10, text=text, fill="#00FF00", font=("Courier New", 12, "bold"))
            if self.matrix_drops[i] * 10 < 400 and random.random() > 0.1:
                self.matrix_drops[i] += 1
            else:
                self.matrix_drops[i] = 0
        self.root.after(50, self.update_matrix)

    def stop_matrix_and_plot(self, solution, x):
        self.is_matrix_running = False
        self.plot_solution(solution, x)

    def plot_solution(self, solution, x):
        try:
            solution_func = simplify(solution.rhs)
            arbitrary_constants = solution_func.free_symbols - {x}
            for constant in arbitrary_constants:
                solution_func = solution_func.subs(constant, 1)
            f_lambdified = lambdify(x, solution_func, modules=["numpy"])

            x_vals = np.linspace(-10, 10, 400)
            y_vals = np.array([float(f_lambdified(val)) if np.isreal(f_lambdified(val)) else np.nan for val in x_vals])

            self.canvas.delete("all")
            width, height = 600, 400
            x_center, y_center = width // 2, height // 2
            scale_x, scale_y = width // 20, height // 20

            self.canvas.create_line(0, y_center, width, y_center, fill="#00FF00")
            self.canvas.create_line(x_center, 0, x_center, height, fill="#00FF00")

            for i in range(1, len(x_vals)):
                if not (np.isnan(y_vals[i-1]) or np.isnan(y_vals[i])):
                    x1 = x_center + x_vals[i-1] * scale_x
                    y1 = y_center - y_vals[i-1] * scale_y
                    x2 = x_center + x_vals[i] * scale_x
                    y2 = y_center - y_vals[i] * scale_y
                    self.canvas.create_line(x1, y1, x2, y2, fill="#00FF00")

        except Exception as ex:
            messagebox.showerror("Error", f"Error al graficar la solución: {str(ex)}")

    def clear_fields(self):
        """Limpia los campos de la ecuación y la condición inicial."""
        self.input_equation_field.delete(0, tk.END)
        self.initial_value_field.delete(0, tk.END)
        self.result_area.delete(1.0, tk.END)
        self.canvas.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraEcuaciones(root)
    root.mainloop()