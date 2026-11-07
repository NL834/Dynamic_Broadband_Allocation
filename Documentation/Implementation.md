# Research 

The main research included defining the problem statement into what you read in the read me. It gives the project a purpose and acts as a foundation for the remainder of the project. I did this by finding reviews online which reinforced the problem I had in mind. It was at this point, I knew it was something worth pursuing.

Instead of going head first intop my own designs, I researched some related topics and what others had done to fix the problem or similar issues.

This includes quality of service (QoS), traffic engineering, human computer interaction (HCI), customer premises equipment (CPE), software defined networking (SDN), fixed bandwidth allocation and application programming interface (API).

To summarise what I learnt from my research:
- QoS - The importance of the users experience in networking
- Traffic Engineering - How traffic actually functions
- HCI - How GUI's are designed and how they function
- CPE - The design of your home router and its features
- SDN - How I was going to develop a program that automates these network configurations
- Fixed bandwidth allocation - Informed me that this has been a problem ever since BT monopolised the internet upon creation

# Designs

The first step of this phase was to develop the project aims, objectives, and requirements.
It converts the identified problem into a straightforward plan of action, outlining what this research aims to accomplish and the specific goals in mind.

## Project Aim

I wanted to develop an MVP capable of showcasing a proof of concept for a networking device to create an on-demand bandwidth provisioning service for home and small business networks and successfully meet the growing demands of modern networks. 

## Goals
- To design, implement and test a self managed, user friendly architecture on a CPE that decouples service provisioning from ISP organisations, putting users in control.
- Address the technical usability and market inertia of the fixed bandwidth model in small business and home networks.
- have the project finished by a specific deadline

## Requirements:

### Functional
- System must separate client and ISP roles
- Must maintain a consistent session
- Allows the user to input a bandwidth amount whenever they desire
- It displays both the clients inactive/active plans
- ISP should be able to view all their clients information
- Showcase active queues and pull router information

### Non-Functional

- Provisioning Latency the system must push the bandwidth policy within a short timeframe. 
- The Flask backend should remember the queues or information
- Credentials must not be stored in plaintext; they must be stored securely using hashing or another encryption method.
- The queue name must sanitise any inputs to prevent command injection.
- A non-technical client should be able to request an upgrade with minimal effort. 
- The system should provide banner messages that serve as acknowledgements
- If the MikroTik is unplugged the script with handle the error and display a router offline message.


## Artefact Design

Now the actual development begins.

Firstly, I wanted to visualise what the network would look like so it would be easier to refer to and I would have a setup in mind.

Please see the image below:

<img width="898" height="343" alt="image" src="https://github.com/user-attachments/assets/505eaf83-8445-4b8b-afec-d945c34a282b" />

This is a network diagram made in Cisco Packet Tracer - a network simulation software.

Here is an explanation of each device:
- The wired device represents the Raspberry PI - acts as the client for the requests
- Router - your home CPE (MikroTik Router)
- PC - My desktop executing the code and acting as the ISP

The desktop would run the code/website and send the clients requests to the 'ISP', this would then be approved and sent to the MikroTik's API via RouterOS. It then executes the new bandwidth queue on the cable associated with the raspberry PI. From this design, we now have a functioning network and product.

The website is coded using flask, as it is low intensive and easy to setup - the perfect software for the average CPE.


To break down this process even more, I developed a flowchart to illustrate the process:

<img width="958" height="810" alt="image" src="https://github.com/user-attachments/assets/3de5873e-b5ab-4adc-8c98-ab2c627216e8" />


I will not go into too much detail on how the whole algorithm works, but a general summary of each step.



