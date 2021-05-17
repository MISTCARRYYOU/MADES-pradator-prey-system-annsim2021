import matplotlib.pyplot as plt
import numpy as np
from pylab import mpl
mpl.rcParams['font.size'] = 18


# 1 in plot list, the lefts are 0
# dot_list is [1,2,3,4,6,7], even number
def plot_square_wave(dots_list, y_track, name, color, aix_begin, aix_end, linestyle):
    if dots_list == []:
        plt.plot([aix_begin,aix_end], [y_track, y_track], color= color, linestyle=linestyle)
        return

    assert len(dots_list) % 2 == 0
    starts = []
    ends = []
    temp_dots_list = []
    for i, dot in enumerate(dots_list):
        if i % 2 == 0:
            starts.append(dot)
            temp_dots_list.append(dot)
        else:
            ends.append(dot+0.1)
            temp_dots_list.append(dot+0.1)
    # draw the |--| mountain
    for i in range(len(starts)):
        plt.plot([starts[i], ends[i]], [y_track+1, y_track+1], color=color, linestyle=linestyle)
        plt.plot([starts[i], starts[i]], [y_track, y_track+1], color=color, linestyle=linestyle)
        plt.plot([ends[i], ends[i]], [y_track, y_track+1], color=color, linestyle=linestyle)

    # draw the - - - -
    all_dots = [aix_begin]
    all_dots += sorted(list(set(temp_dots_list)))
    all_dots.append(aix_end)
    starts = []
    ends = []
    for i, dot in enumerate(all_dots):
        if i % 2 == 0:
            starts.append(dot)
        else:
            ends.append(dot)
    for i in range(len(starts)):
        plt.plot([starts[i], ends[i]], [y_track, y_track], color=color, linestyle=linestyle)

# 将log str 中的某个原子模型的内部或者外部事件的起始点提取出来，返回其起始点与终止点
def extract_dots(is_external, extract_name, time_sequence_str, timeadvance, is_divide3):
    if is_external:
        extract_str = "EXTERNAL"
    else:
        extract_str = "INTERNAL"
    time_record = []
    y_dots = []
    for i, eve in enumerate(time_sequence_str):
        if type(eve) == float:
            time_record.append(i)
    part_4_time = [[] for eve in time_record]

    for index, i in enumerate(time_record):
        if index != len(time_record)-1:
            part_4_time[index] += (time_sequence_str[i+1:time_record[index+1]])
        else:
            part_4_time[index] += (time_sequence_str[i + 1:])

    assert len(part_4_time) == len(time_record)
    time = []
    for eve in time_record:
        time.append(time_sequence_str[eve])

    for i in range(len(time)):
        for eve in part_4_time[i]:
            if extract_str in eve and extract_name in eve:
                y_dots.append(time[i])

    start_end_dots = []
    for i,eve in enumerate(y_dots):
        if is_divide3:  # 代表需要除三，因为三个agent
            if i % 3 == 0:
                start_end_dots.append(eve)
                start_end_dots.append(eve + 0.2 + timeadvance)
        else:
            start_end_dots.append(eve)
            start_end_dots.append(eve + 0.2 + timeadvance)

    return start_end_dots


if __name__ == "__main__":
    # 直接统计每个时刻发生的事件列表先
    plt.figure(figsize=(20, 10))
    with open(r"../DrawFigures/one)step_train_devs_log.txt", "r") as file:
        content = [eve.strip("\n").strip("\t") for eve in file]
    res = []
    for eve in content:
        if eve != "":
            if "Current Time" in eve or "EXTERNAL TRANSITION" in eve or "INTERNAL TRANSITION" in eve:
                res.append(eve)
    pure_time = []

    for eve in res:
        if "Current Time" in eve:
            temp = eve.split(":")[-1].strip().split(" ")[0]
            pure_time.append(float(temp))
        else:
            pure_time.append(eve)
    # 此时 pure_time 为[860.9, 'EXTERNAL TRANSITION in model <Simulation.predator-controller>', 'EXTERNAL TRANSITION in model <Simulation.predator-schedule>'。。。
    prey_plan1_ex_dots = [round(eve-860.9, 2) for eve in extract_dots(True, "prey-plan1", pure_time, 0, False)]
    prey_plan1_in_dots = [round(eve-860.9, 2) for eve in extract_dots(False, "prey-plan1", pure_time, 0, False)]

    prey_plan2_ex_dots = [round(eve - 860.9, 2) for eve in extract_dots(True, "prey-plan2", pure_time, 0, False)]
    prey_plan2_in_dots = [round(eve - 860.9, 2) for eve in extract_dots(False, "prey-plan2", pure_time, 0, False)]

    prey_goal_ex_dots = [round(eve - 860.9, 2) for eve in extract_dots(True, "prey-goal", pure_time, 1, False)]
    prey_goal_in_dots = [round(eve - 860.9, 2) for eve in extract_dots(False, "prey-goal", pure_time, 1, False)]

    prey_schedule_ex_dots = [round(eve - 860.9, 2) for eve in extract_dots(True, "prey-schedule", pure_time, 1, False)]
    prey_schedule_in_dots = [round(eve - 860.9, 2) for eve in extract_dots(False, "prey-schedule", pure_time, 1, False)]

    prey_interaction_ex_dots = [round(eve - 860.9, 2) for eve in extract_dots(True, "prey-interaction", pure_time, 0, False)]
    prey_interaction_in_dots = [round(eve - 860.9, 2) for eve in extract_dots(False, "preY-interaction", pure_time, 0, False)]

    prey_controller_ex_dots = [round(eve - 860.9, 2) for eve in extract_dots(True, "prey-controller", pure_time, 0, False)]
    prey_controller_in_dots = [round(eve - 860.9, 2) for eve in extract_dots(False, "prey-controller", pure_time, 0, False)]




    plt.figure(1)
    plt.xlim([0,5.1])
    plot_square_wave(prey_plan1_ex_dots, 1, "plan1-EXTERNAL", "red", 0, 10, ":")
    plot_square_wave(prey_plan1_in_dots, 2.5, "plan1-INTERNAL", "green", 0, 10, "-")

    plot_square_wave(prey_plan2_ex_dots, 4, "plan2-EXTERNAL", "red", 0, 10, ":")
    plot_square_wave(prey_plan2_in_dots, 5.5, "plan2-INTERNAL", "green", 0, 10, "-")

    plot_square_wave(prey_goal_ex_dots, 7, "goal-EXTERNAL", "red", 0, 10, ":")
    plot_square_wave(prey_goal_in_dots, 8.5, "goal-INTERNAL", "green", 0, 10, "-")

    plot_square_wave(prey_schedule_ex_dots, 10, "schedule-EXTERNAL", "red", 0, 10, ":")
    plot_square_wave(prey_schedule_in_dots, 11.5, "schedule-INTERNAL", "green", 0, 10, "-")

    plot_square_wave(prey_interaction_ex_dots, 13, "interaction-EXTERNAL", "red", 0, 10, ":")
    plot_square_wave(prey_interaction_in_dots, 14.5, "interaction-INTERNAL", "green", 0, 10, "-")

    plot_square_wave(prey_controller_ex_dots, 16, "controller-EXTERNAL", "red", 0, 10, ":")
    plot_square_wave(prey_controller_in_dots, 17.5, "controller-INTERNAL", "green", 0, 10, "-")

    plt.yticks([1, 2.5, 4, 5.5, 7, 8.5, 10, 11.5, 13, 14.5, 16, 17.5],
               ["plan1-Ext", "plan1-Int", "plan2-Ext", "plan2-Int", "goal-Ext", "goal-Int"
                   , "schedule-Ext", "schedule-Int", "interaction-Ext", "interaction-Int", "controller-Ext",
                "controller-Int"])
    # plt.legend()
    plt.xlabel("Simulation time(s)")
    plt.savefig(r"D:\科研项目\paper4\初稿\ANNSIM初稿\manuscript\figure9.eps", format="eps")
    plt.show()
    # times = []
    # for eve_str in res:

