import os
import re
import ast
import pandas as pd
import pulp as plp
import json
from datetime import datetime, timedelta

global scheduled_shifts,scheduled_tasks,scheduled_nurses

def set_time_interval_tasks_to_time_units(data, duration_task):
    time_units = []
    index_task = 0
    for key, item in data.items():
        day = int(key[-1])
        for task in item:
            start_hours, start_minutes = map(int, task['start_time'].split(':'))
            start_time_unit = int(day*4*24+start_hours*4+start_minutes/15)
            end_hours, end_minutes = map(int, task['end_time'].split(':'))
            end_time_unit = int(day*4*24+end_hours*4+end_minutes/15)
            end_time_unit = min((day+1)*4*24, end_time_unit + duration_task[index_task])
            time_units.append(range(start_time_unit,end_time_unit))
            index_task += 1
    return time_units

def set_time_interval_shifts_to_time_units(data):
    global scheduled_shifts,scheduled_tasks
    time_units = []
    #data = scheduled_shifts
    for row in data:
        time_interval_per_shift = []
        #print(data)
        for day in row['days'].split(','):
            day = int(day)
            start_hours, start_minutes = map(int, row['start_time'].split(':'))
            start_time_unit = int(day*4*24+start_hours*4+start_minutes/15)

            end_hours, end_minutes = map(int, row['end_time'].split(':'))
            end_time_unit = int(day*4*24+end_hours*4+end_minutes/15)

            if ',' in scheduled_shifts[0]['break_time']:
                break_time_units = []
                for time in row['break_time'].split(','):
                    break_hours, break_minutes = map(int, time.split(':'))
                    break_time_unit = int(day*4*24+break_hours*4+break_minutes/15)
                    for t in range(break_time_unit,break_time_unit+int(row['break_duration']/15)):
                        break_time_units.append(t)
            else:
                break_hours, break_minutes = map(int, row['break_time'].split(':'))
                break_time_unit = int(day*4*24+break_hours*4+break_minutes/15)
                break_time_units = range(break_time_unit,break_time_unit+int(row['break_duration']/15))

            for t in range(start_time_unit,end_time_unit):
                if t not in break_time_units:
                    time_interval_per_shift.append(t)

        time_units.append(time_interval_per_shift)
    return time_units

def set_duration_to_time_units(data):
    time_units = []
    for key, items in data.items():
        for task in items:
            hours, minutes = map(int, task['duration'].split(':'))
            time_units.append(int(hours*4+minutes/15))
    return time_units

def take_nurse(time_unit,number_of_needed_nurses):
    global scheduled_nurses
    result = []
    for key, item in scheduled_nurses[time_unit].items():
        if item > 0:
            taken_nurses = (min(item,number_of_needed_nurses))
            nurses_left = item - taken_nurses
            scheduled_nurses[time_unit][key] = nurses_left
            for i in range(int(taken_nurses)):
                    result.append(key)
            if taken_nurses == number_of_needed_nurses:
                return result
            else:
                number_of_needed_nurses -= taken_nurses





def main_process(input_tasks,input_scheduled_shifts):
    global scheduled_shifts,scheduled_tasks
    scheduled_shifts = input_scheduled_shifts
    scheduled_tasks = input_tasks
    set_I = range(len(scheduled_shifts))
    set_J = range(sum(len(value) for value in scheduled_tasks.values()))
    set_T = range(len(scheduled_tasks.keys())*4*24)
    set_L = set_time_interval_shifts_to_time_units(scheduled_shifts)
    set_L_binary = {}
    for i in set_I:
        set_L_i = []
        for t in set_T:
            if t in set_L[i]:
                set_L_i.append(1)
            else:
                set_L_i.append(0)
        set_L_binary[i] = set_L_i
    set_L = set_L_binary

    #Constants
    N = [] #The number of nurses required for job every j
    for key, items in scheduled_tasks.items():
        for task in items:
            N.append(task['nurses_required'])
    D = set_duration_to_time_units(scheduled_tasks) #The number of time units required for every job j
    C = [scheduled_shifts[shift]['cost'] for shift in set_I] #Costs for every shift

    set_K = set_time_interval_tasks_to_time_units(scheduled_tasks,D)
    


    opt_model = plp.LpProblem(name='MIP_Model')

    #Decision variables
    #Decide the starting time of task j
    x_vars  = {(j,t):
                plp.LpVariable(cat='Binary', lowBound=0, name="x_{0}_{1}".format(j,t)) 
                for j in set_J for t in set_T}

    #Decide the number of shifts i that are going to be scheduled
    y_vars = {i:
            plp.LpVariable(cat=plp.LpInteger, lowBound=0, name="y_{0}".format(i)) 
            for i in set_I}

    #Constraints

    #Each seperate task must have a starting time in it's time interval
    constraints = {(j) : opt_model.addConstraint(
        plp.LpConstraint(
            e=plp.lpSum(x_vars[j, t] for t in range(set_K[j][0],set_K[j][-1]-D[j]+2)),
            sense=plp.LpConstraintEQ,
            rhs=1,
            name="constraint1_{0}".format(j)))
        for j in set_J}

    #A task can't start when it's outside it's time interval
    constraints = {(j): opt_model.addConstraint(
        plp.LpConstraint(
            e=plp.lpSum(x_vars[j, t] for t in set_T if t not in range(set_K[j][0],set_K[j][-1]-D[j]+2)),
            sense=plp.LpConstraintEQ,
            rhs=0,
            name="constraint2_{0}".format(j)))
        for j in set_J}

    #For every time unit there must be enough nurses to handle all the tasks
    constraints = {(t): opt_model.addConstraint(
        plp.LpConstraint(
            e=plp.lpSum(y_vars[i]*set_L[i][t] for i in set_I)-plp.lpSum(N[j]*x_vars[j, k] for j in set_J for k in range(max(0,t-D[j]+1),t+1)),
            sense=plp.LpConstraintGE,
            rhs=0,
            name="constraint3_{0}".format(t)))
        for t in set_T}

    #Objective function
    objective = plp.lpSum(y_vars[i]*C[i] for i in set_I)
    opt_model.sense = plp.LpMinimize
    opt_model.setObjective(objective)

    #Solve LP Model
    opt_model.solve()
            
    global scheduled_nurses


    scheduled_nurses = []
    amount_of_scheduled_nurses = {}
    for v in opt_model.variables():
        if v.name[0] == 'y':
            amount_of_scheduled_nurses[int(v.name.split('_')[1])] = v.varValue
            
    scheduled_nurses = []
    for t in set_T:
        nurses = {}
        for shift, item in amount_of_scheduled_nurses.items():
            nurses[shift] = set_L_binary[shift][t]*item
        scheduled_nurses.append(nurses)
        
    starting_times_tasks = []
    for v in opt_model.variables():
        if v.name[0] == 'x' and v.varValue > 0:
            starting_times_tasks.append(v.name.split('_'))
            
    tasks_indexes = []
    for key, item in scheduled_tasks.items():
        index = 0
        for task in item:
            tasks_indexes.append(index)
            index+=1
            
    result = {}
    for key in scheduled_tasks.keys():
        result[int(key[-1])] = {}
        
    for row in starting_times_tasks:
        task = int(row[1])
        task_index = tasks_indexes[task]
        time = int(row[2])
        day = int(time/96)
        time_interval_task = [t for t in range(time - day*96,time + D[task] - day*96)]
        nurses = []
        for t in range(time,time+D[task]):
            nurses.append(take_nurse(t,N[task]))
        result[day][task_index] = [time_interval_task,nurses]
    return result,plp.value(opt_model.objective)