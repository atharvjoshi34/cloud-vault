# cloud-vault

<b>1. Description</b>

Cloud Vault is file hosting site where you can store any type of file inclduing your photos, vidoes, pdf and many other things. 

<b>2. Architecture diagram</b>  

Cloud Vault is a web application built with Flask and deployed on Google Cloud Platform. It's containerized using Docker, images are stored in artifact registry and hosted on Cloud Run. User data is stored in Cloud SQL for PostgreSQL, while secrets are managed with Secret Manager. Cloud Storage is used for file uploads, and Terraform is employed for infrastructure provisioning. Cloud Vault also verify your identity by email based 2 step multi-factor authentication.

![cv-final drawio-11](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/e0ea34e3-c69d-44b9-8e11-56266e874716)

<b>3. Best Practices</b>

- While using cloud always follow the least privilege principles for service accounts you are using.
- Never use JSON Key file while you are deploying your application on cloud. Rather use IAM based authentication which are far secure than using a JSON key
- Never hardcode a any secret vaule directly in your application. Industry practice either insert your secret using environemnt variable through your ci/cd pipeline or use some kind of secret manager (used in our case).
- In cloud vault We are using DB username and password to connect to the database. To safe gaurd the DB username and password cloud vault is using GCP service called <b>Secret Manager</b>.
- You can also use SSL certificate to secure your database and use IAM based authentication.

<b>4. Challenges faced and tips</b>

- To send OTP using your gmail you need to enable two step verfiication for your account then generate the ***APP PASSWORD*** which then you can use to send email. Make sure to use this password carefully
- To create databases, tables in your cloud sql instance you will use tool name PGadmin while making the connection for the first time you might encounter the error ***Request time out*** again and again to solve this go to site [https://whatismyipaddress.com/](https://whatismyipaddress.com/) note your IPv4 address and then go to <b>cloud sql instance edit section -> Connection under connection you will see authorized network add your ip address here </b> by doing this you wont face the timeout issue in pgadmin
- When you will deploy your application on cloud run you might face the issue where your database is not responsding or giving the internal server error thats because cloud sql will block the traffic by default you need to follow the same step as we did above. To test on large audience you can add the ip address 0.0.0.0/0 in the authorized network of cloud sql. <b> Note:- This is not a recommeded practice to allow traffice from all internet to your instance. In production only allow a specific range of ip address from where your traffic would be coming.</b>
- 
