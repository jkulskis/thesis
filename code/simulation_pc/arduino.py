import serial
import time
from collections import deque
from typing import List, Deque
from enum import Enum

END_CHAR = "\n"


class Device(Enum):
    turntable = 0
    car = 1
    imu = 2


class ArdCommand:
    def __init__(
        self,
        device_name: str,
        instruction: str,
        ack_timeout: float = 0.0,
    ):
        """

        Args:
            device_name (str): Must be a device defined in the Device class
            instruction (str): Instruction to send over to the device
            ack_timeout (float, optional): Wait for an ack for this amount of time in seconds. If 0, not expecting an ack
        """
        try:
            self.device = Device[device_name.lower()]
        except KeyError:
            raise ValueError(f"Unknown Device: {device_name}")
        self.instruction = instruction
        self.ack_timeout = ack_timeout
        self.ack = None

    def __repr__(self):
        return f"{self.device.value}_{self.instruction}_{1 if self.ack_timeout else 0}{END_CHAR}"


class TurntableCommand(ArdCommand):
    def __init__(
        self,
        direction: int,
        speed: int,
        turn_time: float,
        ack_timeout: float = 0.0,
    ):
        """_summary_

        Args:
            direction (int): 0 for CW, 1 for CCW
            speed (int): PWM value to send, should be in the range [0, 255]
            turn_time (int): Amount of time that we should turn at this speed and direction
            ack_timeout (float, optional): Wait for an ack for this amount of time in seconds. If 0, not expecting an ack
        """
        if speed > 255 or speed < 0:
            raise ValueError(f"Invalid speed value: {speed}. Must be in range [0, 255]")
        super().__init__(
            device_name="turntable",
            instruction=f"{direction}-{speed}-{turn_time}",
            ack_timeout=ack_timeout,
        )

class CarCommand(ArdCommand):
    def __init__(
        self,
        motor_value: int,
        steering: bool = False,
        ack_timeout: float = 0.0,
    ):
        """_summary_

        Args:
            motor_value (int): Value to send to motor on car
            steering (bool): Send to steering servo rather than main motor ESC
            ack_timeout (float, optional): Wait for an ack for this amount of time in seconds. If 0, not expecting an ack
        """
        if steering:
            if motor_value < 60 or motor_value > 120:
                raise ValueError(f"Invalid steering motor value: {motor_value}. Must be in range [60, 120]")
        elif motor_value < 1000 or motor_value > 1700:
            raise ValueError(f"Invalid main motor value: {motor_value}. Must be in range [1000, 1700]")
        self.steering = steering
        self.motor_value = int(motor_value)
        super().__init__(
            device_name="car",
            instruction=f"{0 if not self.steering else 1}-{self.motor_value}",
            ack_timeout=ack_timeout,
        )


class Arduino:
    def __init__(self, port="/dev/ttyACM0", timeout=5, baudrate=9600):
        self.ard = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.commands: Deque[ArdCommand] = deque()
        self.command_history: List[ArdCommand] = []

    def add_command(self, command: ArdCommand):
        self.commands.append(command)

    def send_command(self, command: ArdCommand = None):
        if command is None and not self.commands:
            raise ValueError(
                "Need to pass a command as a param or add a command to the queue"
            )
        # priority to command passed as param, otherwise pop from the command queue
        command_to_send = command if command is not None else self.commands.popleft()
        self.ard.flush()
        self.ard.write(str(command).encode())
        send_time = time.time()
        if command.ack_timeout:  # only expecting ack if we have a timeout > 0
            prev_timeout = self.ard.timeout
            self.ard.timeout = command.ack_timeout
            command.ack = self.ard.read_until(
                expected=END_CHAR
            )  # read until we see the end char or until we timeout
            self.ard.timeout = prev_timeout  # reset back to old timeout rather than command specific ack timeout
        self.command_history.append(command)
    
    def read(self, timeout=0):
        """Read until the end character if timeout is 0, otherwise read until timeout
        """
        if timeout:
            self.ard.timeout = timeout
        return self.ard.read_until(expected=END_CHAR)


if __name__ == "__main__":
    # testing purposes
    print(ArdCommand(device_name="IMU", instruction="dummy-instruction"))
    print(TurntableCommand(direction=0, speed=20, turn_time=2.3))
