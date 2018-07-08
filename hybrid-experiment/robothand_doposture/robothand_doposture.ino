// Jonas Braun, jonas.braun@tum.de
// MSNE Research Internship Hybrid BCI
// 21.03.2018
// This Sketch is used to:
// 0: initialise the robot hand
// 1: receive inputs (0,1,2,3) via serial port from Python
// 2: translate commands to single finger movements and execute them
// initialisation and setup() are copied from 'Open Bionics - FingerLib Example - HandDemo'


#include <FingerLib.h>
#include <math.h>

// uncomment one of the following to select the board
#define ALMOND_BOARD
//#define CHESTNUT_BOARD

// number of controllable fingers (number of motors)
#if defined(ALMOND_BOARD)
#define NUM_FINGERS 5
#define MYSERIAL Serial
#elif defined(CHESTNUT_BOARD)
#define NUM_FINGERS 4
#define MYSERIAL SerialUSB
#else
#error 'No board selected'
#endif

// uncomment one of the following to select which hand is used
//int handFlag = LEFT;
int handFlag = RIGHT;

// initialise Finger class to array
Finger finger[NUM_FINGERS];

char inchar;
int bytein = 0;
int bytein_old = 0;

void setup() {
   // MYSERIAL.print is used to allow compatability between both the Mega (Serial.print) 
  // and the Zero Native Port (SerialUSB.print), and is defined in FingerLib.h
  MYSERIAL.begin(38400);
  MYSERIAL.println("Started");

  // configure all of the finger pins
  pinAssignment();
  MYSERIAL.println("Pins configured");

  // set hand to the open position and wait for it to open
  openHand();
  delay(1500);

}

void loop() 
{
  if (MYSERIAL.available() > 0)
  {
    inchar = MYSERIAL.read();
    bytein =  (int) inchar +1;// - 47;
    MYSERIAL.print("I received: ");
    MYSERIAL.println(inchar);//, DEC);
    if (bytein != bytein_old)
    {
      // if new posture is on bus, execute it
      posture_decoding(bytein-1);     
    }    
  }    
}

// count through all the fingers and set them to open
void openHand(void)
{
  int i;
  for (i = 0; i < NUM_FINGERS; i++)
  {
    finger[i].open();
  }
}

// count through all the fingers and set them to close
void closeHand(void)
{
  int i;
  for (i = 0; i < NUM_FINGERS; i++)
  {
    finger[i].close();
  }
}

void pinch2(void)
{
  finger[0].close();
  finger[1].close();
  finger[2].open();
  finger[3].open();
  finger[4].open();
}

void pinch3(void)
{
  finger[0].close();
  finger[1].close();
  finger[2].close();
  finger[3].open();
  finger[4].open();
}
void showFinger(void)
{
  finger[0].close();
  finger[1].close();
  finger[2].open();
  finger[3].close();
  finger[4].close();
}
void bit_decoding(int bytein)
// initial idea was to have a bit pattern sent like "00111" to encode every single finger
// but it is much easier to just send single chars to the serial port
{
  int i, j;
      for(i=1;i <= NUM_FINGERS; i++)
      {
        j = ((bytein % (int) pow(2,i)) / (int) pow(2,i-1));//floorf
        if (j == 0)
        {
          finger[i].open();
        }
        else
        {
          finger[i].close();
        }
      }
}

void posture_decoding(int bytein)
// self explanatory
{
  if (bytein == 0)
  {
    openHand();
  }
  else if (bytein == 1)
  {
    closeHand();
  }
  else if (bytein == 2)
  {
    pinch2();
  }
  else if (bytein == 3)
  {
    pinch3();
  }
  else if (bytein == 7)
  {
    showFinger();
  }
}



