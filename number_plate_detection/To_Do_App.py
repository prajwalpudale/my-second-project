import requests
import tkinter as tk
from tkinter import messagebox


def get_exchange_rate(base_currency, target_currency):
    api_url = f"https://open.er-api.com/v6/latest/{base_currency}"
    response = requests.get(api_url)
    data = response.json()

    if response.status_code != 200 or "error" in data:
        messagebox.showerror("Error", "Error fetching exchange rates.")
        return None

    return data["rates"].get(target_currency, None)


def convert_currency():
    base_currency = base_currency_entry.get().upper()
    target_currency = target_currency_entry.get().upper()

    try:
        amount = float(amount_entry.get())
        rate = get_exchange_rate(base_currency, target_currency)
        if rate is None:
            messagebox.showerror("Error", "Invalid currency code or unavailable exchange rate.")
            return
        converted_amount = amount * rate
        result_label.config(text=f"{amount} {base_currency} = {converted_amount:.2f} {target_currency}")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered.")


# Tkinter GUI setup
root = tk.Tk()
root.title("Currency Converter")
root.geometry("400x300")

tk.Label(root, text="Base Currency:").pack()
base_currency_entry = tk.Entry(root)
base_currency_entry.pack()

tk.Label(root, text="Target Currency:").pack()
target_currency_entry = tk.Entry(root)
target_currency_entry.pack()

tk.Label(root, text="Amount:").pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

tk.Button(root, text="Convert", command=convert_currency).pack()

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()

