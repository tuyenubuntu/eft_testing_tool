import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageTk

# --- Các đường dẫn file ---
ELEMENT_TYPE_FILE = r"\\10.194.54.84\lth_production_data$\10.EAC\Test data\03. EFT\Element type.txt"
MASTERLIST_FILE = r"\\10.194.54.84\lth_production_data$\10.EAC\Test data\03. EFT\EFT test masterlist.txt"
EMPLOYEE_FILE = r"\\10.194.54.84\lth_production_data$\10.EAC\Test data\03. EFT\Employee list.txt"
METHOD_FILE = r"\\10.194.54.84\lth_production_data$\10.EAC\Test data\03. EFT\testing method.txt"
SETTING_FILE = r"\\10.194.54.84\lth_production_data$\10.EAC\Test data\03. EFT\setting.txt"
FORCE_MAPPING_FILE = r"\\10.194.54.84\lth_production_data$\10.EAC\Test data\03. EFT\force setting by method.txt"
BASE_FOLDER = os.path.join(r"C:\Rumul data\Testing data on V3", str(datetime.now().year))

# --- Hàm hỗ trợ ---
def load_list_from_file(path):
    try:
        with open(path, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except:
        return []

def get_force_from_element_type(element_type):
    if element_type.startswith("24"):
        return "300"
    return "400"

def get_force_from_method(method):
    try:
        with open(FORCE_MAPPING_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2 and parts[0] == method:
                    return parts[1]
    except:
        pass
    return ""

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False

def save_to_masterlist(order, element_type, element_number, employee, method):
    with open(MASTERLIST_FILE, 'a') as f:
        f.write(f"{order}\t{element_type}\t{element_number}\t{employee}\t{method}\n")

def get_latest_element_number(folder):
    numbers = []
    if not os.path.exists(folder):
        return 0
    for file in os.listdir(folder):
        if file.endswith(".woe"):
            try:
                number = int(os.path.splitext(file)[0])
                numbers.append(number)
            except:
                continue
    return max(numbers) if numbers else 0

def get_cycles_from_woe(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if lines:
                return lines[-1].split()[4]
    except:
        pass
    return ""

def get_force_from_woe(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if lines:
                offset = lines[-1].split()[2]
                return str(int(float(offset) * 1000)).zfill(3)
    except:
        pass
    return ""

import barcode
from barcode.writer import ImageWriter

def generate_barcode(data: str, filename: str = "barcode"):
    try:
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(data, writer=ImageWriter())
        full_filename = barcode_instance.save(filename)
        return full_filename
    except Exception as e:
        print(f"Lỗi tạo barcode: {e}")
        return None



def get_force_setting_from_file(method_name, setting_path):
    try:
        with open(setting_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == method_name:
                    return parts[1]
    except Exception as e:
        print(f"Lỗi đọc setting.txt: {e}")
    return ""

def cancel_app():
    root.destroy()

# --- Hàm xử lý nút bấm ---
def clear_fields():
    for key in ['test_order', 'force', 'cycles']:
        fields[key].delete(0, tk.END)
    for key in ['element_type', 'element_number', 'employee', 'method']:
        fields[key].set('')
    fields['force_setting'].config(state='normal')
    fields['force_setting'].delete(0, tk.END)
    fields['force_setting'].config(state='readonly')
    barcode_label.config(image='')

def create_test_order():
    order = fields['test_order'].get().strip().upper()
    fields['test_order'].delete(0, tk.END)
    fields['test_order'].insert(0, order)

    element_type = fields['element_type'].get()
    element_number = fields['element_number'].get()
    employee = fields['employee'].get()
    method = fields['method'].get()

    if not order or not element_type or not element_number or not employee or not method:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
        return

    save_to_masterlist(order, element_type, element_number, employee, method)
    year_folder = os.path.join(BASE_FOLDER, order)
    created = create_folder(year_folder)

    force_setting = get_force_setting_from_file(method, SETTING_FILE)

    if not force_setting:
        messagebox.showerror("Lỗi", "Không tìm thấy Force setting cho phương pháp này")
        return

    fields['force_setting'].config(state='normal')
    fields['force_setting'].delete(0, tk.END)
    fields['force_setting'].insert(0, force_setting)
    fields['force_setting'].config(state='readonly')

    force_value = get_force_from_element_type(element_type)
    fields['force'].delete(0, tk.END)
    fields['force'].insert(0, force_value)

    if not created:
        messagebox.showinfo("Thông báo", "Folder đã tồn tại")
    else:
        messagebox.showinfo("Thành công", "Đã tạo test order và folder")

def show_test_order():
    order = fields['test_order'].get().strip().upper()
    fields['test_order'].delete(0, tk.END)
    fields['test_order'].insert(0, order)

    if not order:
        messagebox.showerror("Lỗi", "Phải nhập test order")
        return

    if os.path.exists(MASTERLIST_FILE):
        with open(MASTERLIST_FILE, 'r') as f:
            for line in reversed(f.readlines()):
                parts = line.strip().split('\t')
                if parts[0] == order:
                    fields['element_type'].set(parts[1])
                    fields['employee'].set(parts[3] if len(parts) > 3 else '')
                    fields['method'].set(parts[4] if len(parts) > 4 else '')
                    method = parts[4] if len(parts) > 4 else ''
                    force_setting = get_force_setting_from_file(method, SETTING_FILE)
                    fields['force_setting'].config(state='normal')
                    fields['force_setting'].delete(0, tk.END)
                    fields['force_setting'].insert(0, force_setting)
                    fields['force_setting'].config(state='readonly')
                    break

    folder_path = os.path.join(BASE_FOLDER, order)

    current_number = fields['element_number'].get()
    if not current_number.isdigit():
        current_number = '1'
    fields['element_number'].set(current_number)

    current_woe = os.path.join(folder_path, f"{current_number}.woe")
    if os.path.exists(current_woe):
        force = get_force_from_woe(current_woe)
        fields['force'].delete(0, tk.END)
        fields['force'].insert(0, force)

        cycles = get_cycles_from_woe(current_woe)
        fields['cycles'].delete(0, tk.END)
        fields['cycles'].insert(0, cycles)

        barcode_file = generate_barcode(cycles)
        if barcode_file:
            img = Image.open(barcode_file)
            img = img.resize((200, 60))
            photo = ImageTk.PhotoImage(img)
            barcode_label.config(image=photo)
            barcode_label.image = photo
    else:
        fields['force'].delete(0, tk.END)
        fields['force'].insert(0, get_force_from_element_type(fields['element_type'].get()))
        fields['cycles'].delete(0, tk.END)
        barcode_label.config(image='')
        messagebox.showinfo("Thông báo", "Test chưa chạy xong")

def get_increase_step_from_setting(method_name, setting_path):
    try:
        with open(setting_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == method_name:
                    return int(parts[1])  # Lấy giá trị increase step từ cột thứ 2
    except Exception as e:
        print(f"Lỗi đọc setting.txt: {e}")
    return 0  # Trả về 0 nếu không tìm thấy giá trị

def next_test():
    try:
        order = fields['test_order'].get().strip().upper()
        if not order:
            messagebox.showerror("Lỗi", "Phải nhập test order trước")
            return

        # Lấy số thứ tự phần tử hiện tại
        element_number = int(fields['element_number'].get())

        folder_path = os.path.join(BASE_FOLDER, order)
        current_woe = os.path.join(folder_path, f"{element_number}.woe")

        if os.path.exists(current_woe):
            # Lấy cycles từ file .woe
            cycles = get_cycles_from_woe(current_woe)

            # Chuyển cycles thành số nguyên
            cycles = int(cycles) if cycles else 0

            # Cập nhật static nếu cần
            force = get_force_from_woe(current_woe)
            fields['force'].delete(0, tk.END)
            fields['force'].insert(0, force)

            # Nếu cycles >= 250000 thì tăng hoặc giảm giá trị static
            if cycles >= 250000:
                static_value = int(force) + 20
            else:
                static_value = int(force) - 20

            # Cập nhật force value
            fields['force'].delete(0, tk.END)
            fields['force'].insert(0, static_value)

            # Tăng số thứ tự phần tử lên 1
            fields['element_number'].set(str(element_number + 1))

        else:
            messagebox.showerror("Lỗi", f"File {element_number}.woe chưa chạy xong.")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


# --- Giao diện chính ---
root = tk.Tk()
root.title("EFT Visualize Form")
root.configure(bg='#002060')

fields = {}
labels = [
    "Test order /Charge no :", "Element type:", "Element Number:",
    "Force:", "Test cycles:", "Barcode:", "Create charge by:",
    "Testing method:", "Increase step:"
]

for i, text in enumerate(labels):
    tk.Label(root, text=text, bg='#002060', fg='white').grid(row=i, column=0, sticky='e', padx=5, pady=5)

fields['test_order'] = tk.Entry(root)
fields['element_type'] = ttk.Combobox(root, values=load_list_from_file(ELEMENT_TYPE_FILE), state="readonly")
fields['element_number'] = ttk.Combobox(root, values=[str(i) for i in range(1, 51)], state="readonly")
fields['force'] = tk.Entry(root)
fields['cycles'] = tk.Entry(root)
barcode_label = tk.Label(root)
fields['employee'] = ttk.Combobox(root, values=load_list_from_file(EMPLOYEE_FILE), state="readonly")
fields['method'] = ttk.Combobox(root, values=load_list_from_file(METHOD_FILE), state="readonly")
fields['force_setting'] = tk.Entry(root, state="readonly")

entries = [
    fields['test_order'], fields['element_type'], fields['element_number'],
    fields['force'], fields['cycles'], barcode_label,
    fields['employee'], fields['method'], fields['force_setting']
]

for i, widget in enumerate(entries):
    widget.grid(row=i, column=1, padx=5, pady=5)

# --- Bổ sung các nút bấm nếu cần thiết tại đây ---
# Các nút
buttons = [
    ("Clear", clear_fields, 'orange'),
    ("Show", show_test_order, 'green'),
    ("Next test", next_test, 'deepskyblue'),
    ("Create test order", create_test_order, 'lightgreen'),
    ("Cancel", cancel_app, 'red')
]

for i, (text, cmd, color) in enumerate(buttons):
    tk.Button(root, text=text, command=cmd, bg=color).grid(row=9, column=i, padx=5, pady=10)

root.mainloop()
# root.mainloop() phải để cuối cùng
# root.mainloop()
