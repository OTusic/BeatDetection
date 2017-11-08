#include <SoftwareSerial.h>
#include <Stepper.h>
//the steps of a circle
#define STEPS 100

                  /********** INITIALIZING VARIABLES FOR STEPPER MOTORS **********/
//set steps and the connection with MCU
Stepper stepperL(STEPS, 8, 9, 10, 11);
Stepper stepperR(STEPS, 3, 4, 5, 6);

// constants won't change. They're used here to set pin numbers:
// variables will change:
int steps = 0;
int numpress = 0;


                  /********** INITIALIZING VARIABLES FOR TIME MONITORING **********/
// variable for pin connected to switch
int switchMode = 12;
int switchState = LOW;

// variable for pin connected to the button
int button = 7;
int buttonState = LOW;  // Begins not being pressed

// variables for LEDs
int redLED = 13;
int ledState = LOW;

long startCalibrationTime = 0;
long startPlayingTime = 0;

// Store the current number of page flip
int numFlips = 0;
int numFlipsPlaying = 0;

// Variouos Flags and Indicies
int firstRun = 1;
int numTimesThroughCalibration = 0;
int numTimesThroughPlaying = 0;
int prevButtonState = LOW;

// Store a list of the times to flip
//const size_t NUM_VALS = 10;
//int* flipTimes = malloc(NUM_VALS * sizeof(int));
int numPages = 5;
int flipTimes[4];

// Time when button was pressed (looking to see if held down)
int timeButtonPushed = 0;
int timeButtonReleased = 0;
int timeStart = 0;
int timeEnd = 0;
int timeForCalibration = 0;
// 1 is playing mode, 0 is calibration mode
int mode = 0;


// Variouos Flags and Indicies
int firstRunPlaying = 1;
int startMode = 0;

bool pythonResponse = false;

                  /********** HELPER FUNCTIONS FOR STEPPER MOTORS **********/
// Move the left motor 
void lmotor()
{
  while (steps <= 200){
  // speed of 225 per minute
  stepperL.setSpeed(150);
  stepperL.step(steps);
  steps +=50;
  }
}

// Move the right motor
void rmotor ()
{
  while (steps <= 200){
  // speed of 225 per minute
  stepperR.setSpeed(150);
  stepperR.step(steps);
  steps +=50;
  }
}

// Stop both of the motors
void off()
{
  // speed of zero
  stepperL.setSpeed(0);
  stepperL.step(0);
  delay(2);
  stepperR.setSpeed(0);
  stepperR.step(0);
  delay(2);
}

// Run motor based on value of numpress
void runGivenMotor(int theNumpress){
    steps = 0;
    if (theNumpress == 1) {
      lmotor();
      numpress = 0;
      delay(500);
    }
    else {
      rmotor();
      numpress = 1;
      delay(500);
    }  
}

                              /********** SETUP **********/
void setup()
{
  /***** STEPPER SETUP ****/
  //speed of 0
  stepperL.setSpeed(0);
  stepperL.step(0);
  stepperR.setSpeed(0);
  stepperR.step(0);

  /***** BUTTON/SWITCH SETUP ****/
  // initialize the pushbutton pin as an input
  pinMode(button, INPUT);
  pinMode(switchMode, INPUT);

  pinMode(redLED, OUTPUT);
  
  // initialize serial communications at 9600 bps
  Serial.begin(9600);
}


                              /********** MAIN LOOP **********/
void loop(){
  int buttonState = digitalRead(button);
  // If this button changed states
  if(buttonState != prevButtonState){
    // Button was just pushed
    if(buttonState == HIGH){      
      timeButtonPushed = millis();  
    }
    // Button was just released
    else{
      timeButtonReleased = millis();  
    }
   }

  prevButtonState = buttonState;
  
  // If button has been pushed and released 
  if(timeButtonReleased > timeButtonPushed){
        // If we're in calibration mode
        if(!mode){
            // If button was NOT held
            if((timeButtonReleased - timeButtonPushed) < 600){
              // **** SEND PYTHON BUTTON PRESSED **** 
              Serial.println("turn"); 
              runGivenMotor(numpress);
              delay(400);
            }
            // Button is being held down
            else{
               // **** SEND PYTHON BUTTON HELD **** 
               
    
               // First time through is different, want to STAY in calibration mode, not switch to playing
               if (firstRun){
                firstRun = 0;
                timeStart = millis();
                Serial.println("stay");
               }
               else{
                // Switch modes
                 mode = 1; 
                 Serial.println("done");
               }
            }
         }
         timeButtonPushed = 0;
         timeButtonReleased = 0;
  }
   /*
   // Playing mode (calibration is done)
    if(mode){
      // Approximate time when calibration ended
      if (firstRunPlaying){
        timeEnd = millis();

        // Time it took for calibration to run
        // i.e. expected time to be playing
        timeForCalibration = timeEnd - timeStart;
        firstRunPlaying = 0;
      }

      if (Serial.available()){
        //pythonResponse = Serial.read();
        runGivenMotor(numpress);
        pythonResponse = false;
      }

      
      int currentTime = millis();

      // When still in expected time to listen (5% increased bound)
      if((currentTime - timeEnd) <= (timeForCalibration)*1.05){
        if(pythonResponse){
          digitalWrite(redLED, HIGH);
          delay(200);
        }
      }
 
    } */

  
}
