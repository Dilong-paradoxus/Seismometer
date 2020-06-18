#include "MPU9250.h"
String incomingByte = String(3); // for serial command
String timeString = String(13); // for receiving current time
String settingString = String(3); // for receiving g setting

int led = 13; //led on pin 13

// an MPU9250 object with the MPU-9250 sensor on I2C bus 0 with address 0x68
MPU9250 IMU(Wire,0x68);
int status;

void setup() {
  // serial to display data
  Serial.begin(115200);
  while(!Serial) {}

  // start communication with IMU 
  status = IMU.begin();
  if (status < 0) {
    Serial.println("IMU initialization unsuccessful");
    Serial.println("Check IMU wiring or try cycling power");
    Serial.print("Status: ");
    Serial.println(status);
    while(1) {}
  }
  // setting the accelerometer full scale range to +/-8G 
  IMU.setAccelRange(MPU9250::ACCEL_RANGE_2G);
  // setting the gyroscope full scale range to +/-500 deg/s
  IMU.setGyroRange(MPU9250::GYRO_RANGE_250DPS);
  // setting DLPF bandwidth to 20 Hz
  IMU.setDlpfBandwidth(MPU9250::DLPF_BANDWIDTH_184HZ);
  // setting SRD to 19 for a 50 Hz update rate
  IMU.setSrd(0);
  // setting DLPF bandwidth to 20 Hz
  // enabling the data ready interrupt
  IMU.enableDataReadyInterrupt();
  // attaching the interrupt to microcontroller pin 2
  pinMode(4,INPUT);
  attachInterrupt(4,getIMU,RISING);
}

void loop() {
  // send specific data on request:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.readString();
    //Serial.print(incomingByte);
    if (incomingByte == "TIM") {
      // say what you got:
      Serial.println("ready");
      timeString = Serial.readString();
      Serial.println(timeString);
      }

    else if (incomingByte == "SEN") {
      Serial.print("SEN Teensy 4.0,");
      Serial.print("time ms,");
      Serial.print("acc mss,");
      Serial.print("gyro rad,");
      Serial.print("mag uT,");
      Serial.println("temp C,");
      }

    else if (incomingByte == "SET") {
      // say what you got:
      Serial.println("ready");
      settingString = Serial.readString();
      Serial.print("Acceleration setting: ");
      Serial.println(settingString);
      if (settingString == "02G"){
        IMU.setAccelRange(MPU9250::ACCEL_RANGE_2G);}
      else if (settingString == "04G"){
        IMU.setAccelRange(MPU9250::ACCEL_RANGE_4G);}
      else if (settingString == "08G"){
        IMU.setAccelRange(MPU9250::ACCEL_RANGE_8G);}
      else if (settingString == "16G"){
        IMU.setAccelRange(MPU9250::ACCEL_RANGE_16G);}
      else {
        IMU.setAccelRange(MPU9250::ACCEL_RANGE_2G);
      }
    }

    else if (incomingByte == "BEE") {
      Serial.print("BOOP ");
      Serial.println(millis());
      }
  }

}

void getIMU(){
  unsigned long currentMillis = millis(); // micros() or millis()
  unsigned long currentMicros = micros();
  // read the sensor
  IMU.readSensor();
  // display the data
  Serial.print("DAT ");
  Serial.print(currentMillis);
  Serial.print(",x ");
  Serial.print(IMU.getAccelX_mss(),10);
  Serial.print(",y ");
  Serial.print(IMU.getAccelY_mss(),10);
  Serial.print(",z ");
  Serial.print(IMU.getAccelZ_mss(),10);
  Serial.println(",");
  //Serial.print(IMU.getGyroX_rads(),6);
  //Serial.print(",");
  //Serial.print(IMU.getGyroY_rads(),6);
  //Serial.print(",");
  //Serial.print(IMU.getGyroZ_rads(),6);
  //Serial.print(",");
  //Serial.print(IMU.getMagX_uT(),6);
  //Serial.print(",");
  //Serial.print(IMU.getMagY_uT(),6);
  //Serial.print(",");
  //Serial.print(IMU.getMagZ_uT(),6);
  //Serial.print(",");
  //Serial.println(IMU.getTemperature_C(),6);
}
