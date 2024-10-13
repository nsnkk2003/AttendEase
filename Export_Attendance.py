def export_attendance(section):
    attendance_data = list(db['attendance'].find({'section': section}))
    if not attendance_data:
        messagebox.showerror("Error", f"No attendance records found for section {section}.")
        return

    df = pd.DataFrame(attendance_data)
    file_name = f"attendance_{section}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    df.to_excel(file_name, index=False)
    messagebox.showinfo("Success", f"Attendance exported to {file_name}")
