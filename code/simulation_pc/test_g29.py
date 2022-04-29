import pygame
import math
from arduino import Arduino, CarCommand


class G29:
    def __init__(self):
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        # print(self.joystick.get_name()) #<----detected and correct name
        # control values
        self.steer = 0
        self.throttle = 0
        self.brake = 0
        self.hand_brake = False
        self.reverse = False
        # indices from wheel_config.ini
        self.steer_index = 0
        self.clutch_index = 1
        self.throttle_index = 2
        self.brake_index = 3
        self.handbrake_index = 4
        self.reverse_index = 5
        # custom indices...may be because of windows?
        self.throttle_index = 1

    def parse_values(self):

        numAxes = self.joystick.get_numaxes()
        jsInputs = [float(self.joystick.get_axis(i)) for i in range(numAxes)]
        jsButtons = [
            float(self.joystick.get_button(i))
            for i in range(self.joystick.get_numbuttons())
        ]

        # Custom function to map range of inputs [1, -1] to outputs [0, 1] i.e 1 from inputs means nothing is pressed
        # For the steering, it seems fine as it is
        K1 = 1.0  # 0.55
        # steerCmd = K1 * math.tan(1.1 * jsInputs[self._steer_idx])
        steerCmd = K1 * jsInputs[self.steer_index]

        K2 = 1.6  # 1.6
        throttleCmd = jsInputs[self.throttle_index]
        # throttleCmd = (
        #     K2
        #     + (2.05 * math.log10(-0.7 * jsInputs[self.throttle_index] + 1.4) - 1.2)
        #     / 0.92
        # )
        # if throttleCmd <= 0:
        #     throttleCmd = 0
        # elif throttleCmd > 1:
        #     throttleCmd = 1

        # brakeCmd = (
        #     1.6
        #     + (2.05 * math.log10(-0.7 * jsInputs[self.brake_index] + 1.4) - 1.2) / 0.92
        # )
        brakeCmd = jsInputs[self.brake_index]
        # if brakeCmd <= 0:
        #     brakeCmd = 0
        # elif brakeCmd > 1:
        #     brakeCmd = 1

        self.steer = steerCmd
        self.throttle = throttleCmd
        self.brake = brakeCmd

        self.reverse = bool(jsButtons[self.reverse_index])
        self.hand_brake = bool(jsButtons[self.handbrake_index])

    def __repr__(self):
        return f"Steer: {self.steer}\nThrottle: {self.throttle}\nBrake: {self.brake}\nHand Brake: {self.hand_brake}\nReverse: {self.reverse}"


if __name__ == "__main__":
    pygame.init()
    g29 = G29()
    ard = Arduino(port="COM5")

    import time

    start_time = time.time()
    last_act_time = start_time
    last_print_time = start_time
    last_main_motor_value = -1
    last_steering_value = -1
    while True:
        pygame.event.pump()
        g29.parse_values()
        # print every 2 seconds
        if time.time() - last_act_time > 0.001:
            if (not int(time.time()) % 2) and (int(time.time()) != last_print_time):
                print(f"{g29}\n")
                last_print_time = int(time.time())
                print(last_print_time == int(time.time()))
            if abs((last_main_motor_value - (new_main_motor_value := 1550 + g29.throttle * -150)) / last_main_motor_value) > 0.003:
                car_main_motor_command = CarCommand(
                    motor_value=new_main_motor_value, steering=False
                )
                ard.send_command(car_main_motor_command)
                last_main_motor_value = new_main_motor_value
            if abs((last_steering_value - (new_steering_value := 90 + 30 * g29.steer)) / last_steering_value) > 0.003:
                car_steering_command = CarCommand(
                    motor_value=new_steering_value, steering=True
                )
                ard.send_command(car_steering_command)
                last_steering_value = new_steering_value
            last_act_time = time.time()
        # elif read_data := ard.read(timeout=0.005):
        #     pass
        #     print(read_data)
