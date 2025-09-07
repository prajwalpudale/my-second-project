import cv2
import easyocr
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import os
import urllib.request

# Frame Width and Height
frameWidth = 1000
frameHeight = 480

# Cascade path
cascade_path = r"/Users/prajwal.pudalegmail.com/Desktop/untitled folder 2/PythonProject1/haarcascade_russian_plate_number.xml"
plateCascade = cv2.CascadeClassifier(cascade_path)

if plateCascade.empty():
    print("Error loading cascade file")
    exit()

# Define the minimum area for a detected plate
MIN_AREA = 500


# Function to preprocess and recognize license plate text
def recognize_plate(cropped_plate):
    # Configure urllib to use certifi's certificate bundle
    https_handler = urllib.request.HTTPSHandler()
    opener = urllib.request.build_opener(https_handler)
    urllib.request.install_opener(opener)

    # Initialize EasyOCR Reader without additional options
    reader = easyocr.Reader(['en'], gpu=False)

    # Read text from the plate
    results = reader.readtext(cropped_plate)

    # Extract the license plate number
    if results:
        return results[0][-2]
    return None


class LicensePlateDetectorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("License Plate Detector")
        self.root.geometry("1200x700")

        # Variables
        self.is_running = False
        self.capture_thread = None
        self.saved_plates = []
        self.current_plate = None
        self.count = 0

        # Create main frames
        self.create_frames()
        self.create_controls()
        self.create_display_area()
        self.create_saved_plates_list()

        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Action.TButton', padding=10, font=('Arial', 10, 'bold'))

    def create_frames(self):
        # Control panel on the left
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Main display area in the center
        self.display_frame = ttk.Frame(self.root, padding="10")
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Saved plates list on the right
        self.list_frame = ttk.Frame(self.root, padding="10")
        self.list_frame.pack(side=tk.RIGHT, fill=tk.Y)

    def create_controls(self):
        # Start/Stop button
        self.toggle_button = ttk.Button(
            self.control_frame,
            text="Start Detection",
            style='Action.TButton',
            command=self.toggle_detection
        )
        self.toggle_button.pack(pady=5, fill=tk.X)

        # Save plate button
        self.save_button = ttk.Button(
            self.control_frame,
            text="Save Plate (s)",
            style='Action.TButton',
            state=tk.DISABLED,
            command=self.save_plate
        )
        self.save_button.pack(pady=5, fill=tk.X)

        # Export button
        self.export_button = ttk.Button(
            self.control_frame,
            text="Export Plates",
            style='Action.TButton',
            command=self.export_plates
        )
        self.export_button.pack(pady=5, fill=tk.X)

        # Exit button
        self.exit_button = ttk.Button(
            self.control_frame,
            text="Exit",
            style='Action.TButton',
            command=self.exit_application
        )
        self.exit_button.pack(pady=5, fill=tk.X)

        # Status label
        self.status_label = ttk.Label(
            self.control_frame,
            text="Status: Stopped",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=20)

    def create_display_area(self):
        # Main video feed display
        self.video_label = ttk.Label(self.display_frame)
        self.video_label.pack(pady=10)

        # Current plate display
        self.plate_label = ttk.Label(self.display_frame, text="Detected Plate: None", font=('Arial', 12))
        self.plate_label.pack(pady=5)

    def create_saved_plates_list(self):
        # Title for saved plates
        ttk.Label(self.list_frame, text="Saved Plates", font=('Arial', 12, 'bold')).pack()

        # Listbox for saved plates
        self.plates_listbox = tk.Listbox(
            self.list_frame,
            width=30,
            height=20,
            font=('Arial', 10)
        )
        self.plates_listbox.pack(pady=5)

    def toggle_detection(self):
        if not self.is_running:
            self.is_running = True
            self.toggle_button.configure(text="Stop Detection")
            self.save_button.configure(state=tk.NORMAL)
            self.status_label.configure(text="Status: Running")
            self.capture_thread = threading.Thread(target=self.run_detection)
            self.capture_thread.daemon = True
            self.capture_thread.start()
        else:
            self.is_running = False
            self.toggle_button.configure(text="Start Detection")
            self.save_button.configure(state=tk.DISABLED)
            self.status_label.configure(text="Status: Stopped")

    def run_detection(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, frameWidth)
        cap.set(4, frameHeight)
        cap.set(10, 150)

        while self.is_running:
            success, frame = cap.read()
            if not success:
                messagebox.showerror("Error", "Failed to capture frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            plates = plateCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            detected_plate = None
            for (x, y, w, h) in plates:
                area = w * h
                if area > MIN_AREA:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    roi = frame[y:y + h, x:x + w]
                    plate_number = recognize_plate(roi)

                    if plate_number:
                        detected_plate = {
                            'number': plate_number,
                            'roi': roi
                        }
                        cv2.putText(frame, plate_number, (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            self.current_plate = detected_plate
            if detected_plate:
                self.root.after(0, lambda p=detected_plate:
                self.plate_label.configure(text=f"Detected Plate: {p['number']}"))

            # Convert frame to PhotoImage and update display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((800, 400))
            photo = ImageTk.PhotoImage(image=img)
            self.root.after(0, lambda p=photo: self.video_label.configure(image=p))
            self.video_label.image = photo

        cap.release()

    def save_plate(self):
        if self.current_plate:
            plate_text = self.current_plate['number']
            self.saved_plates.append({
                'plate': plate_text,
                'roi': self.current_plate['roi']
            })
            self.plates_listbox.insert(tk.END, plate_text)

            # Save plate image
            os.makedirs("./IMAGES", exist_ok=True)
            cv2.imwrite(f"./IMAGES/plate_{self.count}.jpg", self.current_plate['roi'])
            self.count += 1

            messagebox.showinfo("Success", f"Plate {plate_text} saved!")

    def export_plates(self):
        if not self.saved_plates:
            messagebox.showwarning("Warning", "No plates saved yet!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                for plate in self.saved_plates:
                    f.write(f"{plate['plate']}\n")
            messagebox.showinfo("Export", f"Plates exported to {file_path}")

    def exit_application(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.is_running = False
            self.root.quit()


# Create and run the UI
if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateDetectorUI(root)
    root.mainloop()
