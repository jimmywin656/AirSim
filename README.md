# AirSim Setup
## Windows:
### Prerequisites:
- Unreal Engine v4.27.2
- Visual Studio 2022
  - Desktop Development with C++
  - Windows 10 SDK 10.0.19041 or Windows 11 SDK 10.0.26100
  - .NET Framework 4.8.1 SDK

### Steps:
1. Clone the repository:

   ```bash
   git clone https://github.com/Microsoft/AirSim.git
   ```
   and navigate to the AirSim directory: ``` cd AirSim ```
2. Open up Visual Studio 2022 and start the ``` Developer Command Prompt ```
    - Continue without code &rarr; Tools &rarr; Command Line &rarr; Developer Command Prompt
3. Run ``` build.cmd ```. This will create ready to use plugin bits in the ``` Unreal\Plugins ``` folder that can be dropped into any Unreal project.
### Setting up Unreal Engine:
Make sure to close and re-open the Unreal Engine and the Epic Games Launcher before building your first environment if you haven't done so already. 
After restarting, the Epic Games Launcher may ask you to associate project file extensions with Unreal Engine, click on 'fix now' to fix it.

Download an environment created by [Airsim](https://github.com/microsoft/AirSim/releases), or [create one yourself](https://microsoft.github.io/AirSim/unreal_custenv/).
1. Copy and Paste the ``` Plugins ``` folder from ``` AirSim\Unreal ``` into the Environment Project to add AirSim as a plugin

### Setup Detection File:
1. Move modified_detection.py into AirSim/PythonClient/detection
2. Create python virtual environment: ``` python -m venv .venv ``` and run it with ```.venv/Scripts/activate ```
3. Install following dependencies with pip install:
- airsim
- numpy
- msgpack-rpc-python
- backports.weakref
- backports.ssl_match_hostname
- opencv-python

### 3D Models
1. Baseball Bat - https://www.fab.com/listings/3359cd97-250c-474e-a3a4-892fc58cd7db
2. Tennis Racket - https://www.fab.com/listings/fc85c31f-0b0e-4b32-8bf0-553e296fa316
3. Sports Balls:
  - basketball - https://www.fab.com/listings/bab7cb14-49ad-4864-919e-432d0616f315
  - volleyball - https://www.fab.com/listings/bf1309e2-2e4e-4038-b829-515a658dae0d
  - football - https://www.fab.com/listings/8acf36b1-1850-4175-81a1-fe3878538b1b
  - soccerball - https://www.fab.com/listings/538e59cf-0dc8-4de2-81ee-553089bb1de5 & https://www.fab.com/listings/8364616b-935a-46fa-ad2c-f85949d15469
4. Mannequin - https://www.fab.com/listings/c55ce22b-4f0b-440f-9e9f-f1e7746cc7bf
5. Cars - https://www.fab.com/listings/2909157b-ddfa-4cef-a925-69dc2467021f & https://www.fab.com/listings/591e3b3f-9d49-4cd2-8e28-d471c1a10cab
6. Motorcycle - https://www.fab.com/listings/64f26e0c-f69b-48eb-b0ac-02a611dc1585
7. Airplane -
8. Bus -
9. Boat -
10. Stop sign -
11. Snowboard -
12. Umbrella -
13. Bed/Mattress (twin size) -
14. Suitcase -
15. Skis - 
