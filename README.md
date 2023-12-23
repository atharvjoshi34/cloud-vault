# cloud-vault

<b>1. Description</b>

Cloud Vault is file hosting site where you can store any type of file inclduing your photos, vidoes, pdf and many other things. 

<b>2. Architecture diagram</b>  

Cloud Vault is a web application built with Flask and deployed on Google Cloud Platform. It's containerized using Docker, images are stored in artifact registry and hosted on Cloud Run. User data is stored in Cloud SQL for PostgreSQL, while secrets are managed with Secret Manager. Cloud Storage is used for file uploads, and Terraform is employed for infrastructure provisioning. Cloud Vault also verify your identity by email based 2 step multi-factor authentication.

![cv-final drawio-11](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/e0ea34e3-c69d-44b9-8e11-56266e874716)

<b>3. Best Practices</b>

- While using cloud always follow the least privilege principles for service accounts you are using.
- Never use JSON Key file while you are deploying your application on cloud. Rather use IAM based authentication which are far secure than using a JSON key
- Never hardcode any secret vaule directly in your application. Industry practice either insert your secret using environemnt variable through your ci/cd pipeline or use some kind of secret manager (used in our case).
- In cloud vault We are using DB username and password to connect to the database. To safe gaurd the DB username and password cloud vault is using GCP service called <b>Secret Manager</b>.
- You can also use SSL certificate to secure your database and use IAM based authentication.

<b>4. Challenges faced and tips</b>

- To send OTP using your gmail you need to enable two step verfiication for your account then generate the ***APP PASSWORD*** which then you can use to send email. Make sure to use this password carefully
- To create databases, tables in your cloud sql instance you will use tool name PGadmin while making the connection for the first time you might encounter the error ***Request time out*** again and again to solve this go to site [https://whatismyipaddress.com/](https://whatismyipaddress.com/) note your IPv4 address and then go to <b>cloud sql instance edit section -> Connection under connection you will see authorized network add your ip address here </b> by doing this you wont face the timeout issue in pgadmin
- When you will deploy your application on cloud run you might face the issue where your database is not responsding or giving the internal server error thats because cloud sql will block the traffic by default you need to follow the same step as we did above. To test on large audience you can add the ip address 0.0.0.0/0 in the authorized network of cloud sql. <b> Note:- This is not a recommeded practice to allow traffice from all internet to your instance. In production only allow a specific range of ip address from where your traffic would be coming.</b>
- For containerizing your application we have used docker. Make sure you have enabledd <b>Virtualization</b> before installing the docker
- To containerize your application follow the bellow steps:-
  <ol>
    <li>Have a file named <b>Dockerfile</b> present in the root folder of your project.</li>
    <li>Then do cd to your project location and run command <b> docker build -t image_name:tag .</b></li>
    <li>Dont forget to add the <b> .</b> as its telling you the location of your docker file</li>
    <li> Then run the command <b>docker images</b> it will list all the docker images in your system. You will see the column image id copy the id of the image you want to upload to the artifact registry</li>
    <li>Now run the command <b>docker tag SOURCE-IMAGE LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG</b> you can get this path from the artifact registry as well in the console, this image name can same oe either different as your local image</li>
    <li>For the final step you need to run the command <b>docker push LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG</b> this command will push your local image to the artifact registry of the gcp</li>
    </ol>
    
- Another common mistake that happens is while deploying the images the on cloud run make sure you either change the port of cloud run on which your container will be exposed or expose your apllication on the cloud run default port that is 8080 so make sure your container and application must be listening on the port 8080 before deploying the image to the cloud run.
- As cloud run can scale to 0 when there are no request your application can suffer from the cold start while processing the first request that comes. If you want to avoid that you can keep minimum instance as one.

<b>5. Application screenshot</b>

<b>1. Home Page of Cloud Vault<b>

![homepage](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/f8c47ac3-0518-4bf8-8110-72d11c65c7a5)

<b>2. Login<b>

![login](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/28c8b85e-2c5d-403e-88a1-2fb9ff223fa6)

<b>3. Signup</b>

![signup](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/2c7a3596-ea8b-4d0f-8f62-a5061c1fe98a)

<b>4. OTP Verification</b>

![otp](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/a8cf4504-10e2-4b88-9000-5aefed8c5248)

<b>5. User Profile</b>

![user profile](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/dfbd2167-96f3-4c92-b83d-804e395f6104)

























