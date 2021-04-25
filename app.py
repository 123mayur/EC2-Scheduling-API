import json
import boto3
from flask import Flask, request
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

schedule_app = Flask(__name__)
schedule_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
scheduler.add_jobstore('sqlalchemy', url='sqlite:////tmp/test.db')
scheduler.start()

@schedule_app.route('/create', methods=['POST'])
def schedule_to_print():
    data = request.get_json()
    s_time = data.get('s_time')
    i_id = data.get('i_id')
    e_time= data.get('e_time')
    s_job=scheduler.add_job(start,CronTrigger.from_crontab(s_time),args=[i_id])
    e_job = scheduler.add_job(stop,CronTrigger.from_crontab(e_time), args=[i_id])
    myjob = [s_job,e_job]
    return json.dumps(myjob)

@schedule_app.route('/getjob', methods=['GET'])
def get_all_job():
    my_job = scheduler.print_jobs(jobstore='sqlalchemy')
    return json.dumps(my_job)

@schedule_app.route('/update/<job_id>', methods=['PATCH'])
def update_schedule():
    data = request.get_json()
    job_id = data.get('job_id')
    s_time = data.get('s_time')
    e_time = data.get('e_time')
    my_job = scheduler.modify_job(job_id=job_id,jobstore='sqlalchemy',s_time=s_time,e_time=e_time)
    return json.dumps(my_job)

@schedule_app.route('/getjob/<job_id>', methods=['GET'])
def get_job(job_id):
    data = request.get_json(job_id)
    job_id = data.get('job_id')
    my_job = scheduler.pause_job(job_id=job_id,jobstore='sqlalchemy')
    return json.dumps(my_job)

@schedule_app.route('/deletejob/<job_id>', methods=['GET'])
def delete_job():
    data = request.get_json()
    job_id = data.get('job_id')
    my_job = scheduler.remove_job(job_id=job_id,jobstore='sqlalchemy')
    return json.dumps(my_job)


def start(i_id):
    instances = [i_id]
    ec2 = boto3.client('ec2')
    ec2.start_instances(InstanceIds=instances)
    ec2.create_tags(Resources=instances, Tags=[{'Key':'Schedule', 'Value':'True'}])
    return json.dumps({"message":"schedule is created"})

def stop(i_id):
    instances = [i_id]
    ec2 = boto3.client('ec2')
    ec2.stop_instances(InstanceIds=instances)
    ec2.delete_tags(Resources=instances, Tags=[{'Key':'Schedule', 'Value':'True'}])
    return json.dumps({"message": "schedule is created"})

if __name__=='__main__':
    schedule_app.run(debug=True)