import pyautogui
import tkinter as tk
from tkinter import Toplevel
import threading
from datetime import timedelta
import time

class OverlayWindow:
    def __init__(self, root):
        self.delayscan = 30 #s
        self.delayclose = 20000 #ms
        self.root = root
        self.created_overlay = False
        self.remaining_time = None
        self.is_active = False

        self.status_label = tk.Label(root, text="OFF", bg="red", fg="white")
        self.status_label.pack(pady=10)
        self.activity_button = tk.Button(root, text="Bắt đầu", command=self.toggle_activity)
        self.activity_button.pack(pady=5)
        self.timer_label = tk.Label(root, text="Time delay scan: "+ str(self.delayscan) +" second", fg="white",bg="black")
        self.timer_label.pack(pady=5)

    def create_overlay_window(self, coordinates):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        overlay_width = screen_width // 2  # Set the overlay to one-third of the screen's width
        overlay_height = screen_height
        overlay_left = screen_width // 2   # Place the window to the right two-thirds of the screen
        overlay_top = 0

        overlay_window = Toplevel(self.root)
        overlay_window.overrideredirect(1)  # Remove window decorations
        overlay_window.attributes('-topmost', True)  # Hiển thị cửa sổ trên cùng
        overlay_window.geometry(f"{overlay_width}x{overlay_height}+{overlay_left}+{overlay_top}")

        self.text = tk.Label(overlay_window, text="", fg="red", bg="white")
        self.text.pack(fill="both", expand=True)
        self.root.after(self.delayclose, lambda: self.close_overlay(overlay_window))

    #def focus_overlay(self):
    #    pyautogui.moveTo(self.overlay_x, self.overlay_y)
    #    pyautogui.click()
    def close_overlay(self, overlay_window):
        overlay_window.destroy()

    def switch_to_overlay_window(self):
        pyautogui.hotkey('alt', 'tab')

    def toggle_activity(self):
        if self.is_active:
            self.is_active = False
            self.status_label.config(text="OFF", bg="red", fg="white")
            self.activity_button.config(text="Bắt đầu")
            self.timer_label.config(text="Stoped")
        else:
            self.timer_label.config(text="Scanning...")
            self.is_active = True
            self.status_label.config(text="ON", bg="green", fg="white")
            self.activity_button.config(text="Dừng lại")
            # Sử dụng threading để chạy hoạt động trong một luồng riêng
            activity_thread = threading.Thread(target=self.run_activity)
            activity_thread.start()

    def run_activity(self):
        while self.is_active:
            try:
                msgbox = pyautogui.locateOnScreen('msgbox.png')
            except Exception as e:
                print(f"An error occurred: {e}")
                msgbox = None
            if msgbox is not None and not self.created_overlay:
                print("Found")
                print(msgbox)
                self.create_overlay_window(msgbox)
                self.switch_to_overlay_window()  # Switch to the overlay window
                self.created_overlay = True  # Đánh dấu đã tạo overlay
                self.remaining_time = timedelta(seconds=self.delayclose/1000)
                self.update_timer_label()  # Bắt đầu đếm ngược
                for i in range(self.delayscan, 0, -1):
                    self.timer_label.config(text=f"{i}")
                    self.root.update()  # Cập nhật giao diện
                    time.sleep(1)  # Đợi 1 giây
                self.timer_label.config(text="Scaning...")
            elif msgbox is None and self.created_overlay:
                self.created_overlay = False  # Đánh dấu overlay đã đóng

    def update_timer_label(self):
        try:
            if self.remaining_time:
                timer_text = f"Remaining Time: {self.remaining_time}"
                self.text.config(text=f"ĐANG KIỂM TRA CHỨC NĂNG \n \n{timer_text}", font=("Arial", 25, "bold"))
                if self.remaining_time.total_seconds() > 0:
                    self.remaining_time -= timedelta(seconds=1)
                    self.root.after(1000, self.update_timer_label)
        except:
            self.text.config(text="An error occurred in updating the label.", font=("Arial", 12, "normal"))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("200x120")
    root.attributes('-topmost', True)
    root.title("CEV Support SpecReport")
    overlay_window = OverlayWindow(root)
    root.mainloop()
