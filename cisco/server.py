from PyQt5.QAxContainer import QAxWidget
from gui.Ui_main import Ui_MainWindow
from core import ws_server
import time

class CiscoServer:
    def __init__(self,mywin:Ui_MainWindow):
        self.__host_main = "30.209.222.14"  # 主用ip
        self.__port_main = "42028"  # 端口号
        self.__host_back = "30.209.223.14"  # 备用ip
        self.__port_back = "42028"  # 端口号
        self.axWidget:QAxWidget = None
        self.myWin = mywin
        self.isConnect = False
        self.isLogin = False
        self.myWin.connect.clicked.connect(self.InitControl)
        self.myWin.checkin.clicked.connect(self.Logon)
        self.myWin.checkout.clicked.connect(self.AgentLogoff)
        self.myWin.ready.clicked.connect(self.AgentWork);
        self.myWin.busy.clicked.connect(self.AgentAux);
        self.myWin.after.clicked.connect(self.AgentWorkingAfterCall);
        self.myWin.answer.clicked.connect(self.AnswerCall);
        self.myWin.handup.clicked.connect(self.HangupCall);

        self.myWin.delete.clicked.connect(self.reloadactive)
        self.myWin.clearlog.clicked.connect(self.cleanLog)
        self.reloadactive()

    def getCiscoConnectStatus(self):
        return self.isConnect 

    def reloadactive(self):
        #self.axWidget.clear()
        if self.myWin.axWidget != None:
            self.myWin.axWidget.deleteLater()
        
        self.myWin.loadActivex()
        self.axWidget = self.myWin.axWidget
        self.InitControl()
        
        #self.axWidget.repaint()

        #self.axWidget.deleteLater()
        #self.axWidget = None
        #self.myWin.loadActivex()
        #self.axWidget.__init__()
    def cleanLog(self):
        self.myWin.log.setPlainText('')

    def Logon(self):
        cti = (self.myWin.lineEdit_cti.text()).strip()
        ext = (self.myWin.lineEdit_ext.text()).strip()
        self.AgentLogon(cti,ext)
        
    def InitControl(self):
        try:
            self.axWidget.dynamicCall("DisposeControl()")
            self.axWidget.dynamicCall("InitControl(const QString&,const QString&,const QString&,const QString&,const QString&,const QString&)",self.__host_main, self.__port_main, self.__host_back, self.__port_back, "d:\\log\\", "7001")
            self.axWidget.OnConnectCtiSuccedEvent.connect(self._OnConnectCtiSuccedEvent)
        
            self.axWidget.OnCallIncomingEvent[str,str,str,str,str,str].connect(self._OnCallIncomingEvent)
            self.axWidget.OnCallConnectEvent[str,str].connect(self._OnCallConnectEvent)
            self.axWidget.OnCallHeldEvent.connect(self._OnCallHeldEvent)
            self.axWidget.OnCallRetrieveEvent[str,str].connect(self._OnCallRetrieveEvent)
            self.axWidget.OnConnectionClearEvent[str,str].connect(self._OnConnectionClearEvent)
            self.axWidget.OnCallEndEvent[str,str].connect(self._OnCallEndEvent)
            self.axWidget.OnCallOutAlertingEvent[str].connect(self._OnCallOutAlertingEvent)
            self.axWidget.OnCallTransferedEvent[str,str,str,str,str,str,str,str].connect(self._OnCallTransferedEvent)
            self.axWidget.OnCallDataChangedEvent[str,str].connect(self._OnCallDataChangedEvent)
            self.axWidget.OnButtonCallEnableEvent[bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool].connect(self._OnButtonCallEnableEvent)

        
            self.axWidget.OnNewAgentOfTeamMemberEvent[str,str,str,str,str,str].connect(self._OnNewAgentOfTeamMemberEvent)
            self.axWidget.OnMonitorAgentStateChangedEvent[str,str,str,str,str].connect(self._OnMonitorAgentStateChangedEvent)


            self.axWidget.OnAgentStateEnableEvent[bool,bool,bool,bool,bool].connect(self._OnAgentStateEnableEvent)
            self.axWidget.OnAgentBaseInfoEvent[str,str,str,bool,bool,bool].connect(self._OnAgentBaseInfoEvent)
            self.axWidget.OnAgentLogonEvent[str].connect(self._OnAgentLogonEvent)
            self.axWidget.OnAgentWorkEvent.connect(self._OnAgentWorkEvent)
            self.axWidget.OnAgentAuxEvent.connect(self._OnAgentAuxEvent)
            self.axWidget.OnAgentLogoffEvent.connect(self._OnAgentLogoffEvent)
            self.axWidget.OnAgentWorkingAfterCallEvent.connect(self._OnAgentWorkingAfterCallEvent)

            self.axWidget.OnCtiOsRequestErrorEvent[int,str].connect(self._OnCtiOsRequestErrorEvent)
            self.axWidget.OnCTIErrorEvent[str].connect(self._OnCTIErrorEvent)
            
            self.axWidget.OnCallConferencedEvent[str,str,str,str,str].connect(self._OnCallConferencedEvent)
            self.axWidget.OnCallInitiatingEvent[str].connect(self._OnCallInitiatingEvent)

        except Exception as ex:
            template = "--ERROR:[InitControl] An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            self.appendLog(message)
   
    # call activex method -agent
    def AgentLogon(self,cti,ext):
        pwd = '123456'
        message = "[AgentLogon] cti= {}  ext= {}".format(cti,ext)
        print(message)
        #self.appendLog(message)

        self.axWidget.dynamicCall("AgentLogon(const QString&, const QString&, const QString&)",str(ext),str(cti),str(pwd)); 
    
    def AgentLogoff(self,reason):
        self.myWin.log.setPlainText('')
        message = "[AgentLogoff] reason= {}".format(str(reason))
        print('---'+message)
        self.appendLog(message)
        #if(self.isLogin):
        self.axWidget.dynamicCall("AgentLogoff(const qint8)",reason);
        self.isLogin = False
        

    def AgentAux(self,reasonCode):
        if reasonCode == None or reasonCode=='' or reasonCode==False:
            reasonCode='999'
        message = "[AgentAux] reasonCode= {}".format(str(reasonCode))
        self.appendLog(message)
        print('-------------AgentAux---------------',str(reasonCode))
        self.axWidget.dynamicCall("AgentAux(const QString&)",str(reasonCode));

    def AgentWork(self):
        message = "[AgentWork]"
        #self.appendLog(message)
        self.axWidget.dynamicCall("AgentWork()");
    
    def AgentWorkingAfterCall(self,reason):
        message = "[AgentWorkingAfterCall] reason= {}".format(reason)
        #self.appendLog(message)
        if reason == None or reason=='' or reason==False:
            reason =-1
        self.axWidget.dynamicCall("AgentWorkingAfterCall(const qint8)", reason);
    
    # call method
    def AnswerCall(self):
        self.axWidget.dynamicCall("AnswerCall()");
    
    def HoldCall(self):
        self.axWidget.dynamicCall("HoldCall()");
    
    def RetrieveCall(self):
        self.axWidget.dynamicCall("RetrieveCall()");
    
    def HangupCall(self):
        self.axWidget.dynamicCall("HangupCall()");
    
    def MakeCall(self,phoneNo, userdata, pos):
        self.axWidget.dynamicCall("MakeCall(const QString&, const QString&, const QString&)",str(phoneNo), str(userdata), str(pos));

    def BeginTransfer(self,phoneNo, userdata, pos):
        self.axWidget.dynamicCall("BeginTransfer(const QString&, const QString&, const QString&)",str(phoneNo), str(userdata), str(pos));

    def BeginCongerence(self,phoneNo, userdata, pos):
        self.axWidget.dynamicCall("BeginCongerence(const QString&, const QString&, const QString&)",str(phoneNo), str(userdata), str(pos));
    
    def TransferCall(self):
        self.axWidget.dynamicCall("TransferCall()");
    
    def ReconnectCall(self):
        self.axWidget.dynamicCall("ReconnectCall()");
    
    def ConferenceCall(self):
        self.axWidget.dynamicCall("ConferenceCall()");
    
    def StartReportAgentFolwWithSS(self,phoneNo, userdata, pos):
        self.axWidget.dynamicCall("StartReportAgentFolwWithSS(const QString&, const QString&, const QString&)",str(phoneNo), str(userdata), str(pos));
    
    def AlternateCall(self):
        self.axWidget.dynamicCall("AlternateCall()");
    
    def SingleStepTransferCall(self,phoneNo, userdata, pos):
        self.axWidget.dynamicCall("SingleStepTransferCall(const QString&, const QString&, const QString&)",str(phoneNo), str(userdata), str(pos));
    
    def setCurrentCallData(self,userdata,pos):
        self.axWidget.dynamicCall("SetCurrentCallData(const QString&, const QString&)",str(userdata), str(pos));

    def getCurrentCallData(self,dataKey):
        self.axWidget.dynamicCall("GetCurrentCallData(const QString&)",str(dataKey));
    
    def SendDTMF(self,phoneNo):
        self.axWidget.dynamicCall("SendDTMF(const QString&)",str(phoneNo));
    
    #班长功能
    def EnableSkillStatistics(self):
        self.axWidget.dynamicCall("EnableSkillStatistics()");
    
    def EnableAgentStatistics(self):
        self.axWidget.dynamicCall("EnableAgentStatistics()");
    
    def DisableAgentStatistics(self):
        self.axWidget.dynamicCall("DisableAgentStatistics()");
    
    def DisableSkillStatistics(self):
        self.axWidget.dynamicCall("DisableSkillStatistics()");
    
    def StartSuperVisorFunction(self):
        self.axWidget.dynamicCall("StartSuperVisorFunction()");
    
    def StartMonitorAllTeams(self):
        self.axWidget.dynamicCall("StartMonitorAllTeams()");
    
    def StopMonitorAllTeams(self):
        self.axWidget.dynamicCall("StopMonitorAllTeams()");
    
    def GetAllAgents(self):
        self.axWidget.dynamicCall("GetAllAgents()");
    
    def StartMonitorTeam(self,teamId):
        self.axWidget.dynamicCall("StartMonitorTeam(const QString&)",str(teamId));
    
    def StopMonitorTeam (self,teamId):
        self.axWidget.dynamicCall("StopMonitorTeam(const QString&)",str(teamId));
    
    def StartMonitorAgent(self,agent):
        self.axWidget.dynamicCall("StartMonitorAgent(const QString&)",str(agent));
    
    def StopMonitorAgent(self):
        self.axWidget.dynamicCall("StopMonitorAgent()");
    
    def StopMonitorAgentTeam(self,teamId):
        self.axWidget.dynamicCall("StopMonitorAgentTeam(const QString&)",str(teamId));
    
    def StartMonitorAgentTeam(self,teamId):
        self.axWidget.dynamicCall("StartMonitorAgentTeam(const QString&)",str(teamId));
    
    def StartMonitorCall(self,callid):
        self.axWidget.dynamicCall("StartMonitorCall(const QString&)",str(callid));
    
    def SuperVisorListenCall(self):
        self.axWidget.dynamicCall("SuperVisorListenCall()");
    
    def SuperVisorStopListenCall(self):
        self.axWidget.dynamicCall("SuperVisorStopListenCall()");
    
    def SuperVisorBargeInCall(self):
        self.axWidget.dynamicCall("SuperVisorBargeInCall()");
    
    def SuperVisorInterceptCall(self):
        self.axWidget.dynamicCall("SuperVisorInterceptCall()");
    
    def ForceAgentAvailable(self):
        self.axWidget.dynamicCall("ForceAgentAvailable()");
    
    def ForceAgentLogout(self):
        self.axWidget.dynamicCall("ForceAgentLogout()");
    

    
    # rcv activex evets 
    def _OnConnectCtiSuccedEvent(self):
        self.myWin.checkin.setDisabled(False)
        self.appendLog("[OnConnectCtiSuccedEvent] receive _OnConnectCtiSuccedEvent event")
        self.myWin.status.setText('连接成功！')
        self.isConnect = True
        content = {'event': 'OnConnectCtiSuccedEvent', 'Data': {}}
        ws_server.get_web_instance().add_cmd(content)
        #self.AgentLogon('69244','123456','69092')
    

    def _OnCallIncomingEvent(self,callid, ani, dnis, uui, skillno, dialnumber):
        print("callid=%s, ani=%s, dnis=%s, uui=%s, skillno=%s, dialnumber=%s" %(callid, ani, dnis, uui, skillno, dialnumber) )
        message = "[OnCallIncomingEvent] callid={}, ani={}, dnis={}".format(callid,ani,dnis)
        self.appendLog(message)
        content = {'event': 'OnCallIncomingEvent', 'Data': {'callid':callid, 'ani':ani, 'dnis':dnis, 'uui':uui, 'skillno':skillno, 'dialnumber':dialnumber}}
        ws_server.get_web_instance().add_cmd(content)
    
    def _OnCallConnectEvent(self,callid, answeringdeviceid):
        print("callid=%s, answeringdeviceid=%s" %(callid, answeringdeviceid))
        content = {'event': 'OnCallConnectEvent', 'Data': {'callid':callid, 'answeringdeviceid':answeringdeviceid}}
        ws_server.get_web_instance().add_cmd(content)
    
    def _OnAgentStateEnableEvent(self, logon, notready, ready, workready, logoff):
        #print("logon=%s, notready=%s, ready=%s, workready=%s, logoff=%s" %(logon, notready, ready, workready, logoff) )
        message = '[OnAgentStateEnableEvent] logon={}, notready={}, ready={}, workready={}, logoff={}'.format(logon, notready, ready, workready, logoff)
        self.myWin.status.setText(message)
        self.myWin.checkin.setDisabled(not logon)
        self.myWin.busy.setDisabled(not notready)
        self.myWin.ready.setDisabled(not ready)
        self.myWin.checkout.setDisabled(not logoff)
        self.myWin.after.setDisabled(not workready)
        self.appendLog(message)
        content = {'event': 'OnAgentStateEnableEvent', 'Data': {'logon':logon, 'notready':notready, 'ready':ready, 'workready':workready, 'logoff':logoff}}
        ws_server.get_web_instance().add_cmd(content)
    
    def _OnAgentWorkEvent(self):
        content = {'event': 'OnAgentWorkEvent', 'Data': {}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnAgentLogonEvent(self, groupid):
        #print("groupid=%s" %(groupid) )
        message = "[OnAgentLogonEvent] groupid={}".format(groupid)
        self.appendLog(message)
        self.myWin.checkout.setDisabled(False)
        
        self.isLogin = True
        content = {'event': 'OnAgentLogonEvent', 'Data': {}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnAgentLogoffEvent(self):
        message = '[OnAgentLogoffEvent] logout success!'
        self.appendLog(message)
        #self.myWin.checkin.setDisabled(False)
        #self.myWin.checkout.setDisabled(True)
        content = {'event': 'OnAgentLogoffEvent', 'Data': {}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnAgentAuxEvent(self):
        message = '[_OnAgentAuxEvent]'
        self.appendLog(message)
        content = {'event': 'OnAgentAuxEvent', 'Data': {}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnAgentWorkingAfterCallEvent(self):
        message = '[_OnAgentWorkingAfterCallEvent]'
        self.appendLog(message)
        content = {'event': 'OnAgentWorkingAfterCallEvent', 'Data': {}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnAgentBaseInfoEvent(self, wrapstring, notreadystring, logoutstring, issupervisor, NotReadyReasonRequired, LogoutReasonRequired):
        #print("wrapstring=%s, notreadystring=%s, logoutstring=%s, issupervisor=%s, NotReadyReasonRequired=%s, LogoutReasonRequired=%s" %(wrapstring, notreadystring, logoutstring, issupervisor, NotReadyReasonRequired, LogoutReasonRequired) )
        message = "[OnAgentBaseInfoEvent] wrapstring={}, notreadystring={}, logoutstring={}, issupervisor={}, NotReadyReasonRequired={}, LogoutReasonRequired={}".format(wrapstring, notreadystring, logoutstring, issupervisor, NotReadyReasonRequired, LogoutReasonRequired)
        self.appendLog(message)
        content = {'event': 'OnAgentWorkingAfterCallEvent', 'Data': {'wrapstring':wrapstring, 'notreadystring':notreadystring, 'logoutstring':logoutstring, 'issupervisor':issupervisor, 'NotReadyReasonRequired':NotReadyReasonRequired, 'LogoutReasonRequired':LogoutReasonRequired}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCallHeldEvent(self,callid, heldingdeviceid):
        message = "[OnCallHeldEvent] callid={}, heldingdeviceid={}".format(callid, heldingdeviceid)
        self.appendLog(message)

        content = {'event': 'OnCallHeldEvent', 'Data': {'callid':callid, 'heldingdeviceid':heldingdeviceid}}
        ws_server.get_web_instance().add_cmd(content)
    
    def _OnCallRetrieveEvent(self,callid, retrievingdeviceid):
        message = "[OnCallRetrieveEvent] callid={}, retrievingdeviceid={}".format(callid, retrievingdeviceid)
        self.appendLog(message)

        content = {'event': 'OnCallRetrieveEvent', 'Data': {'callid':callid, 'retrievingdeviceid':retrievingdeviceid}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnConnectionClearEvent(self,callid, diconnectdevice):
        message = "[_OnConnectionClearEvent] callid={}, diconnectdevice={}".format(callid, diconnectdevice)
        self.appendLog(message)
    
        content = {'event': 'OnConnectionClearEvent', 'Data': {'callid':callid, 'diconnectdevice':diconnectdevice}}
        ws_server.get_web_instance().add_cmd(content)
    
    def _OnCallEndEvent(self, callid, diconnectdevice):
        message = "[_OnCallEndEvent] callid={}, diconnectdevice={}".format(callid, diconnectdevice)
        self.appendLog(message)

        content = {'event': 'OnCallEndEvent', 'Data': {'callid':callid, 'diconnectdevice':diconnectdevice}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCallOutAlertingEvent(self,ucid):
        message = "[_OnCallOutAlertingEvent] ucid={}".format(ucid)
        self.appendLog(message)

        content = {'event': 'OnCallOutAlertingEvent', 'Data': {'ucid':ucid}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCallTransferedEvent(self, olducid, newucid, transfereddevice, transferingdevice, oriani, oridnis,skill,callId):
        message = "[_OnCallTransferedEvent] callId={}".format(callId)
        self.appendLog(message)

        content = {'event': 'OnCallOutAlertingEvent', 'Data': {'olducid':olducid,'newucid':newucid,'transfereddevice':transfereddevice,'transferingdevice':transferingdevice,'oriani':oriani,'oridnis':oridnis,'skill':skill,'callId':callId}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCallDataChangedEvent(self,callid, userdata):
        message = "[_OnCallDataChangedEvent] userdata={}".format(userdata)
        self.appendLog(message)

        content = {'event': 'OnCallDataChangedEvent', 'Data': {'callid':callid,'userdata':userdata}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnButtonCallEnableEvent(self,answerEnable, holdEnable, retrieveEnable, hangupEnable, singleTransferEnable, makeCallEnable, consultTransferEnable, consultConferenceEnable, transferEnable, conferenceEnable, alternateEnable, reconnectEnable, singleConferenceEnable):
        message = '[OnButtonCallEnableEvent] answerEnable={}, holdEnable={}'.format(answerEnable, holdEnable)
        self.appendLog(message)
        self.myWin.answer.setDisabled(not answerEnable)
        self.myWin.handup.setDisabled(not hangupEnable)

        content = {'event': 'OnButtonCallEnableEvent', 'Data': {'answerEnable':answerEnable,'holdEnable':holdEnable,'retrieveEnable':retrieveEnable,'hangupEnable':hangupEnable,'singleTransferEnable':singleTransferEnable,'makeCallEnable':makeCallEnable,'consultTransferEnable':consultTransferEnable,'consultConferenceEnable':consultConferenceEnable,'transferEnable':transferEnable, 'conferenceEnable':conferenceEnable, 'alternateEnable':alternateEnable, 'reconnectEnable':reconnectEnable, 'singleConferenceEnable':singleConferenceEnable}}
        ws_server.get_web_instance().add_cmd(content)
    
    def _OnNewAgentOfTeamMemberEvent(self,agentid, agentlastname, agentstate, agentextension, supervisorid, uniqueobjectid):
        message = "[_OnNewAgentOfTeamMemberEvent] agentid={}".format(agentid)
        self.appendLog(message)

        content = {'event': 'OnNewAgentOfTeamMemberEvent', 'Data': {'agentid':agentid,'agentlastname':agentlastname,'agentstate':agentstate,'agentextension':agentextension,'supervisorid':supervisorid,'uniqueobjectid':uniqueobjectid}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnMonitorAgentStateChangedEvent(self, agentid, groupid, agentstate, agentextension, uniqueobjectid):
        message = "[_OnMonitorAgentStateChangedEvent] agentid={}".format(agentid)
        self.appendLog(message)

        content = {'event': 'OnMonitorAgentStateChangedEvent', 'Data': {'agentid':agentid,'groupid':groupid,'agentstate':agentstate,'agentextension':agentextension,'uniqueobjectid':uniqueobjectid}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCTIErrorEvent(self,errmsg):
        message = "[_OnCTIErrorEvent] errmsg={}".format(errmsg)
        self.appendLog(message)
        content = {'event': 'OnCTIErrorEvent', 'Data': {'errmsg':errmsg}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCtiOsRequestErrorEvent(self,reqcode, errmsg):
        message = "[_OnCtiOsRequestErrorEvent] reqcode={},errmsg={}".format(reqcode,errmsg)
        self.appendLog(message)
        content = {'event': 'OnCtiOsRequestErrorEvent', 'Data': {'reqcode':reqcode, 'errmsg':errmsg}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCallConferencedEvent(self, primarycallid, secondcallid, conferencingdevice, addparty, devicelist):
        message = "[_OnCallConferencedEvent] secondcallid={},primarycallid={}".format(secondcallid,primarycallid)
        self.appendLog(message)

        content = {'event': 'OnCallConferencedEvent', 'Data': {'primarycallid':primarycallid, 'secondcallid':secondcallid, 'conferencingdevice':conferencingdevice, 'addparty':addparty, 'devicelist':devicelist}}
        ws_server.get_web_instance().add_cmd(content)

    def _OnCallInitiatingEvent(self,ucid):
        message = "[_OnCallInitiatingEvent] ucid={}".format(ucid)
        self.appendLog(message)
        content = {'event': 'OnCallInitiatingEvent', 'Data': {'ucid':ucid}}
        ws_server.get_web_instance().add_cmd(content)

    def appendLog(self,message):
        timestr = time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime())
        self.myWin.log.appendPlainText(timestr+message)


__cisco_instance: CiscoServer = None

def new_cisco_instance(mywin:Ui_MainWindow) -> CiscoServer:
    global __cisco_instance
    if __cisco_instance is None:
        __cisco_instance = CiscoServer(mywin)
    return __cisco_instance

def get_cisco_instance() -> CiscoServer:
    return __cisco_instance
    


    
    
    

    
