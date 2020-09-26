# State [Done, Unassigned, Assigned]
from datetime import datetime

class Job:
    def __init__(self, jobId, address, note, state, assignee):
        self.jobId = jobId
        self.address = address
        self.note = note
        self.state = state
        self.assignee = assignee
        self.createdOn = datetime.today()
        self.modifiedOn = datetime.today()

    def set_state(self, state):
        self.state = state
        self.modifiedOn = datetime.today()

    def set_assignee(self, assignee):
        self.assignee = assignee
        self.modifiedOn = datetime.today()

    def toString(self):
        return "Job Id: {} \nAddress: {} \nNote: {} \n".format(self.jobId, self.address, self.note)

    def toStringAdmin(self):
        return "Job Id: {} \nAddress: {} \nNote: {} \nState: {} \nAssignee: {} \n"\
            .format(self.jobId, self.address, self.note, self.state, self.assignee)

    def toRow(self):
        return [self.jobId, self.address, self.note, self.state, self.createdOn, self.modifiedOn, self.assignee]

    @classmethod
    def fromRow(cls, arr):
        if arr[6] == '':
            return cls(int(arr[0]), arr[1], arr[2], arr[3], None)
        else:
            return cls(int(arr[0]), arr[1], arr[2], arr[3], arr[6])
