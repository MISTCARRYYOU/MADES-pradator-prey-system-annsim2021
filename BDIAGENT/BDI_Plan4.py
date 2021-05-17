from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY
from Message import Message
from BDI_struct_for_cpp import plan2interaction, plan2schedule, Agent4env_content


# evaluate interact with env
# 在评估的过程中与环境交互，不需要存储buffer和other agents policy
# 交互模式就是发送接收，发送接受
class Plan4(AtomicDEVS):
    def __init__(self, agentID):
        AtomicDEVS.__init__(self, "predator-plan4")
        self.outport_schedule = self.addOutPort("outport_schedule")  # 增加端口
        self.inport_schedule = self.addInPort("inport_schedule")  # 增加端口

        self.outport_interaction = self.addOutPort("outport_interaction")  # 增加端口
        self.inport_interaction = self.addInPort("inport_interaction")  # 增加端口

        self.isbegin = False
        self.choose_output = "interaction"  # interaction或者schedule
        self.name = "predator-plan4"
        self.agentID = agentID  # string类

        # 通讯协议
        self.msg = None  # messsage类
        self.message = None  # messsage类
        self.is_need_send = True  # bool
        self.is_need_receive = True  # bool

        self.default_sender = ["any"]  # string array

        # # 初始化结构体参数
        self.plan2interaction = plan2interaction()  #plan2interaction类
        self.plan2schedule = plan2schedule()  # plan2schedule类

        # 其他参数
        self.time_step = 0
        self.is_reset = False
        self.is_reder = True

        self.returns = []
        self.rewards = 0


    def timeAdvance(self):  # ta 要的是返回值
        if self.isbegin:
            return 0
        else:
            return INFINITY

    # 输出
    def outputFnc(self):  # ta 要的是返回值
        if self.choose_output == "interaction":
            return {self.outport_interaction: [self.plan2interaction]}  # plan2interaction类
        elif self.choose_output == "schedule":
            return {self.outport_schedule: [self.plan2schedule]}  # plan2schedule类

    def intTransition(self):  # ta 要的是返回值
        self.isbegin = False
        return self.state

    # 外部事件转移函数
    def extTransition(self, inputs):
        current_port = list(inputs.keys())[0]  # 不会有两个端口同时产生事件的时候

        if current_port == self.inport_schedule:  # 收到调度模块的输入
            self.inputs_schedule = inputs[self.inport_schedule][0]  # schedule2plan类
            assert isinstance(self.inputs_schedule.planID, list) is True

            if self.name in self.inputs_schedule.planID:  # 证明这次发送针对它
                self.isbegin = True
                self.overallparameters = self.inputs_schedule.overall_parameters  # overallparameters类
                # ---------------------------------------------------------------------------------------alter
                self.is_need_send = True
                self.is_need_receive = True
                # ---------------------------------------------------------------------------------------over
            else:
                self.isbegin = False
                return self.state

        elif current_port == self.inport_interaction:  # 收到interaction的输入
            # 接受来自交互模块的内容
            self.inputs_interaction = inputs[self.inport_interaction][0]  # interaction2plan类
            # print(self.name ,self.inputs_interaction.planID)
            if self.name == self.inputs_interaction.planID:  # 证明这次发送针对它
                self.isbegin = True
            else:
                self.isbegin = False
                return self.state
            # 只是直接对调度模块进行反馈的步骤

            if self.inputs_interaction.perception not in ["for send"]:
                # 切片取0是为了给处理并行事件留出接口，在此不需要，所以将列表中元素取出来
                self.perception = self.inputs_interaction.perception[0]  # 结构体env2car
        else:
            raise EOFError

        # 定义部分-------------------------------------------------------
        self.overallparameters.is_evaluate = True

        if self.is_need_send:
            self.is_need_send = False
            # 控制time_step
            self.time_step += 1
            if self.time_step % self.overallparameters.args.evaluate_episode_len == 0:
                self.time_step = 0
                self.is_reset = True
                self.returns.append(self.rewards)
            else:
                self.is_reset = False
            # 控制render
            self.is_reder = True
            # 发送agent选择的actions
            assert self.overallparameters.chosen_actions is not None
            temp_content = Agent4env_content(True, self.overallparameters.chosen_actions, self.is_reset, self.is_reder,
                                             self.overallparameters.agent_id_num, self.overallparameters.agent_policy)

            msg = Message(self.agentID, ["env"], temp_content, "send")
            self.choose_output = "interaction"
            self.plan2interaction.planID = self.name  # string
            self.plan2interaction.message = msg  # message 类
            return self.state

        # receive-1方法
        if self.is_need_receive:
            self.is_need_receive = False
            msg = Message(self.agentID, [None], ["env"], "receive-1")  # 这个地方是用来作区分的地方
            self.choose_output = "interaction"
            self.plan2interaction.planID = self.name  # string
            self.plan2interaction.message = msg
            # 消息内容存储到了self.perception里
            return self.state

        self.overallparameters.s = self.perception.s
        self.overallparameters.r = self.perception.r

        self.rewards += self.perception.r[0]

        # 执行到最后，一定会反馈给调度模块相应的内容
        self.choose_output = "schedule"
        self.plan2schedule.planID = self.name  # string
        self.plan2schedule.overallparameters = self.overallparameters
        return self.state


