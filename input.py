import os
import main
import json
import pandas as pd

def read_txt_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

def save_results_to_json(results, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

        
        
def process_xlsx(file_path):
    xls = pd.ExcelFile(file_path)
    return_shift = {}
    return_task = {}
    df_first = pd.read_excel(xls, sheet_name=xls.sheet_names[0], dtype=str)
    return_shift = [
        {
            'start_time': row['start_time'][:5],
            'end_time': row['end_time'][:5],
            'break_time': row['break_time'][:5],
            'break_duration': int(row['break_duration']),
            'cost': float(row['cost']),
            'days': row['days']
        }
        for _, row in df_first.iterrows()
    ]

    for i in range(1, len(xls.sheet_names)):
        df = pd.read_excel(xls, sheet_name=xls.sheet_names[i], dtype=str)
        return_task[str(i-1)] = [
            {
                'start_time': row['start_time'][:5],
                'end_time': row['end_time'][:5],
                'duration': row['duration'][:5],
                'nurses_required': int(row['nurses_required'])
            }
            for _, row in df.iterrows()
        ]

    return return_shift,return_task

def main_process_pipeline():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'random_generate_sheet_dataframe.xlsx')
    result_file_path = os.path.join(current_dir, 'results.json')
    
    shift,task = process_xlsx(input_file)
    
    result = main.main_process(task, shift)
    
    save_results_to_json(result, result_file_path)
    print("reslut save in:", result_file_path)

if __name__ == "__main__":
    main_process_pipeline()
