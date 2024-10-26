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
