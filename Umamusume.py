from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject
import multiprocessing as mp
from threading import Thread
import time
from UmamusumeProcess import UmaProcess

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyqtWidget import *


class Umamusume(QObject):
    sendLog = pyqtSignal(str)
    sendLog_Main = pyqtSignal(str, str)
    Error_4080 = pyqtSignal()
    
    def __init__(self, parent: "newTab"=None):
        super().__init__()
        if parent is not None:
            self.parent: "newTab" = parent

        self.TotalResetCount = None
        self.ResetCount = None

        # 커스텀 시그널 정의
        self.sendLog.connect(self.parent.recvLog)
        self.sendLog_Main.connect(self.parent.parent.recvLog_Main)
        self.Error_4080.connect(self.parent.parent.MAC_Address_Change)

    def Receive_Worker(self):
        while True:
            self.Receive()
            time.sleep(0.05)

    def Receive(self): # 통신용
        if self.toParent.empty() == False:
            recv = self.toParent.get()
            # print(recv)
            if recv[0] == "sendLog":
                self.sendLog.emit(str(recv[1]))
                # print(recv[1])
            elif recv[0] == "sendLog_main":
                self.sendLog_Main.emit(str(recv[1]), str(recv[2]))
                # print(recv[1])
            elif recv[0] == "isDoneTutorial":
                self.parent.isDoneTutorialCheckBox.setChecked(recv[1])
                # print(recv[1])

            elif recv[0] == "InstanceComboBox.setEnabled":
                self.parent.InstanceComboBox.setEnabled(recv[1])
                # print(recv[1])
            elif recv[0] == "InstanceRefreshButton.setEnabled":
                self.parent.InstanceRefreshButton.setEnabled(recv[1])
                # print(recv[1])

            elif recv[0] == "startButton.setEnabled":
                self.parent.startButton.setEnabled(recv[1])
                # print(recv[1])
            elif recv[0] == "stopButton.setEnabled":
                self.parent.stopButton.setEnabled(recv[1])
                # print(recv[1])
            elif recv[0] == "resetButton.setEnabled":
                self.parent.resetButton.setEnabled(recv[1])
                # print(recv[1])
            elif recv[0] == "isDoneTutorialCheckBox.setEnabled":
                self.parent.isDoneTutorialCheckBox.setEnabled(recv[1])
                # print(recv[1])

            elif recv[0] == "requestTotalResetCount":
                self.TotalResetCount = None
                TotalResetCount = 0
                for i in self.parent.parent.Tab:
                    if i.stopButton.isEnabled():
                        TotalResetCount += i.umamusume.ResetCount
                self.toChild.put(["sendTotalResetCount", TotalResetCount])
                # print(recv[1])
            elif recv[0] == "sendResetCount":
                self.ResetCount = recv[1]
                # print(recv[1])

            elif recv[0] == "숫자4080_에러_코드":
                self.Error_4080.emit()
                # print(recv[1])
            

    # def TotalResetCountFunction(self):
    #     TotalResetCount = 0
    #     for i in self.parent.parent.Tab:
    #         if i.stopButton.isEnabled(): # 시작된 인스턴스만
    #             i.umamusume.toChild.put(["requestResetCount"])
    #     탈출 = False
    #     while True: # 데이터를 계속 새로 받아옴
    #         for i in self.parent.parent.Tab:
    #             if i.stopButton.isEnabled(): # 시작된 인스턴스만
    #                 print(i.umamusume.ResetCount)
    #                 if not (i.umamusume.ResetCount == -1):
    #                     탈출 = True
    #                     break
    #                 print("무한")
    #                 TotalResetCount += i.umamusume.ResetCount
    #             print("보냈음 ㅇㅇ")
    #             time.sleep(0.5)
    #         if 탈출:
    #             break
    #     self.toChild.put(["sendTotalResetCount", TotalResetCount])
    #     print("받았냐?")

    def start(self):
        # 초기화
        self.toParent = mp.Queue() # 다른 프로세스와의 연결고리 생성
        self.toChild = mp.Queue()

        self.toChild.put(["InstanceName", self.parent.InstanceName])
        self.toChild.put(["InstancePort", self.parent.InstancePort])
        self.toChild.put(["isDoneTutorial", self.parent.isDoneTutorialCheckBox.isChecked()])
        self.toChild.put(["isSSRGacha", self.parent.isSSRGachaCheckBox.isChecked()])
        # self.p = mp.Process(name=str(self.parent.InstancePort), target=self.run_a, args=(self.pipeChild, ), daemon=True)
        self.uma = UmaProcess()
        self.process = mp.Process(name=str(self.parent.InstancePort), target=self.uma.run_a, args=(self.toParent, self.toChild, ), daemon=True)
        # self.pipeParent.send("ㅎㅇ1")
        # self.pipeParent.send("ㅎㅇ2")
        # self.pipeParent.send("ㅎㅇ3")
        self.process.start()

        self.Receiver = Thread(target=self.Receive_Worker, daemon=True)
        self.Receiver.start()
        
    def terminate(self):
        self.toChild.put(["terminate"])
        # pass # not yet