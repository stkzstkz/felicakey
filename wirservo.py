import wiringpi as wp
import time


class DoorGPIOContoroller(object):
    '''
    ドア制御関係
    【注意】このクラスは使用後かならずdelすること(デコンストラクタでの処理必要)
    '''
    duty = 0

    def __init__(self):
        '''
	Constructor
        '''
        self.servo_pin = 18            # 12番ピンを指定
        wp.wiringPiSetupGpio()    # 上図 pin(BOARD) の番号でピン指定するモード
        wp.pinMode(self.servo_pin, 2)  # 出力ピンとして指定
        wp.pwmSetMode(0)          # 0Vに指定
        wp.pwmSetRange(1024)      # レンジを0～1024に指定
        wp.pwmSetClock(375)       # 後述

    def servo_angle(self, angle):
        duty = int((4.75*angle/90 + 7.25)*(1024/100))  # 角度からデューティ比を求める
        wp.pwmWrite(self.servo_pin, duty)              # デューティ比を変更
        #print(angle)                                   #オートロックデバッグ用
        #print(duty)                                    #オートロックデバッグ用
        return duty

    def open(self):
        try:
            print("opened")
            #time.sleep(0.5)
            #self.servo_angle(0)
            #time.sleep(0.5)
            time.sleep(0.1)
            self.servo_angle(0)
            time.sleep(0.5)
            self.servo_angle(-90)
            time.sleep(0.5)
            self.servo_angle(0)
            time.sleep(0.1)           
        except Exception:
            print(Exception)

    def close(self):
        #try:
        print("closed")
        #time.sleep(0.5)
        #self.servo_angle(90)
        #time.sleep(0.5)
        time.sleep(0.1)
        self.servo_angle(0)
        time.sleep(0.5)
        self.servo_angle(90)
        time.sleep(0.5)
        self.servo_angle(0)
        time.sleep(0.1)
        #except Exception:
            #print(Exception)

    # def isAttached(self):
    #     '''
    #     true: ドアは閉じている
    #     false: ドアは開いている
    #     '''
    #     if wp.input(self.Confirm_pin) == wp.HIGH:
    #         return True
    #     else:
    #         return False

    # wiringpiはcleanup機能を持っていないため，使わない
    #def __del__(self):          # デコンストラクタ
        #print("deleted")  
        #self.Servo.stop()
        #wp.cleanup()
