#!/usr/bin/env python

import sys,os,getopt
import datetime
from azure.monitor import MonitorClient
import requests
import azAuth
import json

# create monitoring client
# Replace this with your subscription id
subscription_id = '09d29343-ed9a-4ad8-baa3-25e147d2d48a'
resource_group_name = 'myResourceGroup'
vm_name = 'MyUbuntuVM'

# not all VM works, need to check why
# subscription_id = raw_input('Enter subscription ID: ')
# resource_group_name = raw_input('Enter resource group name: ')
# vm_name = raw_input('Enter VM name: ')

client = MonitorClient(
    azAuth.getCredentials(),
    subscription_id
)

# register ARM API - Monitoring Contributor Service Role - it is already registered
# resource_client = ResourceManagementClient(
#     credentials,
#     subscription_id# )
# resource_client.providers.register('Microsoft.Insights')

# get today's activity log

def main():
    getTodayActivityLogs()
    getVMMericsDefinition()
    getCPUTotal()

def getTodayActivityLogs():
    today = datetime.datetime.now().date()
    filter = " and ".join([
        "eventTimestamp ge {}".format(today)
    ])
    select = ",".join([
        "eventName",
        "operationName"
    ])

    activity_logs = client.activity_logs.list(
        filter=filter,
        select=select
    )
    for log in activity_logs:
        # assert isinstance(log, azure.monitor.models.EventData)
        print(" ".join([
            log.event_name.localized_value,
            log.operation_name.localized_value,

        ]))

# get metrics
# Get the ARM id of your resource. You might chose to do a "get"
# using the according management or to build the URL directly
# Example for a ARM VM
def getVMMericsDefinition():
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/Microsoft.Compute/virtualMachines/{}"
    ).format(subscription_id, resource_group_name, vm_name)

# You can get the available metrics of this specific resource
    for metric in client.metric_definitions.list(resource_id):
        # azure.monitor.models.MetricDefinition
        print("Available VM Monitor Metrics:")
        print("{}: id={}, unit={}".format(
            metric.name.localized_value,
            metric.name.value,
            metric.unit
        ))

# Get CPU total of yesterday for this VM, by hour
def getCPUTotal():
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)

    filter = " and ".join([
        "name.value eq 'Percentage CPU'",
        "aggregationType eq 'Total'",
        "startTime eq {}".format(yesterday),
        "endTime eq {}".format(today),
        "timeGrain eq duration'PT1H'"
    ])

    metrics_data = client.metrics.list(
        resource_id,
        filter=filter
    )

    for item in metrics_data:
        # azure.monitor.models.Metric
        print("{} ({})".format(item.name.localized_value, item.unit.name))
        for data in item.data:
            # azure.monitor.models.MetricData
            print("{}: {}".format(data.time_stamp, data.total))

main()