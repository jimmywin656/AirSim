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
1. Mannequin - https://www.fab.com/listings/c55ce22b-4f0b-440f-9e9f-f1e7746cc7bf
2. Cars - https://www.fab.com/listings/2909157b-ddfa-4cef-a925-69dc2467021f & https://www.fab.com/listings/591e3b3f-9d49-4cd2-8e28-d471c1a10cab
3. Motorcycle - https://www.fab.com/listings/64f26e0c-f69b-48eb-b0ac-02a611dc1585
4. Airplane - https://www.fab.com/listings/8ee27feb-43c9-4885-b12d-c32a37b76d72 && https://www.fab.com/listings/af50ef35-6046-4854-8e0e-c3eca8230496
5. Bus - https://www.fab.com/listings/0feaaa57-7f8b-442e-b3c6-cce6571c4507
6. Boat - https://www.fab.com/search?q=boat&ui_filter_price=1&is_free=1
7. Stop Sign - https://www.fab.com/listings/d62fe2d0-ef61-4977-af21-38b36fde994a && https://www.fab.com/listings/8fe0c61c-015d-49d5-82be-74fbd79682e5
8. Snowboard - https://www.fab.com/listings/fc058588-812d-4691-a2d8-80cece0fda66
9. Umbrella - https://www.fab.com/listings/b21a5284-c582-41f8-bf17-68ecb4479ff7 && https://www.fab.com/listings/303d5b77-27a5-4a3e-b640-315a0d004a11
10. Sports Balls:
  - basketball - https://www.fab.com/listings/bab7cb14-49ad-4864-919e-432d0616f315
  - volleyball - https://www.fab.com/listings/bf1309e2-2e4e-4038-b829-515a658dae0d
  - football - https://www.fab.com/listings/8acf36b1-1850-4175-81a1-fe3878538b1b
  - soccerball - https://www.fab.com/listings/538e59cf-0dc8-4de2-81ee-553089bb1de5 & https://www.fab.com/listings/8364616b-935a-46fa-ad2c-f85949d15469
11. Baseball Bat - https://www.fab.com/listings/3359cd97-250c-474e-a3a4-892fc58cd7db
12. Bed/Mattress (> Twin Size) - https://www.fab.com/listings/6604b64f-2510-4fbe-a62d-ae91c9b4d2f9
13. Tennis Racket - https://www.fab.com/listings/fc85c31f-0b0e-4b32-8bf0-553e296fa316
14. Suitcase - https://www.fab.com/listings/565176e8-4b55-4a06-a647-20e8b1c27012
15. Skis - https://www.fab.com/listings/cc5d84fd-b0fb-4c40-a837-c46fc3bf8ec9
   
