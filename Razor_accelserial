#include <SparkFunMPU9250-DMP.h> // Include SparkFun MPU-9250-DMP library

MPU9250_DMP imu; // Create an instance of the MPU9250_DMP class

#define INTERRUPT_PIN 4 // MPU-9250 INT pin tied to D4

#define SerialPort SerialUSB

int ledPin = 13; //set pin for led

void setup()
{
    SerialPort.begin(115200); //initialize serial connection
    if (imu.begin() != INV_SUCCESS)
    {
    while (1)
    {
        // Failed to initialize MPU-9250, loop forever
    }
    }
    
    pinMode(INTERRUPT_PIN, INPUT_PULLUP); // Set interrupt as an input w/ pull-up resistor
    
    // Use enableInterrupt() to configure the MPU-9250's 
    // interrupt output as a "data ready" indicator.
    imu.enableInterrupt();

    // The interrupt level can either be active-high or low. Configure as active-low.
    // Options are INT_ACTIVE_LOW or INT_ACTIVE_HIGH
    imu.setIntLevel(INT_ACTIVE_LOW);

    // The interrupt can be set to latch until data is read, or as a 50us pulse.
    // Options are INT_LATCHED or INT_50US_PULSE
    imu.setIntLatched(INT_LATCHED);

    imu.setSensors(INV_XYZ_ACCEL); //enable sensors
    imu.setAccelFSR(2); // 2, 4, 8, or 16g
    imu.setLPF(42); // low pass: 5, 10, 20, 42, 98, or 188Hz
    imu.setSampleRate(200); //set sample rate hz

    pinMode(ledPin, OUTPUT); //set led pin as output

    SerialPort.println("X, Y, Z, Time");
}

void loop ()
{
  while (imu.time <= (6 * 60 * 60 * 1000)){  // while time < 6hrs
    if ( digitalRead(INTERRUPT_PIN) == LOW ) // If MPU-9250 interrupt fires (active-low)
    {
      imu.update(UPDATE_ACCEL); // Update accel
      //digitalWrite(ledPin, HIGH);
      float zdata = imu.calcAccel(imu.az);
      float ydata = imu.calcAccel(imu.ay);
      float xdata = imu.calcAccel(imu.ax);

      SerialPort.print(xdata, 11); //print data to serial
      SerialPort.print(", "); //print comma
      SerialPort.print(ydata, 11); //print data to serial
      SerialPort.print(", "); //print comma
      SerialPort.print(zdata, 11); //print data to serial
      SerialPort.print(", "); //print comma
      SerialPort.print(imu.time);
      SerialPort.println();
    }
    else { 
    //digitalWrite(ledPin, LOW);
    }
  }
  SerialPort.println("reset"); //send reset flag to serial port
  NVIC_SystemReset();          // processor software reset
}
