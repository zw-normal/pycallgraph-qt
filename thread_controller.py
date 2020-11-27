from function_call_graph import GraphThread
from signal_hub import signalHub


class ThreadController:

    def __init__(self):
        self.func_call_graph_thread = None

    def get_func_call_dot(self, func_id: int):
        if self.func_call_graph_thread:
            self.func_call_graph_thread.resultReady.disconnect()
            self.func_call_graph_thread.stop()
        self.func_call_graph_thread = GraphThread(func_id)
        self.func_call_graph_thread.resultReady.connect(signalHub.getFuncCallDone)
        self.func_call_graph_thread.start()

    def cancel_func_call_dot(self):
        if self.func_call_graph_thread:
            self.func_call_graph_thread.resultReady.disconnect()
            self.func_call_graph_thread.stop()
            self.func_call_graph_thread = None


thread_constroller = ThreadController()
