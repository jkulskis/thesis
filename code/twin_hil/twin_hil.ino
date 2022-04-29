#include <Servo.h>
#include <string.h>

enum
{
  TURNTABLE,
  CAR,
  IMU
} device;

enum
{
  CAR_MAIN_MOTOR,
  CAR_STEERING,
} carCommandTypes;

Servo carMotorESC; // signal pin for the ESC.
Servo steeringServo;

int steeringPin = 9;  // steering
int carMotorPin = 10; // main motor for wheels
int serialVal;        // for incoming serial data

// handling commands
String commandString;
char commandBuf[256];
char *commandToken;

char END_CHAR = '\n';

void setup()
{
  // Attach to Pins
  steeringServo.attach(steeringPin);
  carMotorESC.attach(carMotorPin);
  carMotorESC.writeMicroseconds(1000); // send "stop" signal to ESC. Also necessary to arm the ESC.

  Serial.begin(9600);
}

void handleTurntableCommand()
{
  Serial.println("Handling Turntable Command");
}

void handleCarSteeringCommand()
{
  commandToken = strtok(NULL, "_");

  if (commandToken != NULL)
  {
    char *endptr;
    int steeringValue = strtol(commandToken, &endptr, 10);
    if (commandToken == endptr)
      Serial.println("ERROR: Invalid Command Format");
    else if (steeringValue >= 60 && steeringValue <= 120)
    {
      int serialVal = 60;
      steeringServo.write(steeringValue);
      // Serial.print("Wrote {");
      // Serial.print(steeringValue);
      // Serial.println("} to Steering Servo");
    }
    else
      Serial.println("ERROR: Unknown Steering Value");
  }
}

void handleCarMainMotorCommand()
{
  commandToken = strtok(NULL, "_");

  if (commandToken != NULL)
  {
    char *endptr;
    int motorValue = strtol(commandToken, &endptr, 10);
    if (commandToken == endptr)
      Serial.println("ERROR: Invalid Command Format");
    else if (motorValue >= 1500 && motorValue <= 1700)
    {
      carMotorESC.writeMicroseconds(motorValue);
      // Serial.print("Wrote {");
      // Serial.print(motorValue);
      // Serial.println("} to Car Main Motor ESC");
    }
    else
      Serial.println("ERROR: Unknown Motor Value");
  }
}

void handleCarCommand()
{
  // Serial.println("Handling Car Command");
  commandToken = strtok(NULL, "-");

  if (commandToken != NULL)
  {
    char *endptr;
    int carCommandType = strtol(commandToken, &endptr, 10);
    if (commandToken == endptr) {
      Serial.println("ERROR: Invalid Command Format");
    }
    else if (carCommandType == CAR_MAIN_MOTOR)
      handleCarMainMotorCommand();
    else if (carCommandType == CAR_STEERING)
      handleCarSteeringCommand();
    else
      Serial.println("ERROR: Unknown Car Command Type");
  }

  // while (commandToken != NULL)
  // {
  //   Serial.println(commandToken);
  //   commandToken = strtok(NULL, "_");
  // }
}

void handleIMUCommand()
{
  Serial.println("Handling IMU Command");
}

void handleCommand(char *commandString)
{
  // Serial.print("Received: ");
  // Serial.println(commandString);
  commandToken = strtok(commandString, "_");
  if (commandToken != NULL)
  {
    char *endptr;
    int commandDevice = strtol(commandToken, &endptr, 10);
    if (commandToken == endptr)
      Serial.println("ERROR: Invalid Command Format");
    else if (commandDevice == TURNTABLE)
      handleTurntableCommand();
    else if (commandDevice == CAR)
      handleCarCommand();
    else if (commandDevice == IMU)
      handleIMUCommand();
    else
      Serial.println("ERROR: Unknown Device Type");
  }
}

void loop()
{
  if (Serial.available() > 0)
  {
    // read the incoming byte:
    commandString = Serial.readStringUntil(END_CHAR);
    commandString.toCharArray(commandBuf, commandString.length()+1);
    handleCommand(commandBuf);
  }
}
