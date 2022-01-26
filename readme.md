# 설치방법
## Linux


    sudo apt-get update
    sudo apt-get upgrade

    sudo apt-get install -y cmake build-essential python3-pip3 libusb-1.0-0-dev python3-numpy git python3-scipy python3-matplotlib libffi-dev python3-pyqtgraph
    sudo apt-get install -y gpsd gpsd-clients
    sudo apt install pkg-config

    cd ~
    sudo git clone git://git.osmocom.org/rtl-sdr.git
    cd rtl-sdr
    sudo mkdir build
    cd build
    sudo cmake ../ -DINSTALL_UDEV_RULES=ON
    sudo make
    sudo make install
    sudo ldconfig
    sudo reboot now

    cd ~
    git clone https://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@github.com/JungyongHan/RTLSDR-FMdB
    cd RTLSDR-FMdb
    pip3 install --upgrade pip
    pip3 install pyrtlsdr
    
    python main.py

    

GPS 포트 확인하는 방법

    dmesg

입력후 USB 관련 로그에서 포트 확인

EX. /dev/ttyACM0

config.ini 파일에서 comport 에서 포트입력



---

## Windows

#### 실행하고 있는 윈도우 계정 이름에 한글이 들어가 있으면 안 됩니다. (새로운 계정 만드는 걸 추천)
#### 직접 설치하는 경우 GPS USB 포트 번호를 config.ini 에 반드시 입력해주어야 합니다.

1. setup 폴더 들어가기.

2. python-3.8.6.exe 설치

3. pywin32-228.win32-py3.8.exe 설치

4. gps-drvier 폴더에서 각자 윈도우 운영체제에 맞는 비트의 드라이버 exe 설치(x86 일 경우 32비트, x64 일 경우 64비트)

5. rtlsdr-driver 폴더에서 start.bat 파일 실행

6. RTL-SDR 을 USB 포트를 통해 컴퓨터에 연결

7. 다운로드 된 zadig.exe 프로그램 실행

8. Options - List All Devices 클릭

9. RTL SDR에 해당하는 포트를 클릭 (통상적으로 Bulk-IN, Interface 가 rtl-sdr 포트) 선택 후 Driver에 RTL2832U가 보인다면 이게 맞습니다.

10. Replace Driver 클릭 후 완료 메시지 뜰때까지 대기. 그리고 프로그램 닫기.

11. libsdr 폴더에 있는 두 librtlsdr.dll, rtlsdr.dll 파일을 c:\windows\system32 폴더에 복사 붙여넣기(관리자 권한 필요)

12. loading-module.bat 실행

13. 장치관리자 실행 후 USB GPS 연결

14. 포트(COM & LPT) 항목에서 USB 직렬 장치(COM*) 찾기(여기서 *은 아무숫자)

15. 해당 항목 오른쪽 클릭후 속성 클릭 - 포트 설정 에서 비트/초가 9600으로 설정되어있다면 높은 확률로 USB GPS장치. 이때 COM*의 숫자 알아두기.

16. 취소 누른 후 장치관리자 닫기.  

17. config.ini 파일 메모장으로 열기

18. comport = COM3부분에서 아까 찾아놓은 숫자를 COM3 형식에 맞게 대입 (COM7이었다면 comport = COM7)

19. start.bat 실행

20. 끝!!
   