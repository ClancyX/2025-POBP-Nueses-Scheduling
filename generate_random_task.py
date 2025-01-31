import random
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

global end_of_day,start_time,end_time
random.seed(2024)
start_time = datetime(2025, 1, 16, 0, 0)
end_time = datetime(2025, 1, 16, 23, 0)

end_of_day = datetime.strptime("23:59", "%H:%M")

def random_time(start, end):
    fmt = "%H:%M"
    start_dt = datetime.strptime(start, fmt)
    #print(start_dt)
    end_dt = datetime.strptime(end, fmt)
    #print(end_dt)
    delta = end_dt - start_dt
    random_seconds = random.randint(0, int(delta.total_seconds()) // 900) * 900
    random_dt = start_dt + timedelta(seconds=random_seconds)
    return random_dt.strftime(fmt)

def generate_scheduled_tasks(n):
    tasks = []
    for _ in range(n):
        start_window_start = random_time("00:00", "23:00")
        time_left = end_of_day - datetime.strptime(start_window_start, '%H:%M')
        
        time_slots = int(time_left.total_seconds() // 900) - 1
        if time_slots < 1:
            time_slots = 1 
        #print(time_left)
        duration = random.randint(1, int(((time_left.total_seconds() // 900)-1)))
        #print(duration)
        duration_hours,duration_mins = divmod(duration*15, 60)
        #print(duration_hours)
        time_after_duration = datetime.strptime(start_window_start, "%H:%M") + timedelta(minutes=duration*15)
        #print(time_after_duration)
        start_window_end = random_time(time_after_duration.strftime("%H:%M"), "23:59")
        #print(start_window_end)
        #print('end')
        nurses_required = random.randint(1, 10)

        task = {
            "start_time": f"{start_window_start}",
            "end_time": f"{start_window_end}",
            "duration":f"{duration_hours:02d}:{duration_mins:02d}",
            "nurses_required": nurses_required,
        }
        tasks.append(task)
    return tasks


def main(length):

    
    # Generate tasks and shifts
    num_tasks = length
    num_shifts = 3
    scheduled_tasks = generate_scheduled_tasks(num_tasks)
    scheduled_shifts = [
    {'start_time': '00:00', 'end_time': '12:45', 'break_time': '11:30', 'break_duration': 30, 'cost': 116.19,'days':'1,2,3,4,5'},
    {'start_time': '08:45', 'end_time': '18:45', 'break_time': '09:00', 'break_duration': 30, 'cost': 327.08,'days':'1,2,3,4,5'},
    {'start_time': '16:00', 'end_time': '23:59', 'break_time': '18:00', 'break_duration': 30, 'cost': 437.58,'days':'1,2,3,4,5'},
    {'start_time': '00:00', 'end_time': '06:45', 'break_time': '06:00', 'break_duration': 30, 'cost': 219.00,'days':'0,6'},
    {'start_time': '06:00', 'end_time': '18:45', 'break_time': '15:00', 'break_duration': 30, 'cost': 327.08,'days':'0,6'},
    {'start_time': '15:00', 'end_time': '23:59', 'break_time': '18:00', 'break_duration': 30, 'cost': 355.58,'days':'0,6'}]

    week_list = []
    for i in range(7):
        scheduled_tasks = generate_scheduled_tasks(num_tasks)
        week_list.append(scheduled_tasks)

    df1 = pd.DataFrame(scheduled_shifts)

    df2 = pd.DataFrame(week_list[0])
    df3 = pd.DataFrame(week_list[1])
    df4 = pd.DataFrame(week_list[2])
    df5 = pd.DataFrame(week_list[3])
    df6 = pd.DataFrame(week_list[4])
    df7 = pd.DataFrame(week_list[5])
    df8 = pd.DataFrame(week_list[6])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, 'random_generate_sheet_dataframe.xlsx')

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='shift', index=False)
        df2.to_excel(writer, sheet_name='0', index=False)
        df3.to_excel(writer, sheet_name='1', index=False)
        df4.to_excel(writer, sheet_name='2', index=False)
        df5.to_excel(writer, sheet_name='3', index=False)
        df6.to_excel(writer, sheet_name='4', index=False)
        df7.to_excel(writer, sheet_name='5', index=False)
        df8.to_excel(writer, sheet_name='6', index=False)

    print(f"successful generate new schedule as：{output_file}")

if __name__ == "__main__":
        length = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        main(length)
    
    
    
    
    
    
    
    