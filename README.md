# cc-auto-scaling-boto3
Python script using BOTO3 for automating AWS architecture and Auto scaling groups configured with Elastic Load Balancer and Cloud watch alarms.

Steps involved :
1. Create the basic architecture including VPC, Subnets, Internet Gateway, Security Groups, Route Tables, Instance.
2. Create an AMI of the EC2 instance.
3. Auto scaling Group - used for maintaining or scaling a set of EC2 instances. 
4. Launch Configuration - Information needed by the Auto scaling group to launch EC2 instances.
5. Scaling Policies and Alarms - Set of rules for determining when to scale an instance up or down in an auto scaling group.
6. Elastic Load Balancer - To distribute the traffic.
