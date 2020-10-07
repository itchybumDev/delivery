import csv
import pickle
from datetime import datetime

from User import User
from model.Job import Job

user_dict = {}

currentJobs = {}

doneJobs = {}

dev_team = []

idCounter = [-1]

def saveJobs():
    with open("./db/jobs.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for job in currentJobs.values():
            tmp = job.toRow()
            if job.assignee is not None:
                tmp.append(getUser(job.assignee).toString())
            writer.writerow(tmp)
    return True


def saveDoneJobs(job):
    with open("./db/done_jobs.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        tmp = job.toRow()
        if job.assignee is not None:
            tmp.append(getUser(job.assignee).toString())
        writer.writerow(tmp)
    return True


def loadJobs():
    with open("./db/jobs.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            tmp = Job.fromRow(row)
            currentJobs[tmp.jobId] = tmp
            if tmp.jobId >= idCounter[0]:
                idCounter[0] = tmp.jobId + 1
    return True


def createNewJob(address, note):
    tmp = Job(idCounter[0], address, note, 'Unassigned', None)
    currentJobs[tmp.jobId] = tmp
    saveJobs()
    idCounter[0] += 1


def removeJob(id):
    if int(id) in currentJobs.keys():
        del currentJobs[int(id)]
        saveJobs()
        return True
    return False


def markDone(id):
    curr_job = currentJobs[int(id)]
    curr_job.set_state('Done')
    text = "The job has been DONE \n"
    text += curr_job.toStringAdmin()
    if curr_job.assignee is not None:
        text += getUser(curr_job.assignee).toString() + '\n'
    removeJob(id)
    saveDoneJobs(curr_job)
    return text

def markAssigned(id, userId):
    curr_job = currentJobs[int(id)]
    curr_job.set_state('Assigned')
    curr_job.set_assignee(userId)
    saveJobs()


def markUnAssigned(id):
    curr_job = currentJobs[int(id)]
    curr_job.set_state('Unassigned')
    curr_job.set_assignee(None)
    saveJobs()


def log(message):
    print("********************************")
    print("{} : {}".format(datetime.today(), message))
    print("********************************")


def getCurrentJobs():
    return currentJobs


def getUserDict():
    return user_dict


def getDevTeam():
    return dev_team


def addDevTeam(admin):
    dev_team.append(str(admin))
    saveDevTeam()


def loadDevTeam():
    with open("./db/dev_team.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            dev_team.append(str(row[0]))


def saveDevTeam():
    with open("./db/dev_team.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for v in dev_team:
            writer.writerow([v])
    return True


def saveUserDict(filename):
    global user_dict
    with open("./db/" + filename + ".pickle", 'wb') as handle:
        pickle.dump(user_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("./db/userData.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for v in user_dict.values():
            writer.writerow([v.toExcelRow()])
    return True


def loadUserDict(filename):
    global user_dict
    try:
        with open("./db/" + filename + '.pickle', 'rb') as handle:
            user_dict = pickle.load(handle)
    except IOError:
        log("User Dict data is not found, initialize to empty")


def getAllUser():
    result = ""
    for k, v in user_dict.items():
        result += v.toString()
    return result


def getNumberOfUser(chat_id):
    return len(user_dict.keys())


def addUser(chat_id, effective_user):
    if chat_id in user_dict:
        user = user_dict.get(chat_id)
    else:
        user = User(chat_id)
    user.full_name = effective_user.full_name
    user.is_bot = effective_user.is_bot
    user.username = effective_user.username
    user.first_name = effective_user.first_name
    user.last_name = effective_user.last_name
    user_dict.setdefault(chat_id, user)
    print("{} : {}".format(datetime.today(), user.toString()))
    saveUserDict("userData")
    return user


def getUser(chat_id):
    user = user_dict.setdefault(chat_id, User(chat_id))
    return user


def startAdmin():
    log("Loading all App Data")
    loadUserDict("userData")
    loadDevTeam()
    loadJobs()


def stopAdmin():
    log("Saving all App Data")
    saveUserDict("userData")
    saveDevTeam()
    saveJobs()
