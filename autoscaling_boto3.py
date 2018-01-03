import boto3
#Create a new VPC
ec2 = boto3.resource('ec2')
vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
print (vpc)

#Create subnet1
##AZ: us-east-1a
subnet1 = vpc.create_subnet(vpc.id, CidrBlock='10.0.0.0/25', AvailabilityZone='us-east-1a')

#Create subnet2
##AZ: us-east-1B
subnet2 = vpc.create_subnet(vpc.id, CidrBlock='10.0.1.0/25', AvailabilityZone='us-east-1b')
	
##Internet Gateway and attach it to our VPC.
internet_gateway = ec2.create_internet_gateway()  
internet_gateway.attach_to_vpc(VpcId=vpc.vpc_id)

##routes for our Internet gateway
route_table = vpc.create_route_table()  

route_ig_ipv4 = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internet_gateway.internet_gateway_id)  

route_table.associate_with_subnet(SubnetId=subnet1.id)  
route_table.associate_with_subnet(SubnetId=subnet2.id) 

##security groups
sg = vpc.create_security_group(GroupName="SecurityGroup_Project", Description="SecurityGroup_Project") 

##Inbound/Outbound rules
ip_ranges = [{  
    'CidrIp': '0.0.0.0/0'
}]

perms = [{  
    'IpProtocol': 'TCP',
    'FromPort': 80,
    'ToPort': 80,
    'IpRanges': ip_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 443,
    'ToPort': 443,
    'IpRanges': ip_ranges
}, {
    'IpProtocol': 'TCP',
    'FromPort': 22,
    'ToPort': 22,
    'IpRanges': ip_ranges
}]


sg.authorize_ingress(IpPermissions=perms)

##Imageid:HVM (SSD)EBS-Backed 64-bit
##Create instances in each subnet ::ATTACH A SG
]
instance = ec2.create_instances(ImageId='ami-55ef662f',MinCount=1,MaxCount=1,
SubnetId=subnet1.id,InstanceType="t2.micro")
print(instance)

##Create image of instance
ec2_client = boto3.client('ec2')
ami_id = ec2_client.create_image(
        InstanceId  = 'i-0bb3fcb4396da630b',
        Name        = 'ami_project',
        Description = 'ami_desc',
        NoReboot    = True
    )
	
##Create LOAD BALANCER


client_elb = boto3.client('elb')


response = client_elb.create_load_balancer(
	Listeners=[
        {
            'Protocol': 'HTTP',
            'LoadBalancerPort': 80,
            'InstancePort': 80,
        },
    ],
    LoadBalancerName='projectelb',
    Subnets=[
        subnet1.id,subnet2.id
    ],
    SecurityGroups=[
        sg.id
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'ELBProject'
        },
    ]
)

response = client_elb.configure_health_check(
    LoadBalancerName='projectelb',
    HealthCheck={
        'Target': 'HTTP:80/png',
        'Interval': 12,
        'Timeout': 10,
        'UnhealthyThreshold': 3,
        'HealthyThreshold': 2
    }
)	

##Launch Configuration
client_as = boto3.client('autoscaling')
response = client_as.create_launch_configuration(
    LaunchConfigurationName='project_lc',
    ImageId='ami-8fcee4e5',
    SecurityGroups=[
        sg.id,
    ],
	#UserData='string',
    InstanceId='i-0bb3fcb4396da630b',
    InstanceType='t2.micro',
    InstanceMonitoring={
        'Enabled': True
    },  
) 

	

##Create auto scaling groups

	response = client_as.create_auto_scaling_group(
    AutoScalingGroupName='project_asg',
    LaunchConfigurationName='project_lc',
    MinSize=2,
    MaxSize=6,
    LoadBalancerNames=[
        'projectelb',
    ],
    HealthCheckType='ELB',
    HealthCheckGracePeriod=300,
	VPCZoneIdentifier='subnet-83dd6ade,subnet-28e79963'
	)
##Autoscaling Policies
	response = client_as.put_scaling_policy(
    AutoScalingGroupName='project_asg',
    PolicyName='HighCPUUtilization',
    AdjustmentType='PercentChangeInCapacity',
	ScalingAdjustment=65,
    Cooldown=60,
	)
    response = client_as.put_scaling_policy(
    AutoScalingGroupName='project_asg',
    PolicyName='LowCPUUtilization',
    AdjustmentType='PercentChangeInCapacity',
	ScalingAdjustment=20,
    Cooldown=60,
	)

#########CLOUDWATCH METRICS#############
client_cw = boto3.client('cloudwatch')
scaledown = client_cw.put_metric_alarm(
    AlarmName='scaledown',
    AlarmDescription='High CPU Utilization',
    ActionsEnabled=True,
    MetricName='CPUUtilization',
    Namespace='ELB',
    Statistic='Average',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-0bb3fcb4396da630b'
        },
    ],
    Period=60,
    Unit='Seconds',
    EvaluationPeriods=1,
    Threshold=65.0,
    ComparisonOperator='GreaterThanOrEqualToThreshold',
)


scaleup = client_cw.put_metric_alarm(
    AlarmName='scaleup',
    AlarmDescription='Low CPU Utilization',
    ActionsEnabled=True,
    MetricName='CPUUtilization',
    Namespace='ELB',
    Statistic='Average',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-0bb3fcb4396da630b'
        }
    ],
    Period=60,
    Unit='Seconds',
    EvaluationPeriods=2,
    Threshold=20.0,
    ComparisonOperator='LessThanThreshold'   
)	


	
## attaches the specified load balancer to the specified Auto Scaling group.	
response = client_as.attach_load_balancers(
    AutoScalingGroupName='project_asg',
    LoadBalancerNames=[
        'projectelb',
    ],
)



