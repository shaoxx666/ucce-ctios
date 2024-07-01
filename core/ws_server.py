from abc import abstractmethod
from asyncio import AbstractEventLoop

import websockets
import asyncio
import json
import json
from websockets.legacy.server import Serve
from cisco import server
from gui.Ui_main import Ui_MainWindow

from core.thread_manager import MyThread

class MyServer:
    def __init__(self, host='0.0.0.0', port=10000):
        self.__host = host  # ip
        self.__port = port  # 端口号
        self.__listCmd = []  # 要发送的信息的列表
        self.__server: Serve = None
        self.__message_value = None  # client返回消息的value
        self.__event_loop: AbstractEventLoop = None
        self.__running = True
        self.__pending = None
        self.isConnect = False

    def __del__(self):
        self.stop_server()

    async def __consumer_handler(self, websocket, path):
        async for message in websocket:
            await self.__consumer(message)

    async def __producer_handler(self, websocket, path):
        print('----------__producer_handler')
        while self.__running:
            await asyncio.sleep(0.000001)
            message = await self.__producer()
            if message:
                await websocket.send(message)
                print('send %s' %(message))
                # util.log('发送 {}'.format(message))

    async def __handler(self, websocket, path):
        isConnect = True
        print("[__handler] websocket连接上:%s"% self.__port)
        
        self.on_connect_handler()
        consumer_task = asyncio.ensure_future(self.__consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(self.__producer_handler(websocket, path))
        done, self.__pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED, )
        for task in self.__pending:
            task.cancel()
            isConnect = False
            try:
                server.get_cisco_instance().AgentLogoff()
                print("websocket连接断开:%s"% self.__port)
            except BaseException as e:
                errmsg = "Error: {}".format(e)
                print(errmsg)

    # 接收处理
    async def __consumer(self, message):
        self.on_revice_handler(message)

    # 发送处理
    async def __producer(self):
        if len(self.__listCmd) > 0:
            return self.__listCmd.pop(0)
        else:
            return None

    @abstractmethod
    def on_revice_handler(self, message):
        pass

    @abstractmethod
    def on_connect_handler(self):
        pass

    # 创建server
    def __connect(self):
        server.get_cisco_instance().appendLog('---server connected--')
        self.__event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__event_loop)
        self.__isExecute = True
        if self.__server:
            print('server already exist')
            return
        self.__server = websockets.serve(self.__handler, self.__host, self.__port)
        asyncio.get_event_loop().run_until_complete(self.__server)
        asyncio.get_event_loop().run_forever()

    # 往要发送的命令列表中，添加命令
    def add_cmd(self, content):
        if not self.__running:
            return
        jsonObj = json.dumps(content)
        self.__listCmd.append(jsonObj)
        print('add_cmd=%s' %(content))
        # util.log('命令 {}'.format(content))
        
    # 开启服务
    def start_server(self):
        MyThread(target=self.__connect).start()

    # 关闭服务
    def stop_server(self):
        self.__running = False
        isConnect = False
        if self.__server is None:
            return
        self.__server.ws_server.close()
        self.__server = None
        try:
            all_tasks = asyncio.all_tasks(self.__event_loop)
            for task in all_tasks:
                # print(task.cancel())
                while not task.cancel():
                    print("无法关闭！")
            self.__event_loop.stop()
            self.__event_loop.close()
        except BaseException as e:
            errmsg = "Error: {}".format(e)
            print(errmsg)
            server.get_cisco_instance().appendLog(errmsg)

class WebServer(MyServer):
    def __init__(self, host='0.0.0.0', port=10000,uimain:Ui_MainWindow=None):
        super().__init__(host, port)
        self.cisco = uimain

    def on_revice_handler(self, message):
        print('[on_revice_handler] message='+message)
        self.ws_rcv_msg(message)
        #self.cserve.AgentLogon()
    
    def on_connect_handler(self):
        content = {'event': 'connectEvent', 'Data': {'cisco_connect':server.get_cisco_instance().isConnect }}
        self.add_cmd(content)
    
    def ws_rcv_msg(self,message):
        try:
            #message = '"'+message+'"'
            #message  = '{"cmd":"ping" , "sequence": "1700918323731"}'
            print('ws_rcv_msg='+message)
            json_info = json.loads(message)
            print(json_info)
            print(json_info['cmd'])
            cmd_ifno = json_info['cmd']
            if cmd_ifno == 'LOG_IN':
                #self.cisco.delete.click()
                server.get_cisco_instance().AgentLogon(json_info['cti'],json_info['ext'])
            elif cmd_ifno == 'LOG_OUT':
                server.get_cisco_instance().AgentLogoff('-1')
            elif cmd_ifno == 'READY':
                server.get_cisco_instance().AgentWork()
            elif cmd_ifno == 'NOT_READY':
                server.get_cisco_instance().AgentAux(str(json_info['code']))
            elif cmd_ifno == 'AFTER_WORK':
                server.get_cisco_instance().AgentWorkingAfterCall('-1')
            elif cmd_ifno == 'MAKE_CALL':
                server.get_cisco_instance().MakeCall(json_info['dest'],json_info['pv_data'],json_info['pv_seq'])
            elif cmd_ifno == 'SEND_DTMF':
                server.get_cisco_instance().SendDTMF(json_info['dtmf_value'])
            elif cmd_ifno == 'ANSWER':
                server.get_cisco_instance().AnswerCall()
            elif cmd_ifno == 'HANGUP_CALL':
                server.get_cisco_instance().HangupCall()
            elif cmd_ifno == 'HOLD':
                server.get_cisco_instance().HoldCall()
            elif cmd_ifno == 'HOLD_CANCEL':
                server.get_cisco_instance().RetrieveCall()
            elif cmd_ifno == 'CONSULT':
                server.get_cisco_instance().BeginTransfer(json_info['dest'],json_info['pv_data'],json_info['pv_seq'])
            elif cmd_ifno == 'CONFERENCE':
                server.get_cisco_instance().BeginCongerence(json_info['dest'],json_info['pv_data'],json_info['pv_seq'])
            elif cmd_ifno == 'CONSULT_CANCEL':
                server.get_cisco_instance().ReconnectCall()
            elif cmd_ifno == 'ALTER_CALL':
                server.get_cisco_instance().AlternateCall()
            elif cmd_ifno == 'CONFERENCE_CALL':
                server.get_cisco_instance().ConferenceCall()
            elif cmd_ifno == 'CONSULT_TRANSFER':
                server.get_cisco_instance().TransferCall()
            elif cmd_ifno == 'TRANSFER_SS':
                server.get_cisco_instance().SingleStepTransferCall(json_info['dest'],json_info['pv_data'],json_info['pv_seq'])
            elif cmd_ifno == 'SET_CURRENT_CALL_DATA':
                server.get_cisco_instance().setCurrentCallData(json_info['pv_data'],json_info['pv_seq'])
            elif cmd_ifno == 'GET_CURRENT_CALL_DATA':
                server.get_cisco_instance().getCurrentCallData(json_info['pv_seq'])

            elif cmd_ifno == 'EnableAgentStatistics':
                server.get_cisco_instance().EnableAgentStatistics()
            elif cmd_ifno == 'EnableSkillStatistics':
                server.get_cisco_instance().EnableSkillStatistics()
            elif cmd_ifno == 'DisableAgentStatistics':
                server.get_cisco_instance().DisableAgentStatistics()
            elif cmd_ifno == 'DisableSkillStatistics':
                server.get_cisco_instance().DisableSkillStatistics()
            
            elif cmd_ifno == 'StartSuperVisorFunction':
                server.get_cisco_instance().StartSuperVisorFunction()
            
            elif cmd_ifno == 'StartMonitorAllTeams':
                server.get_cisco_instance().StartMonitorAllTeams()
            
            elif cmd_ifno == 'StopMonitorAllTeams':
                server.get_cisco_instance().StopMonitorAllTeams()
            
            elif cmd_ifno == 'GetAllAgents':
                server.get_cisco_instance().GetAllAgents()
            
            elif cmd_ifno == 'StartMonitorTeam':
                server.get_cisco_instance().StartMonitorTeam(json_info['teamId'])
            
            elif cmd_ifno == 'StopMonitorTeam':
                server.get_cisco_instance().StopMonitorTeam(json_info['teamId'])
            
            elif cmd_ifno == 'StartMonitorAgent':
                server.get_cisco_instance().StartMonitorAgent(json_info['agent'])
            
            elif cmd_ifno == 'StopMonitorAgent':
                server.get_cisco_instance().StopMonitorAgent()
            
            elif cmd_ifno == 'StopMonitorAgentTeam':
                server.get_cisco_instance().StopMonitorAgentTeam(json_info['teamId'])
            
            elif cmd_ifno == 'StartMonitorAgentTeam':
                server.get_cisco_instance().StartMonitorAgentTeam(json_info['teamId'])
            
            elif cmd_ifno == 'StartMonitorCall':
                server.get_cisco_instance().StartMonitorCall(json_info['callid'])
            
            elif cmd_ifno == 'SuperVisorListenCall':
                server.get_cisco_instance().SuperVisorListenCall()
            
            elif cmd_ifno == 'SuperVisorStopListenCall':
                server.get_cisco_instance().SuperVisorStopListenCall()
            
            elif cmd_ifno == 'SuperVisorBargeInCall':
                server.get_cisco_instance().SuperVisorBargeInCall()
            
            elif cmd_ifno == 'SuperVisorInterceptCall':
                server.get_cisco_instance().SuperVisorInterceptCall()
            
            elif cmd_ifno == 'ForceAgentAvailable':
                server.get_cisco_instance().ForceAgentAvailable()
            
            elif cmd_ifno == 'ForceAgentLogout':
                server.get_cisco_instance().ForceAgentLogout()


            elif cmd_ifno == 403:
                return 'Forbidden'
            elif cmd_ifno == 404:
                return 'Not found'
            elif cmd_ifno=='ping':
                content = {'event': 'pong', 'Data': {}}
                self.add_cmd(content)
            elif cmd_ifno=='RELOAD':
                self.cisco.delete.click()
            else:
                return 'Unknown status code'
        except BaseException as e:
            errmsg = "Error: {}".format(e)
            print(errmsg)
            server.get_cisco_instance().appendLog(errmsg)

__web_instance: MyServer = None

def new_web_instance(host='0.0.0.0', port=10000,uimain:Ui_MainWindow=None) -> MyServer:
    global __web_instance
    if __web_instance is None:
        __web_instance = WebServer(host, port,uimain)
    return __web_instance

def get_web_instance() -> MyServer:
    return __web_instance

class TestServer(MyServer):
    def __init__(self, host='0.0.0.0', port=10000):
        super().__init__(host, port)

    def on_revice_handler(self, message):
        print(message)

    def on_connect_handler(self):
        print("连接上了")

if __name__ == '__main__':
    testServer = TestServer(host='0.0.0.0', port=10000)
    testServer.start_server()